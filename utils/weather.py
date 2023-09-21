'''
Module to fetch weather forecast for the day.
API used https://www.ilmatieteenlaitos.fi/avoin-data
'''

import datetime
import requests as rq
import pandas as pd
import xml.etree.ElementTree as ET



def create_url(n_hours: int):
    '''
    Generates url for API call. n_hours: how long into the future the forecast reaches. Maximum is 36 hours.
    '''
    # Define the current date and time values
    current_datetime = datetime.datetime.now()
        # Ensure the new endtime is within the valid range (no more than 36 hours into the future)
    max_hours = 36
    if n_hours > max_hours:
        raise ValueError(f"n_hours cannot exceed {max_hours}.")
    
    # Calculate the new datetime for the endtime by adding n_hours
    new_datetime = current_datetime + datetime.timedelta(hours = n_hours)
    
    # Format the date and time strings for both starttime and endtime
    start_date_str = current_datetime.date().isoformat()
    
    end_date_str = new_datetime.date().isoformat()
    end_time_str = new_datetime.strftime("%H:%M:%S")
    
    # Build the URL
    url = f"http://opendata.fmi.fi/wfs?service=WFS&version=2.0.0&request=getFeature&storedquery_id=ecmwf::forecast::surface::point::simple&place=turku&starttime={start_date_str}T00:00:00Z&endtime={end_date_str}T{end_time_str}Z&"
    
    return url

def get_weather_xml(url: str):
    return rq.get(url).text


def generate_df_from_xml(xml_data):
    '''
    Function to parse the XML data returned by API and return a DataFrame
    Input format: requests.get(url).text
    '''
    root = ET.fromstring(xml_data)
    data = []
    
    for member in root.findall('.//BsWfs:BsWfsElement', namespaces={'BsWfs': 'http://xml.fmi.fi/schema/wfs/2.0'}):
        location = member.find('.//gml:pos', namespaces={'gml': 'http://www.opengis.net/gml/3.2'}).text
        time = member.find('.//BsWfs:Time', namespaces={'BsWfs': 'http://xml.fmi.fi/schema/wfs/2.0'}).text
        parameter_name = member.find('.//BsWfs:ParameterName', namespaces={'BsWfs': 'http://xml.fmi.fi/schema/wfs/2.0'}).text
        parameter_value = member.find('.//BsWfs:ParameterValue', namespaces={'BsWfs': 'http://xml.fmi.fi/schema/wfs/2.0'}).text
        
        data.append({
            'Location': location,
            'Time': time,
            'ParameterName': parameter_name,
            'ParameterValue': float(parameter_value)
        })
    
    df = pd.DataFrame(data)
    return df


def get_turku_weather(df):
    df['Time'] = pd.to_datetime(df['Time'])
    df = df[df['ParameterName'].isin(['Temperature', 'WindSpeedMS', 'PrecipitationAmount', 'Precipitation1h', 'TotalCloudCover'])]

    return df


def terrace_weather(df):
    '''
    Function to determine whether it's 'terassikeli' i.e. you can eat outside.
    '''

    # Group by 'ParameterName' and find the row with the latest timestamp in each group
    latest_timestamp_df = df.loc[df.groupby('ParameterName')['Time'].idxmax()]

    # Define conditions for the rows you want to check
    conditions = (
    (latest_timestamp_df['ParameterName'] == 'Temperature') & (latest_timestamp_df['ParameterValue'] >= 20) |
    (latest_timestamp_df['ParameterName'] == 'WindSpeedMS') & latest_timestamp_df['ParameterValue'].isna() |
    (latest_timestamp_df['ParameterName'] == 'TotalCloudCover') & latest_timestamp_df['ParameterValue'].isna() |
    (latest_timestamp_df['ParameterName'] == 'Precipitation1h') & (latest_timestamp_df['ParameterValue'] == 0.0) |
    (latest_timestamp_df['ParameterName'] == 'PrecipitationAmount') & latest_timestamp_df['ParameterValue'].isna()
    )


    return conditions.all()

def get_weather_by_hour(df, time_of_day):
    '''
    Function to get the current weather based on the specified time of day (hour).
    '''
    # Filter the DataFrame based on the specified time of day (hour)
    df = df[df['Time'].dt.hour == time_of_day]

    # Group by 'ParameterName' and find the row with the latest timestamp in each group
    latest_timestamp_df = df.loc[df.groupby('ParameterName')['Time'].idxmax()]

    # Filter the DataFrame based on the conditions to get the current weather
    latest_timestamp_df = latest_timestamp_df[latest_timestamp_df['ParameterName'].isin(['Temperature', 'WindSpeedMS', 'PrecipitationAmount', 'Precipitation1h', 'TotalCloudCover'])]

    return latest_timestamp_df
