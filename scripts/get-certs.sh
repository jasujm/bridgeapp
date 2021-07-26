#!/bin/bash

server_name=$1
if [ ! $server_name ]; then
    echo "Usage: get-certs.sh [server-name]"
    exit
fi

docker-compose exec certbot certbot certonly --webroot -w /var/www/certbot -d $1
docker-compose up -d --force-recreate nginx
