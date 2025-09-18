#!/usr/bin/env bash
set -e
source venv/bin/activate
pm2 start pm2/ecosystem.config.js
pm2 save
