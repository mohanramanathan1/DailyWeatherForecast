# DailyWeatherForecast
An AWS Lambda function that automatically fetches 7-day weather forecasts from the National Weather Service and delivers them via Telegram bot three times daily with time-appropriate content.
Overview
This project automates weather updates for Normal, Illinois by:

Fetching 7-day forecast data from the National Weather Service API
Formatting different content based on time of day (morning, noon, evening)
Sending notifications through a Telegram bot
Running automatically 3 times daily using AWS EventBridge

Architecture
AWS Services Used

AWS Lambda: Hosts the Python function that fetches and sends weather data
Amazon EventBridge: Three separate schedules for different times of day:

6:00 AM Central: Full 7-day forecast overview
12:00 PM Central: Detailed today + tonight update
9:00 PM Central: Detailed tonight + tomorrow update


AWS Systems Manager Parameter Store: Securely stores Telegram bot credentials (encrypted)
AWS IAM: Manages permissions with least-privilege access policy

External APIs

National Weather Service API: Free, government-provided weather data for US locations
Telegram Bot API: Delivers formatted weather messages to users

Security Features

No hardcoded secrets in code or repository
Credentials stored in SSM Parameter Store with encryption
Custom IAM policy granting minimal required permissions
Private GitHub repository

Data Flow
EventBridge Rule (6 AM)  ──┐
EventBridge Rule (12 PM) ──┼─→ Lambda Function ──→ NWS API ──→ Format Message ──→ Telegram Bot
EventBridge Rule (9 PM)  ──┘           ↓
                                  SSM Parameter Store
                                  (secure credentials)
Technologies

Language: Python 3.x
APIs: National Weather Service, Telegram Bot API
Cloud Provider: AWS
Infrastructure: Lambda, EventBridge (3 scheduled rules), SSM Parameter Store
Version Control: Git/GitHub

Requirements
requests
boto3
See requirements.txt for full dependencies.
Note: Earlier versions used pytz for timezone detection, but the current implementation uses EventBridge to pass the time of day via JSON input, eliminating this dependency.
Setup Instructions
Prerequisites

AWS account with Lambda, EventBridge, and SSM access
Telegram bot token (create via BotFather)
Telegram chat ID

Deployment Steps

Create SSM Parameters (store secrets securely):

bashaws ssm put-parameter \
    --name "/weather-bot/telegram-token" \
    --value "YOUR_BOT_TOKEN" \
    --type "SecureString" \
    --region us-east-1

aws ssm put-parameter \
    --name "/weather-bot/telegram-chat-id" \
    --value "YOUR_CHAT_ID" \
    --type "String" \
    --region us-east-1

Create IAM Role for Lambda with this inline policy:

json{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": ["ssm:GetParameter"],
            "Resource": [
                "arn:aws:ssm:us-east-1:YOUR_ACCOUNT_ID:parameter/weather-bot/telegram-token",
                "arn:aws:ssm:us-east-1:YOUR_ACCOUNT_ID:parameter/weather-bot/telegram-chat-id"
            ]
        }
    ]
}

Deploy Lambda Function:

Upload lambda_function.py and dependencies
Set runtime to Python 3.x
Attach the IAM role created above
Set timeout to 10 seconds
Configure 128 MB memory (adequate for this workload)


Create EventBridge Rules (3 separate rules):

Morning Rule (6 AM):

Name: DailyWeatherTrigger
Schedule: cron(0 12 * * ? *) (6 AM Central = 12:00 UTC)
Target: Your Lambda function
Constant JSON input: {"message_type": "morning"}

Noon Rule (12 PM):

Name: WeatherForecast-Noon
Schedule: cron(0 18 * * ? *) (12 PM Central = 18:00 UTC)
Target: Your Lambda function
Constant JSON input: {"message_type": "noon"}

Evening Rule (9 PM):

Name: WeatherForecast-Evening
Schedule: cron(0 2 * * ? *) (9 PM Central = 02:00 UTC next day)
Target: Your Lambda function
Constant JSON input: {"message_type": "evening"}

Note: Adjust UTC times based on Daylight Saving Time if needed.

Test:

Manually invoke Lambda with test event: {"message_type": "morning"}
Check Telegram for weather message
Verify CloudWatch Logs for successful execution



Current Features
✅ 7-Day Weather Forecast - Full week outlook with day/night periods
✅ Three Daily Updates - Morning (6 AM), Noon (12 PM), Evening (9 PM) Central Time
✅ Time-Appropriate Content:

Morning (6 AM): Comprehensive 7-day overview with brief conditions
Noon (12 PM): Detailed update for rest of today + tonight
Evening (9 PM): Detailed update for tonight + tomorrow
✅ Location: Normal, Illinois
✅ Data Source: National Weather Service (NOAA) - official government forecasts
✅ Telegram Integration: Formatted messages with emojis and Markdown
✅ Secure Credential Management: SSM Parameter Store with encryption
✅ Cost Efficient: Free tier eligible, ~90 Lambda invocations/month
✅ Automated Scheduling: EventBridge rules trigger at specific times

Message Formats
Morning Update (6:00 AM)
Provides a high-level overview of the entire week ahead with temperature and brief conditions for each period:
🌅 Good Morning! 7-Day Weather Forecast for Normal, IL

Today
🌡️ 45°F - Sunny

Tonight
🌡️ 32°F - Clear

Wednesday
🌡️ 50°F - Partly Cloudy
...
Noon Update (12:00 PM)
Focuses on the immediate future with detailed forecasts:
☀️ Midday Weather Update for Normal, IL

This Afternoon
🌡️ 45°F
Sunny

High near 45. Northwest wind 10 to 15 mph...

Tonight
🌡️ 32°F
Clear
...
Evening Update (9:00 PM)
Prepares you for overnight and the next day:
🌙 Evening Weather Update for Normal, IL

Tonight
🌡️ 32°F
Clear

Low around 32. Light wind...

Thursday
🌡️ 48°F
Mostly Sunny
...
Planned Enhancements
🔄 Step Functions Integration: Add retry logic and failure handling
🔄 Email Alerts: SES integration for failure notifications
🔄 Infrastructure as Code: Complete Terraform configuration for repeatable deployments
🔄 Multi-Location Support: Configuration for multiple cities
🔄 Severe Weather Alerts: Special notifications for weather warnings
🔄 Historical Data Logging: Store forecasts in DynamoDB for accuracy tracking
Cost Analysis
This project runs within AWS Free Tier limits:

Lambda: ~90 invocations/month (3 per day × 30 days), ~3 seconds each = FREE (well under 1M requests/month free tier)
EventBridge: Schedule rules are FREE
SSM Parameter Store: Standard parameters are FREE
Data Transfer: Minimal outbound data to Telegram API = FREE (under 1 GB/month)
Total Monthly Cost: $0.00

Scaling Considerations: Even with 10x the current usage (30 invocations/day), costs would remain under $1/month.
Project Background
Built as a learning project to practice:

AWS Lambda development and deployment
Secure secrets management
API integration (REST APIs)
Scheduled automation with EventBridge
Python development for cloud functions
Infrastructure security best practices

Lessons Learned

Security First: Moving from environment variables to SSM Parameter Store significantly improved credential security
Git History Matters: Deleted sensitive data from repository history and created fresh repo with clean slate
Lambda Deployment Packages: Discovered that copying code to Lambda console doesn't install dependencies; either need deployment package or eliminate external dependencies
EventBridge JSON Input Pattern: Using EventBridge to pass parameters via JSON input is cleaner than timezone detection in Lambda code
Architecture Decisions: Sometimes simpler is better - three separate EventBridge rules are easier to manage than complex conditional logic
Free Tier Power: AWS free tier is generous enough for many personal automation projects
API Discovery: National Weather Service provides excellent free data for US locations

License
Personal project - not licensed for redistribution.
Author
Built by Mohan Ramanathan as part of ongoing AWS and cloud automation learning.
