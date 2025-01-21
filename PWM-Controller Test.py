import RPi.GPIO as GPIO
import time
import tkinter as tk

# Pin Definitions
IN1 = 24  # GPIO pin 24
IN2 = 23  # GPIO pin 23
ENA = 25  # GPIO pin 25 (PWM)

# Setup GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)

# Setup PWM
pwm = GPIO.PWM(ENA, 1000)  # 1kHz frequency
pwm.start(0)

def motor_forward(speed):
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    pwm.ChangeDutyCycle(speed)

def motor_backward(speed):
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    pwm.ChangeDutyCycle(speed)

def motor_stop():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    pwm.ChangeDutyCycle(0)

try:
    while True:
        motor_forward(75)  # Move forward with 75% speed
        time.sleep(5)
        motor_stop()
        time.sleep(2)
        motor_backward(75)  # Move backward with 75% speed
        time.sleep(5)
        motor_stop()
        time.sleep(2)
except KeyboardInterrupt:
    pass
finally:
    pwm.stop()
    GPIO.cleanup()
    def update_speed(val):
        speed = int(val)
        if speed == 0:
            motor_stop()
        else:
            motor_forward(speed)

    # Create the main window
    root = tk.Tk()
    root.title("Motor Speed Controller")

    # Create a scale (slider) widget
    scale = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, label="Speed", command=update_speed)
    scale.pack()

    # Run the Tkinter event loop
    root.mainloop()