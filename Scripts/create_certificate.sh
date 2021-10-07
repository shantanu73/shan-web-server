export CERT_DOMAIN=""
export CERT_EMAIL=""

export CERT_SERVER="https://acme-v02.api.letsencrypt.org/directory"
export CERT_TOKEN="/etc/letsencrypt/cf-api-token.ini"

certbot certonly --cert-name $CERT_DOMAIN --dns-cloudflare --dns-cloudflare-credentials $CERT_TOKEN --server $CERT_SERVER -d $CERT_DOMAIN -m $CERT_EMAIL
yes | cp -rf /etc/letsencrypt/live/$CERT_DOMAIN/* /opt/shan-web-server/certificates
chown -R shanuser:shanuser /opt/shan-web-server
systemctl daemon-reload
systemctl enable shan.service
systemctl start shan.service

echo "systemctl stop shan.service" >> /etc/letsencrypt/renewal-hooks/post/post_renewal_script.sh
echo "cp -f /etc/letsencrypt/live/$CERT_DOMAIN/fullchain.pem /opt/shan-web-server/certificates/" >> /etc/letsencrypt/renewal-hooks/post/post_renewal_script.sh
echo "cp -f /etc/letsencrypt/live/$CERT_DOMAIN/privkey.pem /opt/shan-web-server/certificates/" >> /etc/letsencrypt/renewal-hooks/post/post_renewal_script.sh
echo "chown -R shanuser:shanuser /opt/shan-web-server" >> /etc/letsencrypt/renewal-hooks/post/post_renewal_script.sh
echo "systemctl daemon-reload" >> /etc/letsencrypt/renewal-hooks/post/post_renewal_script.sh
echo "systemctl start shan.service" >> /etc/letsencrypt/renewal-hooks/post/post_renewal_script.sh
chmod +x /etc/letsencrypt/renewal-hooks/post/post_renewal_script.sh
