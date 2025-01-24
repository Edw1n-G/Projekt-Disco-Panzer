import pygame

pygame.init()

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

def main():

    # This dict can be left as-is, since pygame will generate a
    # pygame.JOYDEVICEADDED event for every joystick connected
    # at the start of the program.
    
    axes = 0
    ControllerInitialization()

    done = False
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

            for i in range(axes):
                axis = joysticks[1].get_axis(i)

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


if __name__ == "__main__":
    main()
    # If you forget this line, the program will 'hang'
    # on exit if running from IDLE.
    pygame.quit()