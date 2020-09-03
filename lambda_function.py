import json
import boto3
import botocore
import PIL
import io
from PIL import Image
from io import BytesIO


def resize_image(src_bucket, des_bucket, object_key, setwidth=4000, change_key_in_des_bucket=None):
    s3 = boto3.client('s3')
    in_mem_file = BytesIO()
    file_byte_string = s3.get_object(Bucket=src_bucket, Key=object_key)['Body'].read()
    with Image.open(BytesIO(file_byte_string)) as image:
        wpercent = (setwidth / float(image.size[0]))
        hsize = int((float(image.size[1]) * float(wpercent)))
        image_type = image.format
        image = image.resize((setwidth, hsize), Image.ANTIALIAS)
        image.save(in_mem_file, format=image_type)
    in_mem_file.seek(0)
    if isinstance(change_key_in_des_bucket, str):
        object_key = object_key.replace(object_key.split('/')[0], change_key_in_des_bucket)
    s3.put_object(Body=in_mem_file, Bucket=des_bucket, Key=object_key)
    in_mem_file.close()


def lambda_handler(event, context=None):
    for s3_json_data in event['Records']:
        BUCKET_NAME = s3_json_data['s3']['bucket']['name']
        KEY = s3_json_data['s3']['object']['key']
        KEY = KEY.replace("+", " ")
        print(BUCKET_NAME)
        print(KEY)
        resize_image(BUCKET_NAME, BUCKET_NAME, KEY, change_key_in_des_bucket='resized_image_test')
    return {
        'statusCode': 200,
        'bucket_name': BUCKET_NAME,
        'key': KEY,
        'body': json.dumps('S3 image resize done!')
    }
