import time
import RPi.GPIO as GPIO

# Test Script zum Ansteuern einer LED

# GPIO Modus setzen
GPIO.setmode(GPIO.BCM)

#GPIO Pins zuweisen
GPIO.setup(18, GPIO.OUT)

# Initialisieren der Variable "LED" mit dem GPIO Pin 18
led_pin = 18

# Schleife zum Blinken der LED
for i in range(0, 10):
    GPIO.output(led_pin, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(led_pin, GPIO.LOW)
    time.sleep(1)
    i += 1