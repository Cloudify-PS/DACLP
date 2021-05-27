if [ $# -eq 0 ]; then
    echo "Usage: $0 <percent-of-available-memory> [<keep-allocated-for-secs>]"
    echo "example: $0 0.9 10"
    exit 1
fi

wait=$2
if [ -z $2 ]
  then
    wait=0
fi

if (( $(echo "$1 > 1.0" | bc -l) )); then
  echo "Cannot allocate more than the available memory!"
  exit 1
fi

total=$(awk '/MemTotal/{printf "%d\n", $2;}' < /proc/meminfo)
target_free=$(awk -v percent=$1 '/MemTotal/{printf "%d\n", $2 * (1.0-percent);}' < /proc/meminfo)
available=$(awk '/MemAvailable/{printf "%d\n", $2;}' < /proc/meminfo)

alloc=$((available-target_free))
echo "Allocating $alloc kB"
if (( $(echo " $available <= $target_free" | bc -l) )); then
  echo "MemAvailable is lower"
  exit
fi

cat <( </dev/zero head -c "$alloc"k) <(sleep $wait) | tail
echo "Memory freed"
