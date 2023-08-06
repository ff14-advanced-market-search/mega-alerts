#!/bin/bash
while true; do
    echo "wait 30 sec before starting so we dont spam the saddlebag api"
    sleep 30
    python3 mega-alerts.py
done