status=$(pm2 show app | grep status | awk '{print $4}')
if [[ "$status" != "online" ]]; then
  echo "pm2 returned wrong status: $status"
  exit 1
fi