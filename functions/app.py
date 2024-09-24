from logging import getLogger, INFO, Formatter
import json
import os
import string
import time

import boto3
import botocore
from botocore.config import Config

logger = getLogger()
logger.setLevel(INFO)
formatter = Formatter(
    '[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(funcName)s\t%(message)s\n',
    '%Y-%m-%dT%H:%M:%S'
)

config = Config(read_timeout=1000)

# オブジェクト取得
def get_object(bucket_name, object_key, local_path):
    # ディレクトリの作成（存在しない場合）
    local_dir = os.path.dirname(local_path)
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
        logger.info(f'Created directory: {local_dir}')

    client = boto3.client('s3')
    client.download_file(bucket_name, object_key, local_path)

# ファイルを開く
def open_file(file_path):
    with open(file_path, "r") as f:
        data = f.read()
    return data

# LLM 実行
def invoke_model(document, file_path):
    # プロンプト生成
    system_prompt = open_file("./template/system.template")
    logger.info(f'{system_prompt=}')

    message_template = string.Template(open_file("./template/message.template"))
    message_prompt = message_template.safe_substitute(document=document)
    logger.info(f'{message_prompt=}')
    prompt = [{'role': 'user', 'content': message_prompt}]

    # invoke
    bedrock_runtime = boto3.client(service_name='bedrock-runtime', region_name=os.environ['REGION_CONFIG'], config=config)
    body=json.dumps(
        {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": int(os.environ['MAX_TOKENS']),
            "system": system_prompt,
            "messages": prompt
        }  
    )
    max_retries = 5
    initial_delay = 1
    for i in range(max_retries):
        try:
            response = bedrock_runtime.invoke_model(body=body, modelId=os.environ['SONNET_ID'])
            response_body = json.loads(response.get('body').read())
            logger.info(f'{response_body=}')
    
            # ファイル書き込み
            response_text = response_body['content'][0]['text']
            new_file_path = os.path.splitext(file_path)[0] + '.md'
            with open(new_file_path, mode="w") as f:
                f.write(response_text)
        
            return new_file_path
        except botocore.exceptions.ClientError as e:
            # If the call failed due to a transient error, retry with exponential backoff
            if e.response['Error']['Code'] in ['ThrottlingException', 'TooManyRequestsException', 'RequestLimitExceeded']:
                print(f"Request failed with error {e.response['Error']['Code']}. Retrying...")
                
                delay = initial_delay * (2 ** i)
                time.sleep(delay)
                
                continue
            
            # If the call failed due to a permanent error, raise an exception
            raise e
    
    # If all retries failed, raise an exception
    raise Exception(f"Request failed after {max_retries} attempts")

# object を保存
def upload_object(file_path, bucket_name):
    client = boto3.client('s3')
    # オブジェクト保存時、file_pathの先頭から/tmp/を削る必要がある
    client.upload_file(file_path, bucket_name, file_path[5:])


def lambda_handler(event, context):
    logger.info(f'{event=}')
    body = json.loads(event['Records'][0]['body'])

    # バケット名とキーを取得
    bucket_name = body['Records'][0]['s3']['bucket']['name']
    logger.info(f'{bucket_name=}')
    object_key = body['Records'][0]['s3']['object']['key']
    logger.info(f'{object_key=}')
    local_path = f'/tmp/{object_key}'

    # オブジェクトを取得
    get_object(bucket_name, object_key, local_path)
    
    # ドキュメントを取得
    document = open_file(local_path)
    
    # md 生成
    md_path = invoke_model(document, local_path)
    
    # オブジェクトをアップロード
    upload_object(md_path, os.environ['SOURCE_BUCKET'])
