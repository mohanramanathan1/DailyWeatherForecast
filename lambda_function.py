import json
import requests
import boto3

# Initialize SSM client outside handler for Lambda optimization
ssm = boto3.client('ssm', region_name='us-east-1')

def lambda_handler(event, context):
    """
    AWS Lambda function to fetch weather and post to Telegram
    """
    try:
        # Get weather data
        weather_data = get_weather()
        
        # Send to Telegram
        send_to_telegram(weather_data)
        
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

def send_to_telegram(weather_data):
    """Send weather data to Telegram"""
    # Fetch secrets from SSM Parameter Store
    bot_token = get_parameter('/weather-bot/telegram-token')
    chat_id = get_parameter('/weather-bot/telegram-chat-id')
    
    # Format message
    message = f"""🌤 *{weather_data['name']} Weather for Normal, IL*

Temperature: {weather_data['temperature']}°{weather_data['temperatureUnit']}
Conditions: {weather_data['shortForecast']}

{weather_data['detailedForecast']}
"""
    
    # Send to Telegram
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }
    
    response = requests.post(url, json=payload)
    response.raise_for_status()
    
    print(f"Sent to Telegram: {weather_data['shortForecast']}")

def get_parameter(parameter_name):
    """Fetch parameter from SSM Parameter Store"""
    response = ssm.get_parameter(
        Name=parameter_name,
        WithDecryption=True
    )
    return response['Parameter']['Value']