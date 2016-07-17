FROM phusion/baseimage:latest
MAINTAINER vdloo <rickvandeloo@gmail.com>
# WARNING: THIS DOCKERFILE IS INSECURE
# ONLY USE IF YOU KNOW WHAT YOU ARE DOING

RUN rm -f /etc/service/sshd/down
RUN /usr/sbin/enable_insecure_key
RUN apt-get update && apt-get install -y \
    rsync \
    puppet \
    htop
