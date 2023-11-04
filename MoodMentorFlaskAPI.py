from flask import Flask, request, jsonify
import cv2
import numpy as np
import pickle
import os
import boto3

app = Flask(__name__)
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

@app.route('/', methods=['POST'])
def faceRecognition():
    # Check if the request contains an image file
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    image = request.files['image'].read()
    image_array = np.fromstring(image, np.uint8)
    img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    # Initialize S3 client
    s3 = boto3.client('s3')

    # Specify the S3 bucket name
    bucket_name = 'facial-login-model-bucket'  # Replace with your S3 bucket name

    # Download the Haar Cascade XML file from S3
    haarcascade_file_key = 's3://facial-login-model-bucket/haarcascade_frontalface_default.xml'
    s3.download_file(bucket_name, haarcascade_file_key, 'haarcascade_frontalface_default.xml')

    # Load the Haar Cascade XML file
    faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    # Download the 'names.pkl' file from S3
    names_file_key = 's3://facial-login-model-bucket/names.pkl'
    s3.download_file(bucket_name, names_file_key, 'names.pkl')

    # Load the 'names.pkl' file
    with open('names.pkl', 'rb') as f:
        names = pickle.load(f)

    recognizer = cv2.face_LBPHFaceRecognizer.create()
    model_file_key = 's3://facial-login-model-bucket/trainer/trainer.yml'
    s3.download_file(bucket_name, model_file_key, 'trainer.yml')
    recognizer.read('trainer.yml')

    font = cv2.FONT_HERSHEY_SIMPLEX

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(30, 30),
    )

    results = []

    for (x, y, w, h) in faces:
        id, confidence = recognizer.predict(gray[y:y + h, x:x + w])

        if confidence < 100:
            if id >= 0 and id < len(names):
                id = names[id]
                confidence = round(100 - confidence)
            else:
                id = "unknown"
                confidence = round(100 - confidence)
        else:
            id = "unknown"
            confidence = 0

        results.append({'id': id, 'confidence': confidence})

    return jsonify(results)

if __name__ == '__main':
    app.run(host='0.0.0.0', port=80, debug=True)
