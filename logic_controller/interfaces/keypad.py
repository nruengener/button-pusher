import time
from pad4pi import rpi_gpio

KEYPAD = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
    ["*", 0, "#"]
]

# ROW_PINS = [4, 14, 15, 17]  # BCM numbering
# COL_PINS = [18, 27, 22]  # BCM numbering
ROW_PINS = [2, 3, 4, 15]  # BCM numbering
COL_PINS = [17, 27, 22]  # BCM numbering


class KeyPad:
    """Class for reading keypad inputs """
    def __init__(self, timeout=5):
        self.timeout = timeout
        self.input = ""
        self.accepting = False
        self.last_time = 0
        factory = rpi_gpio.KeypadFactory()
        self.keypad = factory.create_keypad(keypad=KEYPAD, row_pins=ROW_PINS, col_pins=COL_PINS)
        # printKey will be called each time a keypad button is pressed
        self.keypad.registerKeyPressHandler(self.key_pressed)

    def key_pressed(self, key):
        # print("key: ", key)
        try:
            # reset input if no button pressed for 5 sec
            current_time = time.time()
            if current_time - self.last_time > self.timeout:
                self.input = ""

            self.last_time = current_time

            # reset input if '*' pressed
            if key == '*':
                self.input = ""
                return

            int_key = int(key)
            if self.accepting and 0 <= int_key <= 9:
                self.input = self.input + str(key)
                if len(self.input) > 1:
                    self.accepting = False
        except ValueError:
            # end input if # or * pressed
            if len(self.input) > 0:
                self.accepting = False

    def get_input(self):
        return self.input

    def start_input(self):
        self.input = ""
        self.accepting = True

    def input_finished(self):
        return self.accepting is False

    def shutdown(self):
        self.keypad.cleanup()


