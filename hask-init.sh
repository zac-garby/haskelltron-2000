#!/bin/sh
exec  </dev/tty1
exec  >/dev/null
exec 2>/dev/null
exec sudo -u pi python3 /home/pi/test.py
