import json
import requests
import boto3

# Initialize SSM client outside handler for Lambda optimization
ssm = boto3.client('ssm', region_name='us-east-1')

def lambda_handler(event, context):
    """
    AWS Lambda function to fetch weather and post to Telegram
    Sends different content based on time of day:
    - morning: Full 7-day forecast (6 AM)
    - noon: Today + Tonight update (12 PM)
    - evening: Tonight + Tomorrow update (9 PM)
    
    EventBridge passes the message_type in the event
    """
    try:
        # Get all weather periods
        all_periods = get_weather()
        
        # Get message type from EventBridge event (default to morning for testing)
        message_type = event.get('message_type', 'morning')
        
        # Format the message based on time of day
        weather_message = format_message(all_periods, message_type)
        
        # Send to Telegram
        send_to_telegram(weather_message)
        
        return {
            'statusCode': 200,
            'body': json.dumps(f'Weather updated successfully - {message_type} message sent')
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
    
    # Get all forecast periods
    all_periods = forecast_data['properties']['periods']
    
    return all_periods

def format_message(periods, message_type):
    """Format weather message based on time of day"""
    
    if message_type == "morning":
        # 6 AM: Full 7-day forecast (brief format)
        message = "🌅 *Good Morning! 7-Day Weather Forecast for Normal, IL*\n\n"
        
        # Show first 14 periods (7 days × 2 periods per day)
        for period in periods[:14]:
            message += f"*{period['name']}*\n"
            message += f"🌡️ {period['temperature']}°{period['temperatureUnit']} - {period['shortForecast']}\n\n"
    
    elif message_type == "noon":
        # 12 PM: Today + Tonight (detailed format)
        message = "☀️ *Midday Weather Update for Normal, IL*\n\n"
        
        # Show just next 2 periods (rest of today + tonight)
        for period in periods[:2]:
            message += f"*{period['name']}*\n"
            message += f"🌡️ {period['temperature']}°{period['temperatureUnit']}\n"
            message += f"{period['shortForecast']}\n\n"
            message += f"_{period['detailedForecast']}_\n\n"
    
    elif message_type == "evening":
        # 9 PM: Tonight + Tomorrow (detailed format)
        message = "🌙 *Evening Weather Update for Normal, IL*\n\n"
        
        # Show next 3 periods (tonight + tomorrow day/night)
        for period in periods[:3]:
            message += f"*{period['name']}*\n"
            message += f"🌡️ {period['temperature']}°{period['temperatureUnit']}\n"
            message += f"{period['shortForecast']}\n\n"
            message += f"_{period['detailedForecast']}_\n\n"
    
    return message

def send_to_telegram(message):
    """Send pre-formatted message to Telegram"""
    # Fetch secrets from SSM Parameter Store
    bot_token = get_parameter('/weather-bot/telegram-token')
    chat_id = get_parameter('/weather-bot/telegram-chat-id')
    
    # Send to Telegram
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }
    
    response = requests.post(url, json=payload)
    response.raise_for_status()
    
    print(f"Successfully sent weather update to Telegram")

def get_parameter(parameter_name):
    """Fetch parameter from SSM Parameter Store"""
    response = ssm.get_parameter(
        Name=parameter_name,
        WithDecryption=True
    )
    return response['Parameter']['Value']


