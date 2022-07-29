# Project Tree

* DeepLearning
    * DataEngine.py is a helper file to read and process the dataset
    * DeepLSolar.py creates, trains and tests a cnn lstm model and stores it in tflite format
    * DeepLTransformer.py creates, trains and tests a transformer model
* Backend
    * Main backend API BackendProcess.py
    * PowerController.py is the scheduler that logs power consumption, controls the systems and sends the commands to the backend
    * HouseInterface.py is a class file that handles the communication with the house outside (house or simulated house)
    * DatabaseModule.py is a class that handles inserts, updates and deletes to the database
    * StateMachine.py is a class that handles decisions made by the power controller
* Simulator
    * GridSimulator.py is a file that has routes to add to the backend API to simulate the house through the HouseInterface
    * SimulatorControl.py is a simple streamlit frontend to control the simulators output
* Tools
    * Is a folder that contains all the tools used for the project
    * ApiRequest.py is a helper file to make http requests on json APIs
    * Console.py holds a log function that can be used to print to the console with date and time
    * ForecastPower.py takes a processed dataframe and returns a forecasted power consumption
    * Shelly.py is a helper file to make requests to the shellies in the house
    * SolarEdgeModebus.py is the interface to the solar inverter
    * TeslaControl.py controls the tesla
    * VisualCorssingApi.py is used to get weather forecasts from the next day
* Testing
    * IntegrationTest.py is a file that tests the integration of the backend. Make sure to run the backend in simulation mode to execute the tests
    * UnitTest.py is a file that runs some basic unit tests on different funtions
    * ModelTest.py opens ./models/VisualCrossing_LSTM_model_splited_day.h5 and runs through the dataset to compare to real-world data from solaredge
* WebServer
    * Dashboard.py is the streamlit frontend
* cache.json (needs to be crated) is a file that stores the tesla owner API keys
* secret.py (needs to be crated) is a setting file that stores private keys and ips
* requirements.txt is a file that stores the python requirements for the project

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
4. Get a tesla API token
    *  run Tools/TeslaControl.py
    *  Log in with the tesla account that is tied to the tesla
    *  Copy the URL after the login and paste it 
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

for the deploy running, a raspberry pi 3 Model B Vi.2 is used. It could be done on other models as long as a 64-bit version is compatible because tensorflow seems to not run on 32-bit.

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
   - Make sure a trained model is present with the secret.py file set with the correct API keys
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
