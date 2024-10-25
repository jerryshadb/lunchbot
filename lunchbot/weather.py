'''
Module to fetch weather forecast for the day.
API used https://www.ilmatieteenlaitos.fi/avoin-data
'''

import datetime
import requests as rq
import pandas as pd
import xml.etree.ElementTree as ET


def create_url(city: str, n_hours: int = 12) -> str:
    """
    Generates the API URL for fetching weather data for the specified city and duration.
    
    Parameters:
    - city (str): Target city for the weather data.
    - n_hours (int): Forecast duration in hours (max 12).
    
    Returns:
    - str: Formatted API URL.
    """
    n_hours = min(n_hours, 12)
    current_time = datetime.datetime.now()
    end_time = current_time + datetime.timedelta(hours = n_hours)
    
    return (
        f"http://opendata.fmi.fi/wfs?service=WFS&version=2.0.0&request=getFeature&"
        f"storedquery_id=ecmwf::forecast::surface::point::simple&place={city.lower()}&"
        f"starttime={current_time.strftime('%Y-%m-%dT08:00:00Z')}&"
        f"endtime={end_time.strftime('%Y-%m-%dT%H:%M:%SZ')}&"
    )


def get_weather_xml(url: str) -> str:
    """Fetches XML data from the weather API URL."""
    response = rq.get(url)
    response.raise_for_status()
    return response.text


def parse_weather_xml(xml_data: str) -> pd.DataFrame:
    """
    Parses XML data to create a DataFrame with location, time, parameter name, and values.
    
    Parameters:
    - xml_data (str): XML formatted weather data from the API.
    
    Returns:
    - pd.DataFrame: DataFrame containing parsed weather data.
    """
    root = ET.fromstring(xml_data)
    records = []

    for element in root.findall('.//BsWfs:BsWfsElement', namespaces={'BsWfs': 'http://xml.fmi.fi/schema/wfs/2.0'}):
        try:
            records.append({
                'Location': element.find('.//gml:pos', namespaces={'gml': 'http://www.opengis.net/gml/3.2'}).text,
                'Time': element.find('.//BsWfs:Time', namespaces={'BsWfs': 'http://xml.fmi.fi/schema/wfs/2.0'}).text,
                'ParameterName': element.find('.//BsWfs:ParameterName', namespaces={'BsWfs': 'http://xml.fmi.fi/schema/wfs/2.0'}).text,
                'ParameterValue': float(element.find('.//BsWfs:ParameterValue', namespaces={'BsWfs': 'http://xml.fmi.fi/schema/wfs/2.0'}).text)
            })
        except AttributeError:
            pass  # Skip entries with missing data

    df = pd.DataFrame(records)
    df['Time'] = pd.to_datetime(df['Time'])
    return df



def get_weather(df: pd.DataFrame) -> pd.DataFrame:
    """Filters DataFrame for relevant weather parameters."""
    return df[df['ParameterName'].isin(['Temperature', 'WindSpeedMS', 'PrecipitationAmount', 'Precipitation1h', 'TotalCloudCover'])]



def terrace_weather(df: pd.DataFrame, min_temp: int = 15) -> bool:
    """
    Checks if conditions are favorable for outdoor seating ('terassikeli').

    Parameters:
    - df (pd.DataFrame): Filtered DataFrame with latest weather data.
    - min_temp (int): Minimum temperature for favorable conditions.
    
    Returns:
    - bool: True if conditions are favorable, False otherwise.
    """
    latest_data = df.loc[df.groupby('ParameterName')['Time'].idxmax()]
    conditions = {
        'Temperature': latest_data[latest_data['ParameterName'] == 'Temperature']['ParameterValue'].iloc[0] >= min_temp,
        'WindSpeedMS': latest_data[latest_data['ParameterName'] == 'WindSpeedMS']['ParameterValue'].isna(),
        'Precipitation1h': latest_data[latest_data['ParameterName'] == 'Precipitation1h']['ParameterValue'].iloc[0] == 0.0,
        'TotalCloudCover': latest_data[latest_data['ParameterName'] == 'TotalCloudCover']['ParameterValue'].isna()
    }
    return all(conditions.values())

def get_weather_by_hour(df: pd.DataFrame, time_of_day: int) -> pd.DataFrame:
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


def get_weather_data(n_hours: int, city: str) -> pd.DataFrame:
    '''
    Fetch weather data for <city> for the next n_hours, starting from the current time.
    Total amount of weather data fetched is from 8AM to current_time + n_hours
    '''
    weather_xml = get_weather_xml(create_url(n_hours = n_hours, city = city))
    weather_df = parse_weather_xml(weather_xml)
    return get_weather(weather_df)

def get_current_and_next_hour_data(weather_data: pd.DataFrame, hour: int) -> pd.DataFrame:
    '''
    Filtering function to extract current and the following hours' weather data

    Parameters:
    weather_data (pd.DataFrame): DF containing weather data
    hour (int): time of day as an integer.

    Returns:
    Weather data for the current and next hours.
    '''
    current_hour_data = get_weather_by_hour(weather_data, hour)
    next_hour_data = get_weather_by_hour(weather_data, hour + 1)
    return current_hour_data, next_hour_data

def get_parameter_value(data: pd.DataFrame, parameter_name: str) -> str | int:
    '''
    Reads single weather value from df and returns it.

    Parameters:
    df (pd.DataFrame): DF containing weather data
    parameter_name (str): Column which value to extract

    Returns:
    Value of parameter parameter_name.

    Used in main to determine weather conditions.
    '''
    parameter_data = data[data['ParameterName'] == parameter_name]
    return parameter_data['ParameterValue'].values[0]


if __name__ == '__main__':
    # Fetch weather data for <location> for the next n hours
    weather_xml = get_weather_xml(create_url(n_hours = 3, city = 'HElsiNKi'))
    weather_df = parse_weather_xml(weather_xml)
    print(get_weather(weather_df))