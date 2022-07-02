#!/usr/bin/env bash

# https://www.humankode.com/ssl/create-a-selfsigned-certificate-for-nginx-in-5-minutes/

openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout nginx-selfsigned.key -out nginx-selfsigned.crt
