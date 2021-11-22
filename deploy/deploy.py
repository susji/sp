#!/usr/bin/env python3

import os

from pyinfra import host
from pyinfra.operations import apt, server, files, systemd

SUDO = True

if not host.data.SP_DOMAIN:
    raise RuntimeError("Define SP_DOMAIN")
if not host.data.FRONTEND_PATH:
    raise RuntimeError("Define FRONTEND_PATH")
if not host.data.BACKEND_ENDPOINT_SUBMIT:
    raise RuntimeError("Define BACKEND_ENDPOINT_SUBMIT")
if not host.data.FRONTEND_DIR:
    host.data.FRONTEND_DIR = "/var/www/sp"

DOM = host.data.SP_DOMAIN

apt.packages(name="Ensure all relevant apt packages",
             packages=["nginx", "certbot", "python3-certbot-nginx"])

server.user("_sp",
            shell="/usr/sbin/nologin",
            group="_sp",
            system=True,
            ensure_home=False)

files.directory(name="Ensure frontend directory is present",
                path="/var/www/sp",
                user="root",
                group="root",
                mode=755,
                recursive=True)

systemd.service(name="Ensure sp is stopped when updating binary",
                service="sp.service",
                running=False)

files.put(name="Upload daemon binary",
          src="../backend/sp",
          dest="/usr/local/bin/sp",
          user="root",
          group="root",
          mode=755)

files.put(name="Upload systemd unit file",
          src="sp.service",
          dest="/etc/systemd/system/sp.service",
          user="root",
          group="root")

frontend_files = ("fetch.html", "submit.html", "sp.js", "style.css")
for ff in frontend_files:
    src = os.path.join("../frontend/", ff)
    dest = os.path.join(host.data.FRONTEND_DIR, ff)
    files.put(name=f"Upload frontend file: {src} -> {dest}",
              src=src,
              dest=dest,
              user="root",
              group="root",
              mode=644)

files.template(name="Upload templatized frontend configuration",
               src="config.js.j2",
               dest="/var/www/sp/config.js",
               user="root",
               group="root",
               mode=644)

files.template(name="Upload templatized backend configuration",
               src="sp.conf.j2",
               dest="/etc/sp.conf",
               user="root",
               group="root",
               mode=644)

systemd.daemon_reload()

systemd.service(name="Ensure sp service is enabled and running",
                service="sp.service",
                enabled=True,
                running=True,
                restarted=True)

files.template(name=f"NGINX configuration for {DOM}",
               src="nginx.j2",
               dest=f"/etc/nginx/sites-available/{DOM}",
               user="root",
               group="root")

files.link(name=f"Enable nginx site for {DOM}",
           present=True,
           path=f"/etc/nginx/sites-enabled/{DOM}",
           target=f"/etc/nginx/sites-available/{DOM}")

server.shell(
    name=f"Make sure certbot is enabled for {DOM}",
    commands=[f"certbot --non-interactive --nginx -d {DOM}", "nginx -t"])

systemd.service(name="Ensure nginx is cycled",
                service="nginx.service",
                enabled=True,
                running=True,
                restarted=True)
