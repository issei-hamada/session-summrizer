# README

S3 バケット(tempbucket)に配置したトランスクリプト(.txt)を要約し、別バケット(target)に出力する。

## 事前準備

- Claude 3.5 sonnet を有効化する

## デプロイ

1. AWS SAM にてデプロイ
   > sam deploy --guided
2. TempBucket に S3 イベントを設定
   SQSキューをターゲットに設定
