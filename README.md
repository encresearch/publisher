![PUBLISHER](./docs/images/publisher_logo.png)
# PUBLISHER: Raspberry Pi Client for Sending Sensor Data
![CI Simulation Tests](https://github.com/encresearch/publisher/workflows/Publisher%20Simulation%20CI/badge.svg?branch=master)


Raspbian client that reads and sends data acquired by four [Adafruit ADS1115](https://learn.adafruit.com/adafruit-4-channel-adc-breakouts/overview) units connected to a Rapsberry Pi at 10Hz sample rate over MQTT to a broker.

This code can also be executed from a regular `x86` machine for development or simulation purposes. If executed this way, the main file makes use of a simulation library that returns random values for the function `Adafruit_ADS1x15.ADS1115.read_adc()`. The topic to which it's sent to our MQTT broker is also prepended with `test_env/`. Please see instructions below of how to run it in simulation mode.

This is the publishing side of the [Data Acquisition Platform](https://github.com/encresearch/data-assimilation-system).

## Hardware Setup

### Powering the ADCs
Each ADC unit can be powered with either 5v or 3.3v. Bare in mind that the maximum input voltage in each of the ADCs' units is VDD.

### I2C Connection
The Adafruit ADS1115 uses the I2C bus to communicate. This protocol needs just two pins to connect **SCL** and **SDA**. These can be shared by several I2C devices as long as the addresses are different. You need to enable the I2C interface in the Raspberry Pi. For this, open the terminal and type:

```
$ sudo raspi-config
```

This will open the ```Raspberry Pi Software Configuration Tool```. After this, go to ```Interfacing Options```, then ```P5 I2C```, and enter ```Yes``` to enable the ARM I2C interface.

The ADS11x5 chips have a base 7-bit I2C address of 0x48 (1001000) and allows four different addresses using the ADR pin. To program the address, connect the address pin as follows:
* 0x48 (1001000) ADR -> GND
* 0x49 (1001001) ADR -> VDD
* 0x4A (1001010) ADR -> SDA
* 0x4B (1001011) ADR -> SCL

For a complete setup of four ADS1115 units with different address, connect as below:

![ADS1115 Wiring Diagram](./docs/images/wiring.png)
For more information about the Raspberry Pi GPIO, visit [here](https://www.raspberrypi.org/documentation/usage/gpio/).

## Install and Run 
These instructions are to get ```publisher``` up and running in your ```Raspberry Pi```. Make sure the hardware and wiring are set up correctly before trying to run the software.

The dependencies can be met either by cloning into the project and setting up a virtual environment based on one of our requirement files (dev, dev_x86, test, prod), or by building the publisher container using the ```docker-compose.dev.yml``` file. The dev_x86 will install the necessary packages to run this repo in simulation mode in a non-RaspberryPi machine. Instructions for both cases are explained below.

### Install and run with Docker

Install [Docker](https://docs.docker.com/install/)
```
$ sudo apt-get update
$ sudo apt-get upgrade 
$ curl -sSL https://get.docker.com | sh
``` 

Install [Docker-Compose](https://docs.docker.com/compose/install/):

```
$ sudo apt-get install libffi-dev libssl-dev
$ sudo pip install docker-compose
```

Clone repository:

```
$ git clone https://github.com/encresearch/publisher.git
```

Run docker-compose:

```
$ sudo docker-compose -f docker-compose.dev.yml up
```

To stop and remove containers, networks and images created by up. (External volumes won't be removed):

```
$ sudo docker-compose -f docker-compose.dev.yml down
```

### Install and Run without Docker
You will need Python 3 and Pip3 installed. You might also need (depending on your OS and its version) libraries to compile Pandas and Numpy such as:
- gcc
- build-essential
- gfortran
- libopenblas-dev
- libatlas-base-dev

Pay attention to what libraries you're missing during the next step, and just look for the package name online and install them. For example:
```
$ sudo apt-get install gcc libopenblas-dev libatlas-base-dev
```

Install our dependencies:
```
$ pip3 install -r requirements/dev.txt
```

The  script above will install the developlment dependencies, but depending on what you're working you might want to install the x86-simulation (dev_x86.txt), test (test.txt) or production (prod.txt) dependencies.

Run it:
```
$ python3 run.py
```

## Testing
We are constantly updating our tests to cover as much as possible. Right now you can test the wiring and readings of the ADCs prior to deployment or during development.

To run our unit tests locally, first install the necessary dependencies as indicated in the installation section.

Update ```test.sh``` permissions, in case you haven't alredy:
```
$ chmod +x test.sh
```

Run
```
$ ./test.sh
```

One of the tests that wun with this, will just output the readings from all the pins in the terminal. To make sure both hardware and software configurations are correct, use a configurable power supply and input a different voltage for each pin (don't forget to use a common ground with the Pi). You will have to "manually" test that the voltage outputs for each pin are the correct (assigned) ones.

> Integration and E2E tests coming up!

## Error Logging
When errors are encountered while runing the application, and this one fails silently, you can find a traceback of the error in a newly-generated ```publisher.log``` file in the root of this project directory.   

## Simulation Mode
To run in simulation mode, `publisher.py` will have to be executed from an `x86` machine. You will have to first install the dependencies from our `requirements/dev_x86.txt` using pip, and then just execute the `publisher.py` file. Bear in mind that in simulation mode, all ADC readings are random integers between -32767 and 32767 because of the GAIN that we set up the ADCs to in our production environment.

## Contributing
Pull requests and stars are always welcome.

To contribute, create a descriptive branch off of master (ex ```data-migration-tests```), commit to it, and submit a pull request.
