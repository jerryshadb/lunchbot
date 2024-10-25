# Lunch Menu Fetcher

**Author:** Jerry Shadbolt  
**E-mail:** [jerry.shadbolt@windowslive.com](mailto:jerry.shadbolt@windowslive.com)

## Description

Automate the tedious process of picking where to eat lunch with co-workers. This tool allows users to fetch lunch menus from a user specified criteria, such as location, distance, time of day and whether you're ok with rain. 

Location is expected in format address-city, for example kaivokatu-helsinki, with flag --location. It defaults to the Turku harbour.
Time defaults to 11 yet can be changed with --time_of_day. (24-hour format)
Distance defaults to 500 but can be changed with --max_distance.
Rain defaults to False, so you don't ignore it, but can be changed with --ignore_rain

So an example you want to have lunch in Helsinki at 12 and you don't mind the rain, command would be 
```bash
lunchbot --location kaivokatu-helsinki --max_distance 500 --time_of_day 12 --ingore_rain
```
or just
```bash
lunchbot
```
## Features

- Fetch lunch menus based on location.
- Set maximum distance for restaurant searches.
- The 5 closest restaurants are returned if it's raining.
- Specify the time of day for lunch.
- Default values are provided for convenience.

## Requirements

- Python 3.6 or higher
- Necessary libraries (to be installed)

## Installation

Follow these steps to install the project locally using Conda:

1. **Clone the repository:**
```bash
git clone https://github.com/jerryshadb/lunchbot.git
cd lunchbot
```
2. **Create the env (optional)** 
```bash
conda create --name <env> --file requirements.txt python=3.10
```
3. **Install the CLI**
```bash
pip install -e .
```


## NOTE
There seem to be some dependency issues present, however the tool still works correctly.