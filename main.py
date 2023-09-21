'''
Prints the restaurant for today with weather and whether it's terrace_weather or not
'''
"""
TODO
Integrate to Slack via Bot. Might be a no-go to since I don't think any workspace admins at work want to waste their time for
the Finland offices lunch bot lol

Add command line flags so that time of day and max distance can be left blank and/or they can be specified like --max_distance 400 --time_of_day 12
"""

from utils.restaurant_scraper import get_menu_list, clean_menu_list, create_df, restaurant_for_the_day, URL
from utils.weather import generate_df_from_xml, get_turku_weather, get_weather_by_hour, get_weather_xml, create_url, terrace_weather
import sys

def get_weather_data():
    # Fetch weather data for Turku for the next 10 hours
    weather_xml = get_weather_xml(create_url(n_hours=10))
    weather_df = generate_df_from_xml(weather_xml)
    return get_turku_weather(weather_df)

def get_current_and_next_hour_data(weather_data, hour):
    current_hour_data = get_weather_by_hour(weather_data, hour)
    next_hour_data = get_weather_by_hour(weather_data, hour + 1)
    return current_hour_data, next_hour_data

def get_parameter_value(data, parameter_name):
    parameter_data = data[data['ParameterName'] == parameter_name]
    return parameter_data['ParameterValue'].values[0]

def main():

    # Ensure a valid integer is provided as a command-line argument
    time_of_day = sys.argv[1]
    max_distance = sys.argv[2]
    if not time_of_day.isdigit():
        raise ValueError(f'Time must be an integer: entered {time_of_day}')
    if not max_distance.isdigit():
        raise ValueError(f'Distance must be an integer: entered {max_distance}')
    
    time_of_day = int(time_of_day)
    max_distance = int(max_distance)

    # Get weather data
    print('Reading weather...')
    weather_data = get_weather_data()
    print('Weather read.')

    # Get current and next hour weather data
    current_hour_data, next_hour_data = get_current_and_next_hour_data(weather_data, time_of_day)

    # Extract relevant weather parameters
    temperature_now = get_parameter_value(current_hour_data, 'Temperature')
    rain_now = get_parameter_value(current_hour_data, 'PrecipitationAmount')
    temp_in_an_hour = get_parameter_value(next_hour_data, 'Temperature')
    rain_in_an_hour = get_parameter_value(next_hour_data, 'PrecipitationAmount')

    # Fetch restaurant data
    print(f'Reading restaurants from {URL}')
    restaurant_df = create_df(clean_menu_list(get_menu_list(URL)))
    restaurant_df = restaurant_df.sort_values(by = ['Etäisyys'])
    restaurant_df = restaurant_df[restaurant_df['Etäisyys'] <= max_distance]
    print(f'Restaurants read: {len(restaurant_df)} in total')

    # If it's raining, limit restaurant selection to 5 closest
    if rain_now >= 2.0:
        restaurant_df = restaurant_df.head(5)

    restaurant = restaurant_for_the_day(restaurant_df)

    restaurant_name = restaurant['Ravintola'].values[0]
    menu = restaurant['Menu'].values[0]
    distance = restaurant['Etäisyys'].values[0]

    # Print the information and copypaste to Slack
    print(":robot_face:Lounasbotti tiedottaa:robot_face:\n")
    if distance >= 1000:
        print(f"Päivän ravintolana toimii {restaurant_name}, n. {distance / 1000} kilometrin päässä\n")
    else:
        print(f"Päivän ravintolana toimii {restaurant_name}, n. {distance} metrin päässä\n")
    print("Luvassa on:\n")
    for setti in menu:
        print(setti)
    print("\n")
    print(f"Lämpötila nyt: {temperature_now}")
    print(f"Sade nyt: {rain_now}")
    print(f"Lämpötila klo {time_of_day + 1}: {temp_in_an_hour}")
    print(f"Sade klo {time_of_day + 1}: {rain_in_an_hour}")
    print(f"Terassikeli nyt: {terrace_weather(current_hour_data)}")
    print(f"Terassikeli klo {time_of_day + 1}: {terrace_weather(next_hour_data)}")
if __name__ == "__main__":
    main()