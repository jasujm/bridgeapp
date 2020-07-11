#!/bin/bash

trap 'kill $(jobs -p)' EXIT

function process_config {
    envsubst '$server_name' < /etc/nginx/conf.d.in/${1}.conf.in > /etc/nginx/conf.d/${1}.conf
}

function create_configs {
    process_config default
    if [ -d /etc/letsencrypt/live/${server_name} ]; then
        process_config bridgeapp
    else
        rm -f /etc/nginx/conf.d/bridgeapp.conf
    fi
}

while IFS= read -r event ; do
    if grep -qF fullchain.pem <<< $event; then
        echo Certificates created/modified. Reloading configs.
        process_config bridgeapp
        nginx -s reload
    fi
done < <(inotifywait -m -e create -e modify -r /etc/letsencrypt) &

while :; do
    sleep 1d
    nginx -s reload
done &

create_configs
nginx -g 'daemon off;'
