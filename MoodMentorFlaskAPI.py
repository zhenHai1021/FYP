from flask import Flask, request, jsonify
import subprocess
import requests

#facial Login
import cv2
import numpy as np
from PIL import Image
import pickle
import requests
##########################

app = Flask(__name__)
@app.route('/facialLogin', methods=['POST', 'GET'])  # Separate GET and POST using square brackets
def faceRecognition():
    def download_file_from_url(url, local_path):
        response = requests.get(url)
        with open(local_path, 'wb') as f:
            f.write(response.content)

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    download_file_from_url('https://facial-login-model-bucket.s3.amazonaws.com/trainer/trainer.yml', 'trainer.yml')
    recognizer.read('trainer.yml')

    cascadePath = 'https://facial-login-model-bucket.s3.amazonaws.com/haarcascade_frontalface_default.xml'
    download_file_from_url('https://facial-login-model-bucket.s3.amazonaws.com/haarcascade_frontalface_default.xml', 'haarcascade_frontalface_default.xml')
    faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    font = cv2.FONT_HERSHEY_SIMPLEX

    # Starting realtime video capture
    total_cameras = 2  # Total number of cameras connected
    current_camera = 0  # Index of the current camera being used

    # Starting realtime video capture
    cam = cv2.VideoCapture(0)
    cam.set(3, 640)  # set video width
    cam.set(4, 480)  # set video height

    # Define min window size to be recognized as a face
    minW = 0.1 * cam.get(3)
    minH = 0.1 * cam.get(4)

    download_file_from_url('https://facial-login-model-bucket.s3.amazonaws.com/names.pkl', 'names.pkl')
    with open('names.pkl', 'rb') as f:
        names = pickle.load(f)

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

            # Check if confidence is less than 100 ==> "0" is a perfect match
            if confidence < 100:
                if id >= 0 and id < len(names):
                    id = names[id]
                    confidence = "  {0}%".format(round(100 - confidence))
                else:
                    id = "unknown"
                    confidence = "  {0}%".format(round(100 - confidence))

            cv2.putText(img, str(id), (x + 5, y - 5), font, 1, (255, 255, 255), 2)  # Display the name of the individual
            cv2.putText(img, str(confidence), (x + 5, y + h - 5), font, 1, (255, 255, 0), 1)

        cv2.imshow('camera', img)

        k = cv2.waitKey(10) & 0xff  # Press 'ESC' for exiting video
        if k == 27:
            break
        elif k == ord('c') or k == ord('C'):  # Switch the camera when 'C' or 'c' is pressed
            current_camera = (current_camera + 1) % total_cameras
            cam.release()
            cam = cv2.VideoCapture(current_camera)
            cam.set(3, 640)
            cam.set(4, 480)

    # Exit the video window
    print("\nExiting Recognizer.")
    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
