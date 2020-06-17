if
#Check for Raspberry Pi
import publisher
#import Adafruit_ADS1x15

else:
    #Warning!! x86 is using MOCK library
    import Adafruit_ADS1x15_MOCK_x86 #to work on x86 machines