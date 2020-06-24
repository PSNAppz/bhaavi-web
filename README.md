# Bhaavi Django App

### Production Installation

## nginx conf `bhaavi.conf`

* Create bhaavi.conf inside `/etc/nginx/sites-available` with below contents:

`server {
    listen 80;
    server_name bhaavi.in;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/ubuntu/bhaavi-web/app.sock;
    }
    location /static/ {
        autoindex on;
        alias /home/ubuntu/bhaavi-web/static/;
    }
}
`
* ln bhaavi.conf `/etc/nginx/sites-enabled`
* `sudo systemctl nginx reload`
