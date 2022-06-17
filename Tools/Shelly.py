import sys
sys.path.append( '.' ) # Adds parent directory so we can import other modules
import requests
from Tools.ApiRequest import make_request
SHELLY_IP_HEATER = "192.168.0.65"
SHELLY_IP_TESLA = "192.168.0.163"

def shelly_total_power(ip):
    try:
        return make_request(f'http://{ip}/status')['total_power']
    except requests.exceptions.ConnectionError:
        return 0
    except requests.exceptions.JSONDecodeError:
        return 0
    except KeyError:
        return 0 # We could return None for these but that will generate errors down the line


def heater_power():
    return shelly_total_power(SHELLY_IP_HEATER)

def tesla_power():
    return shelly_total_power(SHELLY_IP_TESLA)


if __name__ == "__main__":
    print(heater_power())
    print(tesla_power())
