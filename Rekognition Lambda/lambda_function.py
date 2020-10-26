import json
import boto3
import botocore
import PIL
import io
import os
from PIL import Image, ImageFont, ImageDraw, ImageEnhance


font = ImageFont.truetype("arial.ttf", 50)

rekognition_arn = 'arn:aws:rekognition:us-west-2:802916938025:project/ksa-megaton-objectdetection-merge-testdata/version/ksa-megaton-objectdetection-merge-testdata.2020-10-08T16.06.46/1602140806876'
bucket_name = 'mgt-web-data'


def lambda_handler(event, context):
    object_key = event['originalS3Path']

    s3 = boto3.client('s3', region_name='ap-northeast-2')
    rekognition = boto3.client('rekognition', region_name='us-west-2')

    source_img = s3.get_object(Bucket=bucket_name, Key=object_key)['Body'].read()
    response = rekognition.detect_custom_labels(
        ProjectVersionArn=rekognition_arn,
        Image={
            'Bytes': source_img
        },
        MaxResults=6,
    )
    source_img = Image.open(io.BytesIO(source_img))

    for labels in response['CustomLabels']:
        draw = ImageDraw.Draw(source_img)

        x = int(labels['Geometry']['BoundingBox']['Left'] * source_img.size[0])
        y = int(labels['Geometry']['BoundingBox']['Top'] * source_img.size[1])
        x_right = int(x + labels['Geometry']['BoundingBox']['Width'] * source_img.size[0])
        y_right = int(y + labels['Geometry']['BoundingBox']['Height'] * source_img.size[1])

        draw.rectangle(((x, y), (x_right, y_right)), outline='red', width=5)
        draw.text((x, int(y + (y_right - y) / 3)), labels['Name'], font=font)

    in_mem_file = io.BytesIO()
    source_img.save(in_mem_file, format=source_img.format)
    in_mem_file.seek(0)

    s3.put_object(Body=in_mem_file, Bucket=bucket_name, Key=event['saveS3Path'])
    return {
        'statusCode': 200,
        'saveS3Path': event['saveS3Path'],
        'result': json.dumps(response)
    }