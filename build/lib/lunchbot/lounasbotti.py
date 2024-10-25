'''
Prints the restaurant for today with weather and whether it's terrace_weather or not
'''

from .restaurant_scraper import *
from .weather import *
import click


@click.command()
@click.option('--location', type=str, default='vallihaudankatu-turku', 
              help='Specify the location (default: vallihaudankatu-turku)')
@click.option('--max_distance', type=int, default=500, 
              help='Specify the maximum distance in meters (default: 500)')
@click.option('--time_of_day', type=int, default=11, 
              help='Specify the time of day in hours (default: 11)')
@click.option('--ignore_rain/--no-ignore_rain', default=False,
              help='Specify whether to ignore rain (default: False)')
def main(location, max_distance, time_of_day, ignore_rain):
    

    time_of_day = time_of_day
    max_distance = max_distance
    location = location
    city = location.split('-')[1]
    ignore_rain = ignore_rain

    URL = f"https://www.lounaat.info/{location}"

    # Get weather data
    print('Reading weather...')
    weather_data = get_weather_data(n_hours = 12, city = city)
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

    # If it's raining, and you mind, limit restaurant selection to 5 closest
    if rain_now >= 1.0 and not ignore_rain:
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
    print(f"Terassikeli nyt: {terrace_weather(df = current_hour_data, min_temp = 20)}")
    print(f"Terassikeli klo {time_of_day + 1}: {terrace_weather(df = next_hour_data, min_temp = 20)}")

if __name__ == '__main__':
    main()