firewall-cmd --permanent --zone=public --add-service=https
firewall-cmd --permanent --zone=public --add-port=443/tcp
firewall-cmd --reload