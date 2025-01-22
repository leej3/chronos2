from src.core.utils.constant import Relay


class Chiller:

    TYPE = "chiller"

    def __init__(self, number):
        if number not in range(1, 5):
            raise ValueError("Chiller number must be in range from 1 to 4")
        else:
            self.number = number
            self.relay_number = Relay["CHILLER{}".format(number)]
            self.table_class_name = "Chiller{}".format(number)
