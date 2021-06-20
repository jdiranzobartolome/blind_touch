#File executed by the service wlan0_netup_email.service 
#(BETA)

set -e

Needed since I didnt find a way (beside the retries, which in the service also just in case)
for using PartOf and After (which might be able to turn on the service only after the wlan0 setup has finish). Instead of that I enabled the symlink among them so they start together. This will take care of it. A loop checking
that the IP is up. grep gives back a 1 if does not find matches, a 0 if it does. 

error=1
while [ ${error} -eq 1 ]; do
    ipaddress=$(ifconfig | grep -A 1 ${1} | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*')
    error=$?
done

 writing the email to send into a file
date=$(date)
echo "From: Tu gran amigo Odroid <odroidart@gmail.com>" > mail.txt
echo "To: Mi gran amigo Jorge <jorgediranzo@gmail.com>" >> mail.txt
echo "Subject: Pa darte mi IP mocomono" >> mail.txt
echo "Date: ${date}" >> mail.txt
echo "To: jorgediranzo@gmail.com" >> mail.txt
echo " " >> mail.txt
echo "La IP de mi colica ${1} es ${ipaddress}" >> mail.txt

 sending email
curl --url 'smtps://smtp.gmail.com:465' --ssl-reqd \
  --mail-from 'odroidart@gmail.com' --mail-rcpt 'jorgediranzo@gmail.com' \
  --upload-file mail.txt --user 'odroidart@gmail.com:odroidart_23'

deleting email file
rm mail.txt
