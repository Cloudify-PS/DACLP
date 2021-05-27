#!/bin/bash
suffix=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 6 | head -n 1)
ctx instance runtime-properties suffix ${suffix}
