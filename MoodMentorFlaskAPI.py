from flask import Flask
import cv2
import numpy as np
import pickle
import os
import boto3

app = Flask(__name__)
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

def download_file_from_s3(bucket, key, local_path):
    try:
        s3.download_file(bucket, key, local_path)
        print(f"Downloaded {key} from S3")
    except Exception as e:
        print(f"An error occurred while downloading {key} from S3: {str(e)}")


@app.route('/', methods=['POST', 'GET'])
def faceRecognition():
    try:
        print("Starting the face recognition process...")
        # Initialize S3 client
        s3 = boto3.client('s3')

        # Specify the S3 bucket name
        bucket_name = 'facial-login-model-bucket'  # Replace with your S3 bucket name

        faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

        # Load the Haar Cascade XML file
        print("Loading the Haar Cascade XML file...")
        faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

        # Download the 'names.pkl' file from S3
        names_file_key = 'names.pkl'
        download_file_from_s3(bucket_name, names_file_key, 'names.pkl')

         # Load the 'names.pkl' file
        with open('names.pkl', 'rb') as f:
            names = pickle.load(f)

        # Load the face recognition model
        recognizer = cv2.face_LBPHFaceRecognizer.create()
        model_file_key = 's3://facial-login-model-bucket/trainer/trainer.yml'
        print(f"Downloading face recognition model from {model_file_key}")
        s3.download_file(bucket_name, model_file_key, 'trainer.yml')
        recognizer.read('trainer.yml')

        font = cv2.FONT_HERSHEY_SIMPLEX

        total_cameras = 2
        current_camera = 0
        cam = cv2.VideoCapture(0)
        cam.set(3, 640)
        cam.set(4, 480)
        minW = 0.1 * cam.get(3)
        minH = 0.1 * cam.get(4)

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
                        confidence = "  {0}%".format(round(100 - confidence))
                    else:
                        id = "unknown"
                        confidence = "  {0}%".format(round(100 - confidence))

                cv2.putText(img, str(id), (x + 5, y - 5), font, 1, (255, 255, 255), 2)
                cv2.putText(img, str(confidence), (x + 5, y + h - 5), font, 1, (255, 255, 0), 1)

            cv2.imshow('camera', img)

            k = cv2.waitKey(10) & 0xff
            if k == 27:
                break
            elif k == ord('c') or k == ord('C'):
                current_camera = (current_camera + 1) % total_cameras
                cam.release()
                cam = cv2.VideoCapture(current_camera)
                cam.set(3, 640)
                cam.set(4, 480)

        print("\nExiting Recognizer.")
        cam.release()
        cv2.destroyAllWindows()

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
