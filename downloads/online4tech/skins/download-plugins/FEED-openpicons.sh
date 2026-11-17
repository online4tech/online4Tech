#!/bin/bash

left=">>>>"
right="<<<<"
LINE1="---------------------------------------------------------"
LINE2="-------------------------------------------------------------------------------------"

if [ -f /etc/opkg/snp-feed.conf ]; then    
    echo "$LINE1"
    echo "> Removing Openpicons Feed... Please wait"
    echo "$LINE1"
    sleep 2

    rm -f /etc/opkg/snp-feed.conf
    rm -f /etc/opkg/srp-feed.conf
    rm -rf /var/cache/opkg/*
    rm -rf /var/lib/opkg/lists/*

    opkg update

    echo "$LINE1"
    echo "> Openpicons Feed Removed Successfully"
    echo "$LINE1"
    sleep 2
else
    echo "$LINE1"
    echo "> Installing Openpicons Feed... Please wait"
    echo "$LINE1"
    sleep 2

    echo "src/gz snp-feed https://openpicons.com/picons/full-motor-snp/ipk" > /etc/opkg/snp-feed.conf
    echo "src/gz srp-feed https://openpicons.com/picons/full-motor-srp/ipk" > /etc/opkg/srp-feed.conf

    rm -rf /var/cache/opkg/*
    rm -rf /var/lib/opkg/lists/*

    opkg update

    echo "$LINE1"
    echo "> Openpicons Feed Installed Successfully"
    echo "$LINE1"
    sleep 2
fi

exit 0

