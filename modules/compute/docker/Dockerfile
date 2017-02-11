FROM phusion/baseimage:latest
MAINTAINER vdloo <rickvandeloo@gmail.com>

RUN rm -f /etc/service/sshd/down
ADD instance_key.pub /tmp/instance_key.pub
RUN cat /tmp/instance_key.pub > /root/.ssh/authorized_keys && rm -f /tmp/instance_key.pub
RUN apt-get update && apt-get install -y \
    rsync \
    puppet \
    htop \
    nodejs \
    build-essential \
    python \
    iputils-ping \
    wget \
    unzip \
    screen \
    git
RUN puppet module install puppetlabs-vcsrepo
RUN puppet module install maestrodev-wget
RUN puppet module install saz-sudo

