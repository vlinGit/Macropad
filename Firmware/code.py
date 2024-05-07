import time
import board
import digitalio
import usb_hid
import keypad
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

kbd = Keyboard(usb_hid.devices)
cc = ConsumerControl(usb_hid.devices)
led = digitalio.DigitalInOut(board.LED)
led.switch_to_output()

rows = [board.GP21, board.GP20, board.GP19, board.GP18]  # Example pins, adjust as needed
columns = [board.GP9, board.GP8, board.GP7, board.GP6]  # Example pins, adjust as needed

# Keymap definition as well as different modes
mediaMode = [
    ConsumerControlCode.VOLUME_DECREMENT , ConsumerControlCode.VOLUME_INCREMENT, ConsumerControlCode.MUTE, 3,
    ConsumerControlCode.SCAN_PREVIOUS_TRACK , ConsumerControlCode.PLAY_PAUSE, ConsumerControlCode.SCAN_NEXT_TRACK , -1,
    -1, -1, -1, -1,
    -1, -1, -1 , -1
]
functionMode = [
    Keycode.LEFT_SHIFT,Keycode.F14,Keycode.F15,"3",
    Keycode.F13,Keycode.F17,Keycode.F18,Keycode.F19,
    Keycode.F16,Keycode.F21,Keycode.F22,Keycode.F23,
    Keycode.LEFT_CONTROL, Keycode.F20, -1, Keycode.SPACE
]
reservedKeys = [3]
keys = mediaMode
currentMode = 0 # 0 = defaultMode, 1 = functionMode

km = keypad.KeyMatrix(
    row_pins = (board.GP21, board.GP20, board.GP19, board.GP18),
    column_pins = (board.GP9, board.GP8, board.GP7, board.GP6)
)

def getKey(keyNumber):
    if keyNumber < len(keys):
        return keys[keyNumber]
    return -1

def handleReservedKey(keyNumber):
    global currentMode, keys
    if keyNumber == 3:
        if currentMode:
            keys = mediaMode
            currentMode = 0
        else:
            keys = functionMode
            currentMode = 1

def handleKey(key):
    if currentMode == 0:
        cc.send(key)
    else:
        kbd.press(key)

def keyEvent(keyEvent):
    key = getKey(keyEvent.key_number)

    if key != -1:
        if keyEvent.pressed:
            if keyEvent.key_number in reservedKeys:
                handleReservedKey(keyEvent.key_number)
            else:
                handleKey(key)
        elif keyEvent.key_number not in reservedKeys:
            kbd.release(key)

    return key

def handleLed():
    if currentMode:
        led.value = True
    else:
        led.value = False

# Will be used in the future to remember the state of the pad mode after a reset
def writePadState(state):
    try:
        file = open("padState.txt", "w")
        file.truncate(0)
        file.write(state)
        file.close()
        return True
    except:
        return False

def getPadState():
    try:
        file = open("padState.txt", "r")
        state = file.readlines()[0]
        file.close()

        return state
    except:
        return ""

# Main loop
while True:
    event = km.events.get()

    handleLed()
    if event:
        key = keyEvent(event)

    time.sleep(0.001)  # Adjust delay as neede
