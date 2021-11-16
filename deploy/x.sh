#!/bin/sh

set -u

if [ -z "$YOUR_DOMAIN" ]; then
	echo set YOUR_DOMAIN to something
	exit 123
fi

apt install -y nginx fail2ban certbot python3-certbot-nginx
certbot --nginx -d $YOUR_DOMAIN
certbot renew --dry-run

adduser --force-badname --system --no-create-home --group _sp

cp -v sp.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable sp.service
systemctl start sp.service
systemctl status sp.service

cp -v yourdomain /etc/nginx/sites-available/$YOUR_DOMAIN
sed -i -E \
    "s|yourdomain|${YOUR_DOMAIN}|g" \
    /etc/nginx/sites-available/$YOUR_DOMAIN
cp -v jail.local /etc/fail2ban/
ln -s /etc/nginx/sites-available/$YOUR_DOMAIN /etc/nginx/sites-enabled
rm -f /etc/nginx/sites-enabled/default
