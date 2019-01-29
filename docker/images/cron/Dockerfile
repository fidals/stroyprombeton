FROM debian:latest

RUN apt-get update && apt-get install -y \
    cron \
    rsyslog

CMD service rsyslog start && service cron start && tail -f /var/log/syslog
