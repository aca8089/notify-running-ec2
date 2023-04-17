import boto3
import os
from datetime import datetime, timedelta

def lambda_handler(event, context):
    # Set up SNS client
    sns = boto3.client('sns')
    # Set up EC2 client
    ec2 = boto3.client('ec2')
    
    # Read project and environment from environment variables
    component   = os.environ['Component']
    environment = os.environ['Environment']
    topicarn    = os.environ['TopicARN']
    
    # get the current time in UTC
    now_utc = datetime.utcnow()

    # calculate the UTC offset for IST
    utc_offset = timedelta(hours=2, minutes=23)
    
    # add the UTC offset to the current UTC time
    now_ist = now_utc + utc_offset
    
    # format the IST datetime string
    ist_format = '%Y-%m-%d %H:%M IST'
    ist_str = now_ist.strftime(ist_format)
        
    # Get list of running instances
    filters = [{'Name': 'instance-state-name', 'Values': ['running']}]
    instances = ec2.describe_instances(Filters=filters)

    # Prepare email content
    subject = f'List of running EC2 instances in {component} {environment}- {ist_str}'
    body = f'Hi, \n\nThe following instances are currently running in AWS {component} {environment}:\n\n'
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            for tag in instance['Tags']:
                if tag['Key'] == 'Name':
                    body += 'Instance Name: ' + tag['Value'] + '\n'
                    body += 'Instance Id: ' + instance['InstanceId'] + '\n'
                    body += 'Instance Type: ' + instance['InstanceType'] + '\n\n'

    # Publish email to SNS topic
    response = sns.publish(
        TopicArn=topicarn,
        Message=body,
        Subject=subject
    )

    return "Email sent with response: {}".format(response)
