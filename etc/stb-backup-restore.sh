#!/bin/env sh

sudo mkdir -p /opt/backup/stroyprombeton/
sudo chown -R `whoami` /opt/

for type in database media static
do
    while true; do
        read -p "Do you wish to download $type [y/n]: " yn
        case $yn in
            [Yy]* ) echo "Downloading $type...";
                    scp root@stroyprombeton.ru:/opt/backup/stroyprombeton/$type.tar.gz /opt/backup/stroyprombeton/$type.tar.gz;
                    mkdir -p /opt/$type/stroyprombeton;
                    tar xvfz /opt/backup/stroyprombeton/$type.tar.gz --directory /opt/$type/stroyprombeton;
                    rm /opt/backup/stroyprombeton/$type.tar.gz
                    break;;
            [Nn]* ) break;;
            * ) echo "Please answer yes or no.";;
        esac
    done
done
