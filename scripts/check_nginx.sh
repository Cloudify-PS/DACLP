if [ -e /var/run/nginx.pid ]
  then
    echo "Nginx is running."
  else
    echo "Nginx is NOT running!"
    exit 1
fi
