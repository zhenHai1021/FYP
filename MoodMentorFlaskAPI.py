import boto3
import cv2
import numpy as np
import pickle
import os
from flask import Flask, jsonify

app = Flask(__name__)
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

def download_file_from_s3(bucket, key, local_path):
    try:
        s3.download_file(bucket, key, local_path)
        print(f"Downloaded {key} from S3")
    except Exception as e:
        print(f"An error occurred while downloading {key} from S3: {str(e)}")

@app.route('/', methods=['GET', 'POST'])
def faceRecognition():
    # Initialize S3 client
    s3 = boto3.client('s3')

    # Specify the S3 bucket name
    bucket_name = 'facial-login-model-bucket'  # Replace with your S3 bucket name

    # Download the Haar Cascade XML file from S3
    haarcascade_file_key = 'haarcascade_frontalface_default.xml'
    download_file_from_s3(bucket_name, haarcascade_file_key, 'haarcascade_frontalface_default.xml')

    # Load the Haar Cascade XML file
    faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    # Download the 'names.pkl' file from S3
    names_file_key = 'names.pkl'
    download_file_from_s3(bucket_name, names_file_key, 'names.pkl')

    # Load the 'names.pkl' file
    with open('names.pkl', 'rb') as f:
        names = pickle.load(f)

    # Rest of your code...

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
