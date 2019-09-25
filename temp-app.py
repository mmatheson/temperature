import time
import json
import requests
import argparse

TEMP_SENSOR="/sys/bus/w1/devices/28-000008e233e8/w1_slave"
HONEYCOMB_URL="https://api.honeycomb.io/1/events/p70"

def read_sensor():
    with open(TEMP_SENSOR, 'r') as sensor:
        return sensor.readlines()
    
def parse_sensor_output(sensor_output):
    temperature = sensor_output[1].split('t=')[1]
    
    # Check that the temperature is not invalid
    if temperature != -1:
        temperature_celsius = round(float(temperature) / 1000.0, 1)
        temperature_fahrenheit = round((temperature_celsius * 1.8) + 32.0, 1)
        return {'celsius': temperature_celsius, 'fahrenheit': temperature_fahrenheit, 'ts':time.time()}

    return "Failed to parse"

def get_temp():
    sensor_data = read_sensor()
    temperature_data = parse_sensor_output(sensor_data)
    return temperature_data


def collect_temps(location):
    while True:
        temp = get_temp() 
        temp["location"] = location
        print(temp)
        hdrs = {"X-Honeycomb-Team": "d1604e424cca01456f506fcc5a0f69af"}
        try:
            requests.post(HONEYCOMB_URL, data=json.dumps(temp), headers=hdrs, timeout=100)
        except Exception as E:
            print("Failed to post request: {} (time: {})".format(E, time.time()))

        time.sleep(5 * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Set a location for these samples')
    parser.add_argument('--location', dest='loc', help='set the location for the samples')
    args = parser.parse_args()
    loc = args.loc
    collect_temps(loc)

