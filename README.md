# Samsung---Sericulture-Smart-System
Its a main Samsung IOT Project - About Sericulture Domain 
 Sericulture Control System with Blynk Integration

An IoT-based smart environmental monitoring and control system built using Raspberry Pi and Blynk Cloud. This system automatically monitors temperature and humidity and controls a fan and water pump to maintain ideal conditions for sericulture (silk farming). It also allows manual control and real-time monitoring through the Blynk mobile app.

This project was developed as part of the Samsung Innovation Campus (SIC) program.

 Features

Real-time temperature and humidity monitoring using DHT11 sensor
Automatic fan control when temperature exceeds threshold
Automatic pump control when humidity drops below threshold
Manual control of fan and pump via Blynk app
Real-time status updates on mobile
Cloud-based IoT monitoring
LED indicator for system condition

 Hardware Used

Raspberry Pi
DHT11 Temperature and Humidity Sensor
Relay Module
Fan
Water Pump
LED
Jumper wires

 Software & Libraries

Python 3.11
Blynk IoT Platform
Libraries used:
BlynkLib
adafruit_dht
RPi.GPIO
board

Install dependencies:

pip install blynklib adafruit-circuitpython-dht

⚙️ How It Works

The DHT11 sensor continuously reads temperature and humidity.
If temperature exceeds 25°C, the fan turns ON automatically.
If humidity drops below 50%, the pump turns ON automatically.
Users can manually control devices using the Blynk mobile app.
System sends live data and device status to Blynk Cloud.

 Blynk Virtual Pins
Pin	Function
V0	Temperature
V1	Humidity
V2	Fan Status
V3	Pump Status
V4	Fan Control
V5	Pump Control
V6	System Status

 How to Run

Clone this repository

git clone https://github.com/yourusername/sericulture-control-system.git


Run the Python file

python sericulture_control.py


Connect Blynk app using your Auth Token.

Applications

Smart sericulture farms
Agricultural automation
IoT monitoring systems
Student IoT projects

 Author

Pooja M

Computer Science Engineering Student

Samsung Innovation Campus

Cambridge Institute of Technology North Campus
