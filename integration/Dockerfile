FROM nginx

COPY nginx-selfsigned.crt /etc/ssl/certs/nginx-selfsigned.crt
COPY nginx-selfsigned.key /etc/ssl/private/nginx-selfsigned.key
COPY nginx.conf /etc/nginx

CMD [ "nginx", "-g", "daemon off;" ]
