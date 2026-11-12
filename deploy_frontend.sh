#!/bin/bash
set -e

cd /root/innobanks_app
git pull origin main

cd /root/innobanks_app/website/next-app
npm install
npm run build

mkdir -p .next/standalone/.next
cp -r .next/static .next/standalone/.next/
cp -r public .next/standalone/

systemctl restart britishschool-next
systemctl status britishschool-next --no-pager
