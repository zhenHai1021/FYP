from flask import Flask, request, jsonify
from urllib.parse import urlparse 
import subprocess
import requests
import json
import os
import boto3
import subprocess
import botocore
import sys
import cv2
import numpy as np
import pickle

app = Flask(__name__)
s3 = boto3.client('s3')
 # Modify this path if necessary

@app.route('/hello_world', methods=['POST'])
def hello_world():
    try:
        S3_PUBLIC_URL = 'https://facial-login-model-bucket.s3.amazonaws.com/hello_world.py'  # Replace with your S3 bucket URL

        # Define the full path to the Python interpreter
        PYTHON_PATH = '/usr/bin/python3' 
        # Fetch the 'hello_world.py' script from the public S3 URL
        s3_script = requests.get(S3_PUBLIC_URL)
        
        if s3_script.status_code == 200:
            with open('/tmp/hello_world.py', 'wb') as f:
                f.write(s3_script.content)
            
            # Use the full path to the Python interpreter
            result = subprocess.check_output([PYTHON_PATH, '/tmp/hello_world.py'], stderr=subprocess.STDOUT, text=True)
            
            return jsonify({'result': result})
        else:
            return jsonify({'error': f"Failed to fetch 'hello_world.py' from S3: {s3_script.status_code}"})
    except Exception as e:
        return jsonify({'error': str(e)})


def download_file_from_s3(bucket_name, s3_key, local_path):
    s3 = boto3.client('s3')
    try:
        s3.download_file(bucket_name, s3_key, local_path)
    except botocore.exceptions.NoCredentialsError:
        return f"S3 credentials not found for {s3_key}"
    except botocore.exceptions.ClientError as e:
        return f"Error downloading file from S3: {str(e)}"
    return None


@app.route('/recognize', methods=['POST'])
def recognize_face():
    def download_file_from_s3(bucket_name, s3_key, local_path):
  
    try:
        s3.download_file(bucket_name, s3_key, local_path)
    except botocore.exceptions.NoCredentialsError:
        return f"S3 credentials not found for {s3_key}"
    except botocore.exceptions.ClientError as e:
        return f"Error downloading file from S3: {str(e)}"
    return None
    

    # Download necessary files from S3
    s3_bucket_name = 'facial-login-model-bucket'
    s3_trainer_yml_key = 's3://facial-login-model-bucket/trainer/trainer.yml'
    s3_cascade_xml_key = 's3://facial-login-model-bucket/haarcascade_frontalface_default.xml'
    s3_names_pkl_key = 's3://facial-login-model-bucket/names.pkl'

    trainer_yml_error = download_file_from_s3(s3_bucket_name, s3_trainer_yml_key, 'trainer.yml')
    cascade_xml_error = download_file_from_s3(s3_bucket_name, s3_cascade_xml_key, 'haarcascade_frontalface_default.xml')
    names_pkl_error = download_file_from_s3(s3_bucket_name, s3_names_pkl_key, 'names.pkl')

    if trainer_yml_error:
        return [{"error": trainer_yml_error}]
    if cascade_xml_error:
        return [{"error": cascade_xml_error}]
    if names_pkl_error:
        return [{"error": names_pkl_error}]

    # Load downloaded files
    recognizer = cv2.face_LBPHFaceRecognizer.create()
    recognizer.read('trainer.yml')
    cascadePath = 'haarcascade_frontalface_default.xml'
    faceCascade = cv2.CascadeClassifier(cascadePath)

    font = cv2.FONT_HERSHEY_SIMPLEX

    cam = cv2.VideoCapture(0)  # Access the default camera (phone's camera)
    cam.set(3, 640)  # Set video width
    cam.set(4, 480)  # Set video height

    minW = 0.1 * cam.get(3)
    minH = 0.1 * cam.get(4)

    with open('names.pkl', 'rb') as f:
        names = pickle.load(f)

    recognition_results = []  # Initialize a list to store recognition results

    while True:
        ret, img = cam.read()

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(int(minW), int(minH)),
        )

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

            id, confidence = recognizer.predict(gray[y:y + h, x:x + w])

            if confidence < 100:
                if id >= 0 and id < len(names):
                    id = names[id]
                    confidence = round(100 - confidence)  # Remove the '%' symbol
                else:
                    id = "unknown"
                    confidence = round(100 - confidence)  # Remove the '%' symbol
            else:
                id = "unknown"
                confidence = 0  # Set confidence to 0 for unrecognized faces

            result = {
                "name": id,
                "confidence": confidence
            }
            recognition_results.append(result)

            cv2.putText(img, str(id), (x + 5, y - 5), font, 1, (255, 255, 255), 2)
            cv2.putText(img, str(confidence), (x + 5, y + h - 5), font, 1, (255, 255, 0), 1)

        cv2.imshow('camera', img)

        k = cv2.waitKey(10) & 0xff
        if k == 27:
            break

    return recognition_results

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
