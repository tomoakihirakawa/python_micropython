#!/bin/bash

echo "copy alll files to $1"
echo "ampy -p $1 put ssid_pwd.json"
ampy -p "$1" put ssid_pwd.json
echo "ampy -p $1 put openNetwork"
sudo rm -r openNetwork/__pycache__
ampy -p "$1" put openNetwork
echo "ampy -p $1 put servomotor"
sudo rm -r servomotor/__pycache__
ampy -p "$1" put servomotor
echo "ampy -p $1 put steppermotor"
sudo rm -r steppermotor/__pycache__
ampy -p "$1" put steppermotor
echo "ampy -p $1 put PCA9685"
sudo rm -r PCA9685/__pycache__
ampy -p "$1" put PCA9685
echo "ampy -p $1 put pressureSensors"
sudo rm -r pressureSensors/__pycache__
ampy -p "$1" put pressureSensors
echo "ampy -p $1 put AHRS"
sudo rm -r AHRS/__pycache__
ampy -p "$1" put AHRS
echo "ampy -p $1 put libi2c"
sudo rm -r libi2c/__pycache__
ampy -p "$1" put libi2c
echo "ampy -p $1 put display"
sudo rm -r display/__pycache__
ampy -p "$1" put display
echo "ampy -p $1 put boot.py"
ampy -p "$1" put boot.py
echo "ampy -p $1 put main.py"
ampy -p "$1" put main.py
