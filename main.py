import os
import requests
import json
from datetime import datetime
import schedule
import time
import tweepy

# Twitter authenticate keys and tokens
Twitter_api_key = os.environ.get('Twitter_api_key')
Twitter_api_secret = os.environ.get('Twitter_api_secret')
Twitter_access_token = os.environ.get('Twitter_access_token')
Twitter_access_token_secret = os.environ.get('Twitter_access_token_secret')

# Authenticate to Twitter
auth = tweepy.OAuthHandler(Twitter_api_key, Twitter_api_secret)
auth.set_access_token(Twitter_access_token, Twitter_access_token_secret)

twitter = tweepy.API(auth)

try:
    twitter.verify_credentials()
    print("Authentication OK")
except:
    print("Error during authentication")


# Open weather authentication key
API_KEY = os.environ.get('OpenWeatherKey')

# Accuweather authentication key
#API_KEY = 'xaYYBXMhGRMIVOGes6XuXKMhbV1HavuY'

# weather request
city_name = "Wrocław"
city_key = '273125'

def DegToDirection(wind_deg):
    if (0 < wind_deg <= 25):
        wind_direction = 'north'
    elif (335 <= wind_deg <= 360):
        wind_direction = 'north'
    elif (25 < wind_deg <= 65):
        wind_direction = 'north east'
    elif (65 < wind_deg <= 115):
        wind_direction = 'east'
    elif (115 < wind_deg <= 155):
        wind_direction = 'south east'
    elif (155 < wind_deg <= 205):
        wind_direction = 'south'
    elif (205 < wind_deg <= 245):
        wind_direction = 'south west'
    elif (245 < wind_deg <= 295):
        wind_direction = 'west'
    elif (295 < wind_deg <= 335):
        wind_direction = 'north west'
    return wind_direction


def BikeOk(wind_speed):
    if wind_speed < 10:
        bike = 'Yeah, wind speed under 10m/s'
    else:
        bike = 'Hard, wind speed over 10m/s'
    return bike


# job for scheduler
def PostingJob():
    api_request = requests.get('https://api.openweathermap.org/data/2.5/weather?q=' + city_name + '&units=metric&appid=' + API_KEY)
    #api_request = requests.get('http://dataservice.accuweather.com/currentconditions/v1/' + city_key + '?apikey= '+ API_KEY + '&details=true')
    weather = api_request.json()
    print(weather)
    current_time = datetime.now().strftime("%d-%m %H:%M")

    tweet = (current_time +
             "\n-> sky: " + (weather['weather'][0]['description']) +
             "\n-> temperature: " + ('%.1f°C' % weather['main']['temp']) +
             "\n-> feels like: " + ('%.1f°C' % weather['main']['feels_like']) +
             "\n-> wind speed: " + ('%.1fm/s' % weather['wind']['speed']) +
             "\n-> wind direction: " + (DegToDirection(weather['wind']['deg'])) +
             "\n-> humidity: " + (str(weather['main']['humidity']) + '%') +
             "\n-> pressure: " + ('%.0fhPa' % weather['main']['pressure']) +
             "\n-> bike: " + BikeOk(weather['wind']['speed']))

    try:
        twitter.update_status(tweet)
        print('Poszedl post')
    except tweepy.TweepError as error:
        if error.api_code == 187:
            print(current_time + " duplicated message")


schedule.every(2).minutes.do(PostingJob)

while True:
    schedule.run_pending()
    time.sleep(1)
