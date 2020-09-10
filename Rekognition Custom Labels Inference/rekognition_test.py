import json
import boto3
import botocore
import PIL
import io
import os
from PIL import Image, ImageFont, ImageDraw, ImageEnhance
from io import BytesIO

aws_region = 'us-west-2'

font = ImageFont.truetype("arial.ttf", 50)

foldername =
save_path_local =
image_path_local =

rekognition_arn =
bucket_name =
bucket_key = 

s3 = boto3.client('s3', region_name=aws_region)
rekognition = boto3.client('rekognition', region_name=aws_region)
paginator = s3.get_paginator('list_objects_v2')
pages = paginator.paginate(Bucket=bucket_name, Prefix=bucket_key)

object_key_list = [x['Key'] for page in pages for x in page['Contents']]

for object_key in object_key_list:
    filename = object_key.split('/')[-1]
    source_img = Image.open(os.path.join(image_path_local, filename))
    response = rekognition.detect_custom_labels(
        ProjectVersionArn=rekognition_arn,
        Image={
            'S3Object': {
                'Bucket': bucket_name,
                'Name': object_key,
            }
        },
        MaxResults=6,
    )

    with open(os.path.join(save_path_local, filename.split('.')[0]+'.json'), "w") as json_file:
        json.dump(response, json_file)

    for labels in response['CustomLabels']:
        draw = ImageDraw.Draw(source_img)

        x = int(labels['Geometry']['BoundingBox']['Left'] * source_img.size[0])
        y = int(labels['Geometry']['BoundingBox']['Top'] * source_img.size[1])
        x_right = int(x + labels['Geometry']['BoundingBox']['Width'] * source_img.size[0])
        y_right = int(y + labels['Geometry']['BoundingBox']['Height'] * source_img.size[1])

        draw.rectangle(((x, y), (x_right, y_right)), outline='red', width=5)
        draw.text((x, int(y + (y_right - y) / 3)), labels['Name'], font=font)

    source_img.save(os.path.join(save_path_local, filename), "JPEG")


