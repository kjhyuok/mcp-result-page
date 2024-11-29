import boto3
import os
import json
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from botocore.exceptions import ClientError


def get_secret():
	secret_name = os.getenv('SLACK_TOKEN_SECRET')
	region_name = os.getenv('REGION')

	# Create a Secrets Manager client
	session = boto3.session.Session()
	client = session.client(
		service_name='secretsmanager',
		region_name=region_name
	)

	try:
		get_secret_value_response = client.get_secret_value(
			SecretId=secret_name
		)
	except ClientError as e:
		raise e

	secret_string = get_secret_value_response['SecretString']
	secret_dict = json.loads(secret_string)
	
	return secret_dict["slack_token"]


def lambda_handler(event, context):
	client = WebClient(token=get_secret())
	message_text = "our current user or role does not have access to Kubernetes objects on this EKS cluster."

	try:
		result = client.chat_postMessage(
			channel="bedrock-interactivity", 
			text=message_text,
			blocks=[
				{
					"type": "section",
					"block_id": "error_text",
					"text": {
						"type": "mrkdwn",
						"text": "*Error Message* : " + message_text
					}
				},
				{
					"type": "section",
					"text": {
						"type": "mrkdwn",
						"text": ">:robot_face: 아래 버튼을 클릭하면 LLM을 통해 정보를 검색합니다."
					}
				},
				{
					"type": "actions",
					"elements": [
						{
							"type": "button",
							"text": {
								"type": "plain_text",
								"emoji": True,
								"text": "Watch"
							},
							"style": "danger",
							"value": "click_watch"
						},
						{
							"type": "button",
							"text": {
								"type": "plain_text",
								"emoji": True,
								"text": "To bedrock agent"
							},
							"style": "primary",
							"value": "click_agent"
						},
						{
							"type": "button",
							"text": {
								"type": "plain_text",
								"emoji": True,
								"text": "Reporting"
							},
							"value": "click_reporting"
						}
					]
				}
			]
		)
		print(result)

	except SlackApiError as e:
		print(f"Error posting message: {e}")  

