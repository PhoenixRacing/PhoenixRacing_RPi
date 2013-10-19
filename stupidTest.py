import RPi.GPIO as GPIO
#setup the board layout
SPEEDO_PIN = 24
TACH_PIN = 25

GPIO.setmode(GPIO.BOARD)
GPIO.setup(SPEEDO_PIN, GPIO.IN)
GPIO.setup(TACH_PIN, GPIO.IN)

while True:
  if GPIO.input(SPEEDO_PIN):
    print "Found Speedo!"
  if GPIO.input(TACH_PIN):
    print "Found Tach!"