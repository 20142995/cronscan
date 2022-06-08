#!/bin/bash

cd /app
mkdir -p /app/logs
nohup python3 run.py >/app/logs/web.log 2>&1 &

/bin/bash