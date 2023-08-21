# This example demonstrates the FORCED MODE
# First with BSEC disabled
# Then with BSEC enabled

from bme68x import BME68X
import bme68xConstants as cst
import bsecConstants as bsec
from time import sleep


def get_data():
    print('TESTING FORCED MODE WITHOUT BSEC')
    sensor = BME68X(cst.BME68X_I2C_ADDR_HIGH, 1)
    # Configure sensor to measure at 320 degC for 100 millisec
    sensor.set_heatr_conf(cst.BME68X_FORCED_MODE, 320, 100, cst.BME68X_ENABLE)
    data = sensor.get_data()
    print(data)    
    return data

