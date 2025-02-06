import RPi.GPIO as GPIO
import time
import pygame

#Pygame starten
pygame.init()

# Pin Layout
IN1 = 24  # GPIO pin 24
IN2 = 23  # GPIO pin 23
ENA = 25  # GPIO pin 25 (PWM)

# Setup GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)

# PWM
pwm = GPIO.PWM(ENA, 1000)  # 1kHz frequency
pwm.start(0)

joysticks = {}
global axes
axes = 0

def ControllerInitialization():
    # Initialize joysticks

    for i in range(pygame.joystick.get_count()):
        joy = pygame.joystick.Joystick(i)
        joysticks[joy.get_instance_id()] = joy
        #Wenn mehr als 1 Controller verbundne ist trennen
        if len(joysticks) <= 1:
            joysticks[joy.get_instance_id()] = joy
            print(f"Joystick {joy.get_instance_id()} connected")
        else:
            print(f"Joystick {joy.get_instance_id()} disconnected because another joystick is already connected")
            joy.quit()

    # For each joystick, print details once
    for joystick in joysticks.values():

        # Get the name from the OS for the controller
        name = joystick.get_name()
        print(f"Controller name: {name}")

        #GUID ist eine eindeutige ID für den Controller
        guid = joystick.get_guid()
        print(f"Controller GUID: {guid}")

        # Akku Status
        power_level = joystick.get_power_level()
        print(f"Controller power level: {power_level}")

        # Buttons Anzahl
        buttons = joystick.get_numbuttons()
        print(f"Number of buttons: {buttons}")

        # Achsen Anzahl
        axes = joystick.get_numaxes()
        print(f"Number of axes: {axes}")
        
        if axes < 4:
            raise ValueError("Dieser Controller hat nicht genug Achsen um den Panzer zu Steuern.")

#Motor Ansteuerung
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

def Motor1_Control(power):
    power = round(power * 100,2)
    if power <= -25:
        motor_forward(abs(power))
    elif power >= 25:
        motor_backward(abs(power))
    else:
        motor_stop()

def main():

    # This dict can be left as-is, since pygame will generate a
    # pygame.JOYDEVICEADDED event for every joystick connected
    # at the start of the program.
    
    axes = 0
    smooth_left_stick = 0
    strenght = 0.05
    ControllerInitialization()

    done = False
    try:
        # Loop until the user clicks the close button.
        while not done:
            # Event processing step.
            # Possible joystick events: JOYAXISMOTION, JOYBALLMOTION, JOYBUTTONDOWN,
            # JOYBUTTONUP, JOYHATMOTION, JOYDEVICEADDED, JOYDEVICEREMOVED
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True  # Flag that we are done so we exit this loop.

                if event.type == pygame.JOYBUTTONDOWN:
                    print("Joystick button pressed.")

                if event.type == pygame.JOYBUTTONUP:
                    print("Joystick button released.")

                left_stick = pygame.joystick.Joystick(0).get_axis(1)
                smooth_left_stick = strenght * left_stick + (1-strenght) * smooth_left_stick
                
                Motor1_Control(smooth_left_stick)
                print(f"raw:{left_stick}. smooth:{smooth_left_stick}")

                # Handle hotplugging
                if event.type == pygame.JOYDEVICEADDED:
                    # This event will be generated when the program starts for every
                    # joystick, filling up the list without needing to create them manually.
                    joy = pygame.joystick.Joystick(event.device_index)
                    #Wenn mehr als 1 Controller verbundne ist trennen
                    if len(joysticks) == 0:
                        joysticks[joy.get_instance_id()] = joy
                        print(f"Joystick {joy.get_instance_id()} connected")
                    else:
                        print(f"Joystick {joy.get_instance_id()} disconnected because another joystick is already connected")
                        joy.quit()

                if event.type == pygame.JOYDEVICEREMOVED:
                    if joy in joysticks:
                        del joysticks[event.instance_id]
                    print(f"Joystick {event.instance_id} disconnected")
                    joysticks.clear()         
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

if __name__ == "__main__":
    main()
    # If you forget this line, the program will 'hang'
    # on exit if running from IDLE.
    pygame.quit()
