# -*- coding: utf-8 -*-
import requests
import calendar
import datetime
from dateutil.parser import parse
import pandas as pd


WWO_API_KEY = "e0703fd9cbc64e2caa1165738200212"  # world weather online
WWO_BASE_URL = "https://api.worldweatheronline.com/premium/v1/past-weather.ashx"


# location : use lattitude, longitude
# heure : format = hmm (24h); ex: 1500 = 15 heures


def get_weather_data(start_date, end_date=None, location="paris,france", data_format="json", forecast_time_interval="1", key=WWO_API_KEY):
    """ 
        function to get weather data; limit : 500 calls / day
        parameters : 
            start_date, end_date : "yyyy-mm-dd"
            location : city or lattitude and longitude : "XX.XXX,XX.XXX"; when using "paris", the location is 48.867, 2.333
            forecast_time_interval : time interval (in hours) 
        output:
            list of dictionnaries for each day beatween start_date and end_date
    """
    params_dict = {'date': start_date, 'q': location,
                   'format': data_format, 'tp': forecast_time_interval, 'key': key}
    if end_date:
        params_dict['enddate'] = end_date

    r = requests.get(WWO_BASE_URL, params=params_dict)
    json_data = r.json()

    if 'error' in json_data:
        print(json_data['error'][0]['msg'])
        return None
    return json_data['data']['weather']


def get_month_weather_data(month, year):
    start_date = "-".join([year, month, "1"])
    last_month_day = calendar.monthrange(int(year), int(month))[1]
    end_date = "-".join([year, month, str(last_month_day)])

    # verify if the dates are available
    today = datetime.date.today()
    if parse(start_date).date() <= today <= parse(end_date).date():
        end_date = today.strftime(r"%Y-%m-%d")
        print(end_date)
    elif today < parse(start_date).date():
        return None

    month_data = get_weather_data(start_date, end_date)
    return pd.DataFrame(month_data)


# test
# print(len(get_weather_data('2020-12-2')[0]['hourly']))
print(get_month_weather_data("12", "2020").columns)
