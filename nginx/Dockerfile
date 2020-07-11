FROM nginx

RUN set -ex;         \
    apt-get update;  \
    apt-get install -y inotify-tools

COPY start.sh /usr/bin

ENTRYPOINT ["start.sh"]
