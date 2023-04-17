import boto3
import os
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def lambda_handler(event, context):
    # AWS clients
    ec2 = boto3.client('ec2')
    ses = boto3.client('ses')
    
    # Read project and environment from environment variables
    project     = os.environ['project_name']
    environment = os.environ['environment_name']

    # Get running instances
    instances = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

    # Send email with instance name
    message = MIMEMultipart()
    message['Subject'] = f'Running EC2 instances in AWS {project} {environment}'
    message['From'] = 'from@example.com'
    message['To'] = 'to@example.com'

    text = f'Hi, \n\nThe following instances are currently running in AWS {project} {environment}:\n\n'
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            for tag in instance['Tags']:
                if tag['Key'] == 'Name':
                    text += 'Instance Name: ' + tag['Value'] + '\n'
                    text += 'Instance Id: ' + instance['InstanceId'] + '\n'
                    text += 'Instance Type: ' + instance['InstanceType'] + '\n\n'

    message.attach(MIMEText(text))

    response = ses.send_raw_email(RawMessage={'Data': message.as_string()})
    print('Email sent with message ID:', response['MessageId'])
