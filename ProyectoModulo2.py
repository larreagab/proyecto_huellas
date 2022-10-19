
import time
import board
#import busio
from digitalio import DigitalInOut, Direction
import adafruit_fingerprint
from time import sleep



led = DigitalInOut(board.D13)
led.direction = Direction.OUTPUT
#uart = busio.UART(board.TX, board.RX, baudrate=57600)

# If using with a computer such as Linux/RaspberryPi, Mac, Windows with USB/serial converter:
import serial
#uart = serial.Serial("/dev/ttyUSB0", baudrate=57600, timeout=1)

# If using with Linux/Raspberry Pi and hardware UART:
#import serial
uart = serial.Serial("/dev/ttyAMA0", baudrate=57600, timeout=1)

finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

##################################################


def get_fingerprint():
    """Get a finger print image, template it, and see if it matches!"""
    print("Coloque el dedo en el sensor") 
    print("Esperando la imagen...")
   
    while finger.get_image() != adafruit_fingerprint.OK:
        pass
    print("Modelando...")
          
    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
        return False
    print("Buscando...")
    
    if finger.finger_search() != adafruit_fingerprint.OK:
        return False
    return True


# pylint: disable=too-many-branches
def get_fingerprint_detail():
    """Get a finger print image, template it, and see if it matches!
    This time, print out each error instead of just returning on failure"""
    print("Getting image...", end="", flush=True)
    i = finger.get_image()
    if i == adafruit_fingerprint.OK:
        print("Image taken")
    else:
        if i == adafruit_fingerprint.NOFINGER:
            print("No finger detected")
        elif i == adafruit_fingerprint.IMAGEFAIL:
            print("Imaging error")
        else:
            print("Other error")
        return False

    print("Templating...", end="", flush=True)
    i = finger.image_2_tz(1)
    if i == adafruit_fingerprint.OK:
        print("Templated")
    else:
        if i == adafruit_fingerprint.IMAGEMESS:
            print("Image too messy")
        elif i == adafruit_fingerprint.FEATUREFAIL:
            print("Could not identify features")
        elif i == adafruit_fingerprint.INVALIDIMAGE:
            print("Image invalid")
        else:
            print("Other error")
        return False

    print("Searching...", end="", flush=True)
    i = finger.finger_fast_search()
    # pylint: disable=no-else-return
    # This block needs to be refactored when it can be tested.
    if i == adafruit_fingerprint.OK:
        print("Found fingerprint!")
        return True
    else:
        if i == adafruit_fingerprint.NOTFOUND:
            print("No match found")
        else:
            print("Other error")
        return False


# pylint: disable=too-many-statements
def enroll_finger(location):
    """Take a 2 finger images and template it, then store in 'location'"""
    for fingerimg in range(1, 3):
        if fingerimg == 1:
            print("Coloque el dedo en el sensor...", end="", flush=True)
            
        else:
            print("Coloque el mismo dedo de nuevo...", end="", flush=True)
            
        while True:
            i = finger.get_image()
            if i == adafruit_fingerprint.OK:
                print("Imagen tomada")
                
                sleep(0.5)
                break
            if i == adafruit_fingerprint.NOFINGER:
                print(".", end="", flush=True)
            elif i == adafruit_fingerprint.IMAGEFAIL:
                print("Error de Imagen")
                
                sleep(2)
                return False
            else:
                print("Otro error")
                sleep(2)
                return False

        print("Modelando Imagen...", end="", flush=True)
        
        i = finger.image_2_tz(fingerimg)
        sleep(0.3)
        if i == adafruit_fingerprint.OK:
            print("Modelada")
            sleep(0.5)
        else:
            if i == adafruit_fingerprint.IMAGEMESS:
                print("Imagen borrosa")
                sleep(2)
            elif i == adafruit_fingerprint.FEATUREFAIL:
                print("No se pudo identificar")
                sleep(2)
            elif i == adafruit_fingerprint.INVALIDIMAGE:
                print("Imagen invalida")
                sleep(2)
            else:
                print("Otro error")
                sleep(2)
            return False

        if fingerimg == 1:
            print("Quite el dedo")
            time.sleep(1)
            while i != adafruit_fingerprint.NOFINGER:
                i = finger.get_image()

    print("Creando Modelo...", end="", flush=True)
    
    i = finger.create_model()
    sleep(0.3)
    if i == adafruit_fingerprint.OK:
        print("Creado")

        sleep(0.3)
    else:
        if i == adafruit_fingerprint.ENROLLMISMATCH:
            print("Huellas no coinciden")
            sleep(2)
        else:
            print("Otro error")
            sleep(2)
        return False

#     print("Guardando modelo #%d..." % location, end="", flush=True)
    
    i = finger.store_model(location)
    sleep(0.3)
    if i == adafruit_fingerprint.OK:
        print("Guardado")
        
        sleep(0.5)
    else:
        if i == adafruit_fingerprint.BADLOCATION:
            print("Error de ubicacion")
            sleep(2)
        elif i == adafruit_fingerprint.FLASHERR:
            print("Error de almacenamiento Flash")      
            sleep(2)
        else:
            print("Otro error")
            sleep(2)
        return False

    return True


##################################################


def get_num():
    """Use input() to get a valid number from 1 to 127. Retry till success!"""
    i = 0
    while (i > 127) or (i < 1):
        try:
            i = int(input("Enter ID # from 1-127: "))
        except ValueError:
            pass
    return i


