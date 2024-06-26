from time import strptime
import requests
import config as config
import pandas as pd
from datetime import datetime
# from AccountBook import worksheet

class ExchangeRate():
    """
    frequently used currencies:
    TWD, CNY, USD, JPY, EUR
    """
    def __init__(self, base_country_name):
        self.base_country_name = base_country_name
        self.url = f"https://v6.exchangerate-api.com/v6/{config.EXCHANGE_RATE_API_KEY}/latest/{base_country_name}"
        self.response = requests.get(self.url)
        self.data = self.response.json()

    def getRate(self, country_name):
        return self.data['conversion_rates'][country_name]


if __name__ == "__main__":
    # 1 NTD to how many JPY
    print(ExchangeRate("TWD").getRate("JPY"))
