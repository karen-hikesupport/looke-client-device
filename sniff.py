#!/usr/bin/python3
# Sniff air / ethanol
# Keith McAlister 6th May 2023 based on the PI3G Meat and Cheese code.

from bme68x import BME68X
import bme68xConstants as cst
import bsecConstants as bsec
from time import sleep
from pathlib import Path
import json
import numpy as np 


# The export from AI Studio is for BSE C2.4.0.0 snf the first four bytes of the .config file in decimal are 1974
# The .h and .c that studio exports with the config file also has a reference to bsec_config_selectivity[1974] = ...
# So it looks like BSEC can use multiple AI configs and reference them by this index.
# In the PI3G Python Wrapper we use only one config and this function chops off the 1974 header - strictly speaking is chops off the first 4 bytes in the slicer [4:].

gas_sensor_data =[]
# This is the config file output by AI_Studio
config_file = '2023_05_06_15_00_Air-Ethanol_HP-354_RDC-5-10.config'
config_path = str(Path(__file__).resolve().parent.joinpath(config_file))
def read_conf(path: str):
    with open(path, 'rb') as ai_conf:
    	conf = [int.from_bytes(bytes([b]), 'little') for b in ai_conf.read()]
    	conf = conf[4:]
    return conf

def record_gas_sensor_data():
    gas_sensor_data =[]
    # Open the I2C communications and set the operating mode
    bme = BME68X(0X77,0)
    bme.set_sample_rate(bsec.BSEC_SAMPLE_RATE_LP)
    # report on the BME688 and BSEC version
    print(f'SENSOR: {bme.get_variant()} BSEC: {bme.get_bsec_version()}')

    air_ethanol = read_conf(config_path)
    print(f'SET BSEC CONF {bme.set_bsec_conf(air_ethanol)}')

    # Air and Ethanol - two subscriptions (0,1)
    print(f'SUBSCRIBE GAS ESTIMATES {bme.subscribe_gas_estimates(2)}')

    # initialise the sensor
    print(f'INIT BME68X {bme.init_bme68x()}')

    print('\n\nSTARTING MEASUREMENT\n')

    
    data_fetch = True
    i=0
    while(data_fetch):
        # print(bme.get_bsec_data())
        try:
            data = bme.get_digital_nose_data()
            print(data)
        except Exception as e:
            print(e)
            main()
        if data:
            # for entry in bme.get_digital_nose_data():
            entry = data[-1]
            # print(f'{entry}')
            print(f'NORMAL AIR {entry["gas_estimate_1"]:.1%}\nNH3 {entry["gas_estimate_2"]:.1%}')
            print()

            NormalAir = entry["gas_estimate_1"]
            NH3 = entry["gas_estimate_2"]

            # This bit is from the Meat and Cheese PI3G demo - ist writes out the data to file as JASON
            d = {
                'NormalAir': NormalAir,
                'NH3': NH3,
                'CO2':1,
                'CH4':2
            }

            
            i = i+1
            if(i>=11 and i<=20):
                print('skipped ....')
            else:
                gas_sensor_data.append(d)

            if len(gas_sensor_data) > 5:
                  data_fetch = False

            with open('sniff-data.json', 'w') as file:
                json.dump(d, file)

    print(gas_sensor_data)
    
    NormalAir =get_average_value([x["NormalAir"] for x in gas_sensor_data])
    NH3 =get_average_value([x["NH3"] for x in gas_sensor_data])
    CO2 =get_average_value([x["CO2"] for x in gas_sensor_data])
    CH4 =get_average_value([x["CH4"] for x in gas_sensor_data])

    result = {
            'NormalAir': NormalAir,
            'NH3': NH3,
            'CO2':CO2,
            'CH4':CH4
        }
    print(result)
    return result

def get_average_value(sensorArray:any):                
        average = np.mean(sensorArray)
        return average

