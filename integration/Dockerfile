FROM nginx

COPY nginx-selfsigned.crt /etc/ssl/certs/nginx-selfsigned.crt
COPY nginx-selfsigned.key /etc/ssl/private/nginx-selfsigned.key
COPY nginx.conf /etc/nginx
COPY index.html /data/www/

CMD [ "nginx", "-g", "daemon off;" ]
