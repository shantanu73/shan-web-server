cd /opt
mkdir authbinddir
cd authbinddir
wget https://s3.amazonaws.com/aaronsilber/public/authbind-2.1.1-0.1.x86_64.rpm
rpm -Uvh https://s3.amazonaws.com/aaronsilber/public/authbind-2.1.1-0.1.x86_64.rpm
touch /etc/authbind/byport/443
chmod 500 /etc/authbind/byport/443