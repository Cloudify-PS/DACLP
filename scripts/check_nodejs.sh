#!/bin/bash
status_line=$(sudo su -c "pm2 show app | grep status")
status=$(echo "$status_line" | awk '{print $4;}')
if [[ "$status" == "online" ]]
  then
    echo "The app is running in pm2."
  else
    echo "pm2 returned wrong status: $status"
    exit 1
fi