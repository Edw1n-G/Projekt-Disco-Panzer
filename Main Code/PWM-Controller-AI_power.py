import pygame
import RPi.GPIO as GPIO
import time
import threading

# Pin Layout
IN1 = 24  # Motor direction control pin 1
IN2 = 23  # Motor direction control pin 2
ENA = 25  # PWM control pin for motor speed
#hi
# Configuration
DEADZONE = 0.1  # Joystick deadzone to ignore small movements
ACCELERATION_TIME = 0.5  # Time (seconds) to transition speeds smoothly
SPEED_SCALE = [0.4, 1.0]  # Min and Max speed scaling (40% to 100%)

# GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)

# Set up PWM on the motor enable pin
pwm = GPIO.PWM(ENA, 1000)  # PWM frequency set to 1 kHz
pwm.start(0)  # Start with 0% duty cycle

# Initialize Pygame and joystick support
pygame.init()
pygame.joystick.init()

# Joystick connection management
joystick = None
connect_thread = None
stop_thread = False

"""Es gibt eine Funktion für Joystick verbindungen suchen die in einem eigenen Thread läuft.
    Die Funktion wird in einer Schleife ausgeführt und sucht nach einem angeschlossenen Joystick.
    Wenn ein Joystick gefunden wird, wird die Verbindung hergestellt und die Funktion beendet.
    Wenn der Joystick in der main Loop getrennt wird, wird die Funktion in einem Thread neu gestartet und der Motor gestoppt.
    
    Die Funktion set_motor() setzt die Motorrichtung und Geschwindigkeit basierend auf dem Eingabewert der Geschwindigkeit.
    Die Geschwindigkeit wird von den Joystickwerten genommen und hat auserhalb der Deadzone eine Geschwindigkeit von 40% bis 100%. siehe l.130
    Dann wird die Geschwindigkeit vom jetzt wet auf den Zielwert in "ACCELERATION_TIME" beschleunigt indem basieren auf den wert die geschwindigkeit stück für stück ändert. def ramp_speed() l.87"""

def connect_joystick():
    """ Attempt to connect a joystick and restart if disconnected. """
    global joystick, connect_thread, stop_thread
    while not stop_thread:
        pygame.joystick.quit()
        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            print("Controller connected!")
            return  # Exit the function once connected
        else:
            joystick = None
            print("Controller disconnected. Reconnecting...")
        time.sleep(1)  # Wait before retrying

def start_connection_thread():
    global connect_thread, stop_thread
    stop_thread = False
    connect_thread = threading.Thread(target=connect_joystick, daemon=True)
    connect_thread.start()

def set_motor(speed):
    """ Set motor direction and speed based on input speed value. """
    if speed > 0:
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
    elif speed < 0:
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.HIGH)
    else:
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.LOW)
    pwm.ChangeDutyCycle(abs(speed) * 100)  # Scale speed to PWM duty cycle

def stop_motor():
    """ Stop the motor when joystick disconnects. """
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    pwm.ChangeDutyCycle(0)

current_speed = 0  # Store the current motor speed

def ramp_speed(target_speed):
    """ Gradually adjust motor speed to target speed for smooth acceleration/deceleration. """
    global current_speed
    step = (target_speed - current_speed) / (ACCELERATION_TIME * 10)  # Calculate small step size
    for _ in range(int(ACCELERATION_TIME * 10)):
        current_speed += step
        set_motor(current_speed)
        time.sleep(0.1)  # Small delay for smooth transition
    set_motor(target_speed)
    current_speed = target_speed  # Ensure final target speed is reached

def main():
    """ Main loop for handling controller input and updating motor speed. """
    global current_speed
    screen = pygame.display.set_mode((400, 200))  # Set up UI window
    pygame.display.set_caption("Motor Control UI")
    font = pygame.font.Font(None, 36)
    
    start_connection_thread()  # Start connection thread at the beginning
    
    running = True
    while running:
        screen.fill((0, 0, 0))  # Clear the screen
        pygame.event.pump()  # Process events
        
        # If no joystick is connected, stop motor and restart connection thread
        if joystick is None:
            stop_motor()
            text = font.render("Controller Disconnected", True, (255, 0, 0))
            screen.blit(text, (50, 80))
            pygame.display.flip()
            time.sleep(0.5)
            start_connection_thread()  # Restart connection attempt if needed
            continue
        
        # Read joystick Y-axis value (-1 to 1)
        pygame.joystick.init()
        axis_y = joystick.get_axis(1)
        
        # Apply deadzone logic
        if abs(axis_y) < DEADZONE:
            target_speed = 0
        else:
            # Normalize joystick value and scale speed
            normalized = (abs(axis_y) - DEADZONE) / (1 - DEADZONE)
            target_speed = (SPEED_SCALE[0] + normalized * (SPEED_SCALE[1] - SPEED_SCALE[0])) * (-1 if axis_y < 0 else 1)
        
        # Start speed transition in a separate thread
        threading.Thread(target=ramp_speed, args=(target_speed,), daemon=True).start()
        
        # Display Info on UI
        speed_text = font.render(f"Motor Speed: {current_speed:.2f}", True, (255, 255, 255))
        axis_text = font.render(f"Joystick Y: {axis_y:.2f}", True, (255, 255, 255))
        screen.blit(speed_text, (50, 50))
        screen.blit(axis_text, (50, 100))
        pygame.display.flip()
        
        time.sleep(0.1)  # Small delay for loop
    
    # Cleanup on exit
    global stop_thread
    stop_thread = True  # Stop the connection thread
    pygame.quit()
    pwm.stop()
    GPIO.cleanup()

# Run the main function when the script is executed
if __name__ == "__main__":
    main()
