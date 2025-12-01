import json
import requests
import os

def lambda_handler(event, context):
    """
    AWS Lambda function to fetch weather and post to Home Assistant
    """
    try:
        # Get weather data
        weather_data = get_weather()
        
        # Post to Home Assistant
        send_to_homeassistant(weather_data)
        
        return {
            'statusCode': 200,
            'body': json.dumps('Weather updated successfully')
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }

def get_weather():
    """Fetch weather from National Weather Service API"""
    # Normal, IL coordinates
    lat, lon = 40.5142, -88.9906
    
    # Get forecast URL from NWS
    point_url = f"https://api.weather.gov/points/{lat},{lon}"
    point_response = requests.get(point_url)
    point_data = point_response.json()
    
    # Get actual forecast
    forecast_url = point_data['properties']['forecast']
    forecast_response = requests.get(forecast_url)
    forecast_data = forecast_response.json()
    
    # Get today's forecast (first period)
    today = forecast_data['properties']['periods'][0]
    
    return {
        'name': today['name'],
        'temperature': today['temperature'],
        'temperatureUnit': today['temperatureUnit'],
        'shortForecast': today['shortForecast'],
        'detailedForecast': today['detailedForecast']
    }

def send_to_homeassistant(weather_data):
    """Send weather data to Home Assistant webhook"""
    ha_webhook_url = os.environ.get('HA_WEBHOOK_URL')
    
    if not ha_webhook_url:
        raise Exception("HA_WEBHOOK_URL environment variable not set")
    
    payload = {
        'temperature': f"{weather_data['temperature']}°{weather_data['temperatureUnit']}",
        'conditions': weather_data['shortForecast'],
        'detailed': weather_data['detailedForecast'],
        'period': weather_data['name']
    }
    
    response = requests.post(ha_webhook_url, json=payload)
    response.raise_for_status()
    
    print(f"Sent to Home Assistant: {payload}")