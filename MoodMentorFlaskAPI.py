from flask import Flask, request, jsonify
import cv2
import numpy as np
import pickle
import requests

app = Flask(__name__)

# Function to download files from URLs and save them locally
def download_file_from_url(url, local_path):
    response = requests.get(url)
    with open(local_path, 'wb') as f:
        f.write(response.content)

# URLs for model files
trainer_url = 'https://facial-login-model-bucket.s3.amazonaws.com/trainer/trainer.yml'
cascade_url = 'https://facial-login-model-bucket.s3.amazonaws.com/haarcascade_frontalface_default.xml'
names_url = 'https://facial-login-model-bucket.s3.amazonaws.com/names.pkl'

# Paths to save the downloaded files
trainer_path = 'trainer.yml'
cascade_path = 'haarcascade_frontalface_default.xml'
names_path = 'names.pkl'

# Download the model files
download_file_from_url(trainer_url, trainer_path)
download_file_from_url(cascade_url, cascade_path)
download_file_from_url(names_url, names_path)

# Load the trained recognizer and cascade classifier
recognizer = cv2.face_LBPHFaceRecognizer_create()
recognizer.read(trainer_path)
faceCascade = cv2.CascadeClassifier(cascade_path)

# Load the names of recognized individuals
with open(names_path, 'rb') as f:
    names = pickle.load(f)

@app.route('/facialLogin', methods=['POST'])
def faceRecognition():
    if 'frame' not in request.files:
        return jsonify({'result': 'No frame data received'}), 400

    frame_data = request.files['frame'].read()
    frame = np.frombuffer(frame_data, dtype=np.uint8)
    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(30, 30),
    )

    for (x, y, w, h) in faces:
        id, confidence = recognizer.predict(gray[y:y + h, x:x + w])

        if confidence < 100:
            if id >= 0 and id < len(names):
                id = names[id]
                confidence = round(100 - confidence, 2)
            else:
                id = "unknown"
                confidence = round(100 - confidence, 2)
            return jsonify({'result': f'Authenticated as {id} with confidence {confidence}%'})

    return jsonify({'result': 'Authentication failed'})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
