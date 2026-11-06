# Nginx
Open source web server and reverse proxy.

Project Homepage: [Nginx Homepage](https://nginx.org/)
Documentation: [Nginx Docs](https://nginx.org/en/docs/)

---
## Commands
COMMAND | DESCRIPTION
---|---
`sudo nginx -t` | Test the configuration
`sudo nginx -T` | Test and dump the full config
`sudo systemctl reload nginx` | Apply config without dropping connections
`sudo systemctl restart nginx` | Restart
`sudo tail -f /var/log/nginx/error.log` | Follow the error log
`nginx -V 2>&1 \| tr ' ' '\n' \| grep module` | Compiled-in modules

Debian layout: `sites-available/` holds configs, link them into `sites-enabled/` (`sudo ln -s /etc/nginx/sites-available/<SITE> /etc/nginx/sites-enabled/`).

## Basic configuration arguments and examples

Logging and debugging:

```nginx
error_log <file> <loglevel>
    error_log logs/error.log;
    error_log logs/debug.log debug;
    error_log logs/error.log notice;
```

basic listening ports:

```nginx
listen <port> <options>
        listen 80;
        listen 443 ssl;
        http2 on;
        listen 443 quic reuseport;   # HTTP/3
```

header modifications:
```nginx
add_header Alt-Svc 'h3=":443"; ma=86400';   # advertise HTTP/3
add_header Strict-Transport-Security "max-age=63072000" always;

ssl_certificate     cert.pem;
ssl_certificate_key cert.key;

server_name domain1.com *.domain1.com;
root /var/www/html/domain1;
index index.php index.html;
```

location blocks:
```nginx
location / {
    try_files $uri $uri/ /index.php$is_args$args;
}
location ~ \.php$ {
    fastcgi_pass 127.0.0.1:9000;
    fastcgi_index index.php;
    fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
    include fastcgi_params;
}
location ~ /\.ht {
    deny all;
}
location = /favicon.ico {
    log_not_found off;
    access_log off;
}
location ~* \.(css|gif|ico|jpeg|jpg|js|png|svg|webp)$ {
    expires max;
    log_not_found off;
}
```

## Redirect HTTP to HTTPS
```nginx
server {
    listen 80;
    server_name example.com;
    return 301 https://$host$request_uri;
}
```

## Reverse Proxy
### Show Client's real IP
```nginx
server {
    server_name example.com;
    location / {
        proxy_pass http://localhost:4000;
        proxy_set_header Host $host;
        # Show clients real IP behind a proxy
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
### WebSockets
```nginx
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
```

## Useful Snippets
```nginx
client_max_body_size 100M;                 # uploads
gzip on;
gzip_types text/css application/javascript application/json image/svg+xml;
limit_req_zone $binary_remote_addr zone=perip:10m rate=10r/s;   # in http {}
limit_req zone=perip burst=20 nodelay;                          # in location {}
auth_basic "Restricted";
auth_basic_user_file /etc/nginx/.htpasswd;                      # htpasswd -c /etc/nginx/.htpasswd <USER>
```
TLS settings: see [[ssl-security]]. Alternatives: [[traefik]].
