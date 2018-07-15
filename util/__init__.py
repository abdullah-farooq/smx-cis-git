import json
import boto3

REGION='us-east-2'
ARN="arn:aws:sns:us-east-2:011002865179:smx-critical-alarm-triggered2"

def send_aws_sns(message, region=REGION, arn=ARN):
    """
    Send json message
    :param message: to be sent
    :param region: the ARN region
    :param are: the SNS topic
    :return: AWS response
    """
    client = boto3.client('sns', region_name=region)
    response = client.publish(
        TargetArn=arn,
        Message=json.dumps({'default': json.dumps(message)}),
        MessageStructure='json'
        )
    return response






