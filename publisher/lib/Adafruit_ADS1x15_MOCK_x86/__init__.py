import random

class ADS1115:
    """Mocking class."""
    def __init__(*args, **kwargs):
        pass
    
    def read_adc(*args, **kwargs):
        """Simulation function that mocks ADC readings from the Pi."""
        return random.randint(-32767,32767)

