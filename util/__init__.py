import json
import boto3

REGION='us-east-2'
ARN="arn:aws:sns:us-east-2:011002865179:smx-critical-alarm-triggered2"

awsconf="/home/ubuntu/.aws/config"
lines = [line.rstrip('\n') for line in open(awsconf)]
key1=lines[1].split('=')[1]
key2=lines[2].split('=')[1]

def send_aws_sns(message, region=REGION, arn=ARN):
    """
    Send json message
    :param message: to be sent
    :param region: the ARN region
    :param are: the SNS topic
    :return: AWS response
    """
    client = boto3.client('sns', region_name=region,
            aws_access_key_id=key1,
            aws_secret_access_key=key2)
    response = client.publish(
        TargetArn=arn,
        Message=json.dumps({'default': json.dumps(message)}),
        MessageStructure='json'
        )
    return response






