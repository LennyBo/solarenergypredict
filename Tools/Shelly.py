import requests
import json
SHELLY_IP_HEATER = "192.168.0.65"
SHELLY_IP_TESLA = "192.168.0.163"

def shelly_total_power(ip):
    try:
        res = requests.get(f'http://{ip}/status')
        if res.status_code == 200:
            data = res.json()
            return int(data['total_power'])
        else:
            return None
    except requests.exceptions.ConnectionError:
        return None
    except requests.exceptions.JSONDecodeError:
        return None
    except KeyError:
        return None


def heater_power():
    return shelly_total_power(SHELLY_IP_HEATER)

def tesla_power():
    return shelly_total_power(SHELLY_IP_TESLA)


if __name__ == "__main__":
    print(heater_power())
    print(tesla_power())
