# Installation

## creating an executable environment
to install and run the program, the first step is to get all the files downloaded so clone the repository.

1. Train a model to use
   * Run DeepLearning/DeepLSolar.py
   * This will create a tflite file in models/ which is the model that will be used.
2. Create a secret.py file in the root directory.
    * Add the following lines
```
# Visualcrossing api key
API_KEY_VC = "AAAAAAAAAAAAAAAAAAAAAAAA"
# Shelly ip addresses
# If running in simulation, just use placeholder values
SHELLY_IP_HEATER = "XXX.XXX.XXX.XXX"
SHELLY_IP_TESLA = "XXX.XXX.XXX.XXX"
# Solar edge ip address and port
solar_edge_ip = "XXX.XXX.XXX.XXX"
solar_edge_port = 1502 # 1502 is the default port
```
3. Install python dependencies
    * pip install pandas streamlit schedule solaredge_modbus requests bottle cheroot teslapy tensorflow matplotlib sklearn
    * To run the transformer, also install
    * pip install tensorflow_addons
4. Get a tesla api token
    *  run Tools/TeslaControl.py
    *  Log in with the tesla account that is tied to the tesla
    *  Copy the url after the login and paste it 
    *  Check if the cach.json file is created in the root directory

## Running the program

To start the application, run the following commands:

```
py Backend/BackendProcess.py
# In a different terminal
streamlit run Webserver/dashboard.py
# In simulation mode, run the following command on another terminal the get access to the controls
streamlit run Simulator/SimulatorControl.py
```

For development reasons, by default the program will run in simulation mode if running it on a Windows machine.
If it is wished to run the deploy version, go to Backend/BackendProcess.py at lines 112 to 114 and invert the commented out lines.

# Installation on the raspberry pi

for the deploy running, a raspberry pi 3 Model B Vi.2 is used. It could be done on other models as long as a 64 bit version is compatible because tensorflow seems to not run on 32-bit.

64 bit is required to install tensorflow so a version of this project could be made for 32 bit without predictive controls.

1. Install ubuntu 64 bit
2. Install python 3.8

```
sudo apt get update -y && sudo apt upgrade -y
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.8 python3.8-dev python3.8-distutils python3-apt screen
```

3. Alias python3 to python3.8

```bash
nano ~/.bashrc
#Add the following lines
alias python=python3.8
alias pip=python3.8 -m pip
# Then
sudo reboot
```

5. Install tensorflow dependencies

```
# Download tensorflow wheel
curl -L https://github.com/PINTO0309/Tensorflow-bin/releases/download/v2.8.0/tensorflow-2.8.0-cp38-none-linux_aarch64.whl -o tensorflow-2.8.0-cp38-none-linux_aarch64.whl
sudo add-apt-repository universe
sudo apt-get update
sudo apt-get install -y libhdf5-dev libc-ares-dev libeigen3-dev gcc gfortran libgfortran5 libatlas3-base libatlas-base-dev libopenblas-dev libopenblas-base libblas-dev liblapack-dev cython3 libatlas-base-dev openmpi-bin libopenmpi-dev python3-dev
pip install -U wheel mock six
pip install [wheel file]
```

This will a few hours.

Once it is done to test the installation:

```
python
import tensorflow as tf
tf.__version___
```

Should give 2.8.0

4. Install python packages

```
pip install pandas streamlit schedule solaredge_modbus requests bottle cheroot
```

5. Copy the files to the pi
   - Recommend using WinSCP to copy the files to the pi.
   - Make sure a trained model is present with the secret.py file set with the correct api keys
6. Create a startup script on the pi

```bash
nano StartEnergyPredict.sh

#!/bin/sh

cd /home/pi/solarenergypredict
# Kills all screen to restart the program
pkill screen
screen -m -d -L -Logfile BackendApi.log -S BackendScreen python3.8 Backend/BackendProcess.py
screen -m -d -L -Logfile streamlit.log -S StreamlitScreen python3.8 -m streamlit run WebServer/Dashboard.py

```

7. Make the script executable

```
chmod +x StartEnergyPredict.sh
```

8. Run the script

```
./StartEnergyPredict.sh
```

9. This should start all the processes
   - Log files are created in the /home/pi/solarenergypredict directory
   - To take control of the process, use the following command:
     - screen -r BackendScreen
     - screen -r StreamlitScreen
10. Automatically restart the program on reboot (power outage)

```bash
crontab -e

# Add the following line
@reboot /home/pi/StartEnergyPredict.sh
```
