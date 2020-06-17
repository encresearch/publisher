import random

class ADS1115:
    """Mocking class."""
    def __init__(*args, **kwargs):
        pass
    
    def read_adc(*args, **kwargs):
        return

    x = random.uniform(-32767,32767)
    print("Number is " ,x)
                ##get random number between plus/minus 32767

