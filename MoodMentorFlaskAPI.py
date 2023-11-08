import cv2
import pickle
from flask import Flask, request, jsonify
import subprocess
import requests
import os
import boto3
import botocore

app = Flask(__name__)
s3 = boto3.client('s3')

def download_file_from_s3(bucket_name, s3_key, local_path):
    try:
        s3.download_file(bucket_name, s3_key, local_path)
    except botocore.exceptions.NoCredentialsError:
        return f"S3 credentials not found for {s3_key}"
    except botocore.exceptions.ClientError as e:
        return f"Error downloading dataset from S3: {str(e)}"
    return None

def convert_image_format(image_data):
    # Assuming the image data is in a format like JPEG
    # Convert the image to OpenCV's format (BGR)
    img = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
    return img

@app.route('/recognize', methods=['POST'])
def recognize_face():
    # Download necessary files from S3
    s3_bucket_name = 'facial-login-model-bucket'
    s3_trainer_yml_key = 'trainer/trainer.yml'
    s3_cascade_xml_key = 'haarcascade_frontalface_default.xml'
    s3_names_pkl_key = 'names.pkl'

    trainer_yml_error = download_file_from_s3(s3_bucket_name, s3_trainer_yml_key, 'trainer.yml')
    cascade_xml_error = download_file_from_s3(s3_bucket_name, s3_cascade_xml_key, 'haarcascade_frontalface_default.xml')
    names_pkl_error = download_file_from_s3(s3_bucket_name, s3_names_pkl_key, 'names.pkl')

    if trainer_yml_error:
        return {"error": trainer_yml_error}
    if cascade_xml_error:
        return {"error": cascade_xml_error}
    if names_pkl_error:
        return {"error": names_pkl_error}

    # Check if required files exist
    if not os.path.isfile('trainer.yml') or not os.path.isfile('haarcascade_frontalface_default.xml') or not os.path.isfile('names.pkl'):
        return jsonify({"error": "Missing required files for recognition"})

    # Load downloaded files
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('trainer.yml')
    cascadePath = 'haarcascade_frontalface_default.xml'
    faceCascade = cv2.CascadeClassifier(cascadePath)

    font = cv2.FONT_HERSHEY_SIMPLEX

    # Process images received from the Flutter app
    images = request.files.getlist('images')

    recognition_results = []  # Initialize a list to store recognition results

    minW, minH = 64, 48  # Define appropriate values

    try:
        for image in images:
            # Check if the received file is a valid image (e.g., JPEG)
            if not image.content_type.startswith('image'):
                return jsonify({"error": "Invalid image format received"})

            # Check the file size
            if len(image.read()) < 80:  # Adjust the size threshold as needed
                return jsonify({"error": "Image file size is too small"})

            img = convert_image_format(image.read())
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            faces = faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.1,  # Adjust scaleFactor as needed
                minNeighbors=3,    # Adjust minNeighbors as needed
                minSize=(int(minW), int(minH)),
            )

            for (x, y, w, h) in faces:
                id, confidence = recognizer.predict(gray[y:y + h, x:x + w])

                result = {
                    "face_id": id,
                    "confidence": confidence
                }
                recognition_results.append(result)
    except Exception as e:
        print(f"Error during recognition: {str(e)}")
        return jsonify({"error": str(e)})

    # Check if any faces were recognized
    if recognition_results:
        return jsonify(recognition_results)
    else:
        return jsonify({"error": "No faces detected in the image"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
