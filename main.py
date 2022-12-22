# Libraries
from sense_hat import SenseHat
import subprocess
import time
from dotenv import dotenv_values
import BlynkLib
import requests

# Used for debugging
debug_mode = False

# Load environmental data
config = dotenv_values(".env")

# Initialize Blynk
blynk = BlynkLib.Blynk(config["BLYNK_AUTH_TOKEN"])

# Initialise SenseHAT
sense = SenseHat()
sense.clear()


# Register handler for virtual pin V0 write event
@blynk.on("V0")
def v3_write_handler(value):
    buttonValue = value[0]
    print(f'Current button value: {buttonValue}')

    # Read button value to control the device power
    if buttonValue == "1":
        url = 'https://maker.ifttt.com/trigger/turn_on/with/key/'+config["IFTTT_KEY"]
        response = requests.post(url)
    else:
        url = 'https://maker.ifttt.com/trigger/turn_off/with/key/'+config["IFTTT_KEY"]
        response = requests.post(url)


def read_environmental_data():
    # ----- Sense Hat -----
    # Read CPU temperature using the vcgencmd utility and decode bytes object returned by output to regular Unicode string
    cpu_temp_bytes = subprocess.check_output("vcgencmd measure_temp", shell=True).decode() 
    cpu_temp = cpu_temp_bytes.split("=")[1].split("'")[0]

    # Convert the CPU temperature from a string to a float
    cpu_temp = float(cpu_temp)
    if debug_mode == True:
        print("CPU T:", cpu_temp)

    # Read sensor temperature
    temp = sense.get_temperature()
    if debug_mode == True:
        print("Sensor T:", temp)

    # Calibrate temperature
    factor = 1.6
    temp_calibrated = temp - ((cpu_temp - temp)/factor)
    temp_calibrated = float("{0:.2f}".format(temp_calibrated))
    if debug_mode == True:
        print("Calibrated T:", temp_calibrated)

    return temp_calibrated


# Send temperature exceeded notification
def send_temperature_notification():
    url = 'https://maker.ifttt.com/trigger/temperature_exceeded/with/key/'+config["IFTTT_KEY"]
    response = requests.post(url)

notification_cooldown = 0 # Initialize timer for mobile notifications
target_temperature = 22

while True:
    blynk.run()
    temperature = read_environmental_data()
    blynk.virtual_write(1, temperature) # write environmental data to Blynk

    # ----- Limit number of notifications sent to the user -----
    if temperature >= target_temperature and notification_cooldown == 0:
        send_temperature_notification()
        notification_cooldown = 60 # With sleep time 0.5 and cooldown 60, notification can trigger every 30 seconds
    elif notification_cooldown > 0:
        notification_cooldown -= 1

    time.sleep(.5)