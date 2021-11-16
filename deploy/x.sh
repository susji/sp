#!/bin/sh

set -u

if [ -z "$YOUR_DOMAIN" ]; then
	echo set YOUR_DOMAIN to something
	exit 123
fi

apt install -y nginx fail2ban certbot python3-certbot-nginx

install -v -m 0755 -o root -g root sp /usr/local/bin/sp
install -v -m 0755 -o root -g root -d /var/www/sp
install -v -m 0755 -o root -g root *.js *.html /var/www/sp
install -v -m 0644 -o root -g root sp.service /etc/systemd/system/sp.service

adduser --force-badname --system --no-create-home --group _sp

install -m 0644 -o root -g root yourdomain /etc/nginx/sites-available/$YOUR_DOMAIN

systemctl daemon-reload
systemctl enable sp.service
systemctl start sp.service
systemctl status sp.service


sed -i -E \
    "s|yourdomain|${YOUR_DOMAIN}|g" \
    /etc/nginx/sites-available/$YOUR_DOMAIN
ln -s /etc/nginx/sites-available/$YOUR_DOMAIN /etc/nginx/sites-enabled
rm -f /etc/nginx/sites-enabled/default

certbot --nginx -d $YOUR_DOMAIN
certbot renew --dry-run
