#Sharan Karthikeyan
# This code is an AWS Lambda function written in python. It runs automatically when a .png file is put into an S3 bucket.
# Its purpose is to use AWS textract on the .png file to extract its text, and then writes its content into a .txt file and stores it in another S3 bucket.

import json
import boto3
import os
import urllib.parse

print('Loading function')

s3 = boto3.client('s3')

# Amazon Textract client
textract = boto3.client('textract')

#function to extract the text from a png file stored in an S3 bucket
def getTextractData(bucketName, documentKey):
    print('Loading getTextractData')
    # Calls Amazon Textract
    response = textract.detect_document_text(Document={'S3Object': {'Bucket': bucketName,'Name': documentKey}})
        
    detectedText = ''

    # Print detected text
    for item in response['Blocks']:
        if item['BlockType'] == 'LINE':
            detectedText += item['Text'] + '\n'
            
    return detectedText
    
#function to write the contents of the textracted text into a txt file and store it into an S3 bucket
def writeTextractToS3File(textractData, bucketName, createdS3Document):
    print('Loading writeTextractToS3File')
    generateFilePath = os.path.splitext(createdS3Document)[0] + '.txt'
    s3.put_object(Body=textractData, Bucket=bucketName, Key=generateFilePath)
    print('Generated ' + generateFilePath)
    
#this runs when the lambda event is triggered. This event is a .png file being put into the specified S3 bucket
def lambda_handler(event, context):
    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        detectedText = getTextractData(bucket, key)
        writeTextractToS3File(detectedText, 'textract-fda', key)
                
        return 'Processing Done!'

    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e