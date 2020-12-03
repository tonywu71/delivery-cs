# -*- coding: utf-8 -*-
import requests
import calendar
import datetime
from dateutil.parser import parse
import pandas as pd
from tqdm import tqdm

""" 
Running this program will create two pickle files containing all the weather data from 1/1/2009 to today.
The first one : daily_weather_data...pkl contains data about one day (average temperature, etc.)
The second one : hourly_weather_data...pkl contains data about one hour (temperature, wind, etc.)

These files can be loaded as pandas dataframes with this line :
df = pd.read_pickle(file_name)
"""

WWO_API_KEY = "e0703fd9cbc64e2caa1165738200212"  # world weather online
WWO_BASE_URL = "https://api.worldweatheronline.com/premium/v1/past-weather.ashx"


def get_weather_data(start_date, end_date=None, location="paris,france", data_format="json", forecast_time_interval="1", key=WWO_API_KEY):
    """
        function to get weather data; limit : 500 calls / day; first data : 1st jan 2009
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


def convert_dict_to_df(data):
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
    # there cause pbs when there is no moon, and seems not that relevant
    per_day_df.drop(['moonrise', 'moonset'], axis='columns', inplace=True)

    # create another dataframe for the hourly data
    hourly_data = per_day_df.pop('hourly')
    hourly_data_features = ['time', 'tempC', 'windspeedKmph', 'winddirDegree', 'weatherCode', 'precipMM', 'humidity',
                            'visibility', 'pressure', 'cloudcover', 'HeatIndexC', 'DewPointC', 'WindChillC', 'WindGustKmph', 'FeelsLikeC', 'uvIndex']
    hourly_data_dict = {feature: [hourly_data[day][hour][feature] for day in range(len(
        hourly_data)) for hour in range(len(hourly_data[day]))] for feature in hourly_data_features}
    per_hour_df = pd.DataFrame(hourly_data_dict)

    return per_day_df, per_hour_df


def convert_to_correct_datatypes(per_day_df, per_hour_df):
    """ returns both dataframe with corrected datatypes """

    # add date to hour columns
    for hour_feature in ('sunrise', 'sunset'):
        per_day_df[hour_feature] = per_day_df["date"] + \
            " " + per_day_df[hour_feature]

    # convert each column to the right datatype
    per_day_dtypes = {}
    for int_feature in ('maxtempC', 'mintempC', 'avgtempC', 'uvIndex', 'moon_illumination'):
        per_day_dtypes[int_feature] = "int64"  # could be 32b
    for float_feature in ('totalSnow_cm', 'sunHour'):
        per_day_dtypes[float_feature] = "float64"  # same
    for datetime_feature in ('date', 'sunrise', 'sunset'):
        per_day_dtypes[datetime_feature] = 'datetime64'
    corrected_per_day_df = per_day_df.astype(per_day_dtypes)

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
    corrected_per_hour_df = per_hour_df.astype(per_hour_dtypes)

    return corrected_per_day_df, corrected_per_hour_df


def save_df_to_pickle(df, file_name):
    df.to_pickle(file_name)


def load_df(file_name):
    df = pd.read_pickle(file_name)
    return df


def get_all_data_available(save=True):
    """ saves and returns all the data since the 1st of January 2009 to the present """
    all_daily_df = []
    all_hourly_df = []
    # for each year since 2009
    for year in tqdm(range(2009, 2020+1), unit="year"):
        # for each month (jan -> dec)
        for month in range(1, 12+1):
            # get all the data of this month
            raw_data = get_month_weather_data(str(month), str(year))
            if raw_data:
                # convert it to dataframe
                daily_df, hourly_df = convert_dict_to_df(raw_data)
                # convert the dtypes
                c_daily_df, c_hourly_df = convert_to_correct_datatypes(
                    daily_df, hourly_df)
                all_daily_df.append(c_daily_df)
                all_hourly_df.append(c_hourly_df)
    # group all data in two df
    complete_daily_df = pd.concat(all_daily_df)
    complete_hourly_df = pd.concat(all_hourly_df)

    if save:
        save_df_to_pickle(complete_daily_df,
                          "daily_weather_data_from_2009_to_present.pkl")
        save_df_to_pickle(complete_hourly_df,
                          "hourly_weather_data_from_2009_to_present.pkl")

    return complete_daily_df, complete_hourly_df


if __name__ == "__main__":
    get_all_data_available()
