import RPi.GPIO as GPIO
import select
from subprocess import Popen, PIPE
import usb.core
import time
import sys
import os
import keyboard as kb
import lcddriver

events = []
should_quit = False

ghci = Popen(["/usr/local/bin/start-ghci.sh"], stdout=PIPE, stderr=PIPE, stdin=PIPE)
ghci.stdin.write(':set prompt ""\n0\n')
time.sleep(1)
ghci.stdout.readline()
#ghci.stdin.write("\n")
ghci.stdout.readline()

lcd = lcddriver.lcd()
lcd.lcd_clear()

GPIO.setmode(GPIO.BCM)

GPIO.setup(17, GPIO.OUT)
GPIO.setup(27, GPIO.OUT)

GPIO.output(17, GPIO.LOW)
GPIO.output(27, GPIO.LOW)

dev = usb.core.find(idVendor=0x04b8, idProduct=0x0202)

def retract(n):
	time.sleep(1)
	GPIO.output(17, GPIO.HIGH)
	GPIO.output(27, GPIO.HIGH)
	time.sleep(1)
	dev.write(1, "\n" * n)
	time.sleep(1)
	GPIO.output(17, GPIO.LOW)
	GPIO.output(27, GPIO.LOW)
	time.sleep(2)

def show_input(i):
	inp = i + " " * (20 * 4 - len(i))
	for r in range(4):
		line = inp[r*20 : (r+1) * 20]
		lcd.lcd_display_string(line, r+1)

if dev is None:
	print "couldn't find the device!"
	sys.exit(1)

reattach = False
if dev.is_kernel_driver_active(0):
	reattach = True
	dev.detach_kernel_driver(0)

head = """
                   _
                  /\\\\________
                    \\\\________
                    /\\\\________
                   /  \\\\________
                  /    \\\\________

           The Haskelltron 2000
          [ use "quit" to quit ]
"""

dev.write(1, head)
dev.write(1, "\n" * 10)

def send(s):
	all = s
	retract(10)

	# print "all =", all

	if all == "quit":
		return True

	dev.write(1, "  > " + all + "\n")
	ghci.stdin.write(all + "\n")
	time.sleep(1)
	#r, w, e = select.select([ghci.stdout], [], [], 1)
	#if ghci.stdout in r:
	l = os.read(ghci.stdout.fileno(), 256)
	dev.write(1, l)
	if len(l) == 256:
		dev.write(1, "... + more")
	dev.write(1, "\n")

	dev.write(1, "\n" * 10)

	return False

# ghci.stdout.readline()

while not should_quit:
	e = kb.read_event()

	if e.name == "enter" and e.event_type == "down":
		show_input("")
		should_quit = send("".join(e for e in kb.get_typed_strings(events)))
		events = []
		if should_quit:
			break
	else:
		events.append(e)
		show_input("".join(e for e in kb.get_typed_strings(events)))

dev.write(1, "\n" * 5)
dev.write(1, chr(27) + chr(105))

if reattach:
	dev.attach_kernel_driver(0)

