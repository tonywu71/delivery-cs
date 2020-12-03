# -*- coding: utf-8 -*-
import requests
import calendar
import datetime
from dateutil.parser import parse
import pandas as pd


WWO_API_KEY = "e0703fd9cbc64e2caa1165738200212"  # world weather online
WWO_BASE_URL = "https://api.worldweatheronline.com/premium/v1/past-weather.ashx"


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
    elif today < parse(start_date).date():
        return None

    month_data = get_weather_data(start_date, end_date)
    return month_data


def convert_data_dict_to_df(data):
    """ this return two dataframe : one with the data that changes each day, and one with the data that changes each hour """
    per_day_df = pd.DataFrame(data)
    # delete the data in farenheit (redondant as we have it in degree)
    per_day_df.drop(['maxtempF', 'mintempF', 'avgtempF'],
                    axis='columns', inplace=True)
    # flatten astronomy data
    astronomy_data = per_day_df.pop('astronomy')
    astro_columns = list(astronomy_data[0][0].keys())
    astro_dict = {feature: [astronomy_data[day][0][feature]
                            for day in range(len(astronomy_data))] for feature in astro_columns}
    for feature in astro_dict:
        per_day_df[feature] = astro_dict[feature]

    # create another dataframe for the hourly data
    hourly_data = per_day_df.pop('hourly')
    hourly_data_features = ['time', 'tempC', 'windspeedKmph', 'winddirDegree', 'weatherCode', 'precipMM', 'humidity',
                            'visibility', 'pressure', 'cloudcover', 'HeatIndexC', 'DewPointC', 'WindChillC', 'WindGustKmph', 'FeelsLikeC', 'uvIndex']
    hourly_data_dict = {feature: [hourly_data[day][hour][feature] for day in range(len(
        hourly_data)) for hour in range(len(hourly_data[day]))] for feature in hourly_data_features}
    per_hour_df = pd.DataFrame(hourly_data_dict)

    return per_day_df, per_hour_df


def convert_df_dtypes(df, dtypes):
    """ returns the dataframe with the correct datatypes """
    return df.astype(dtypes)


def get_correct_datatypes(per_day_df, per_hour_df):

    # add date to hour columns
    for hour_feature in ('sunrise', 'sunset', 'moonrise', 'moonset'):
        per_day_df[hour_feature] = per_day_df[date] + \
            " " + per_day_df[hour_feature]

    # convert each column to the right datatype
    per_day_dtypes = {}
    for int_feature in ('maxtempC', 'mintempC', 'avgtempC', 'uvIndex', 'moon_illumination'):
        per_day_dtypes[int_feature] = "int64"  # could be 32b
    for float_feature in ('totalSnow_cm', 'sunHour'):
        per_day_dtypes[float_feature] = "float64"  # same
    for datetime_feature in ('date', 'sunrise', 'sunset', 'moonrise', 'moonset'):
        per_day_dtypes[datetime_feature] = 'datetime64'
    corrected_per_day_df = convert_df_dtypes(per_day_df, per_day_dtypes)

    # add date to time column
    datetime_data = []
    time_data = per_hour_df.pop("time")
    for date in per_day_df["date"]:
        for hour in range(24):
            datetime_string = date + "-" + str(hour) + ":00"
            datetime_data.append(datetime_string)
    per_hour_df["datetime"] = datetime_data

    # convert each column to the right datatype
    per_hour_dtypes = {}
    for int_feature in ('tempC', 'windspeedKmph', 'winddirDegree', 'weatherCode', 'humidity', 'visibility', 'pressure', 'cloudcover', 'HeatIndexC', 'DewPointC', 'WindChillC', 'WindGustKmph', 'FeelsLikeC', 'uvIndex'):
        per_hour_dtypes[int_feature] = "int64"
    per_hour_dtypes['precipMM'] = "float64"
    per_hour_dtypes['datetime'] = "datetime64"
    corrected_per_hour_df = convert_df_dtypes(per_hour_df, per_hour_dtypes)

    return corrected_per_day_df, corrected_per_hour_df


def save_df_to_pickle(df, file_name):
    df.to_pickle(file_name)


def load_df(file_name):
    df = pd.read_pickle(file_name)
    return df


# test
# print(len(get_weather_data('2020-12-2')[0]['hourly']))
# print(get_month_weather_data("12", "2020").columns)
per_day_df, per_hour_df = convert_data_dict_to_df(
    get_month_weather_data("12", "2020"))
# per_hour_df = pd.read_pickle("test.pkl")
