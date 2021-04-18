#!/bin/bash

trap 'kill $(jobs -p)' EXIT

function process_config {
    envsubst '$server_name' < /etc/nginx/conf.d.in/${1}.conf.in > /etc/nginx/conf.d/${1}.conf
}

while :; do
    sleep 1d
    nginx -s reload
done &

process_config default
if [ -d /etc/letsencrypt/live/${server_name} ]; then
    process_config bridgeapp
else
    rm -f /etc/nginx/conf.d/bridgeapp.conf
fi
nginx -g 'daemon off;'
