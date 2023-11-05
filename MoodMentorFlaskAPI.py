from flask import Flask, request, jsonify
import subprocess
import boto3

app = Flask(__name__)

# Define your AWS S3 bucket and object key for the Login.py script
S3_BUCKET_NAME = 'facial-login-model-bucket'
S3_OBJECT_KEY = 'LoginMoodMentor.py'

s3 = boto3.client('s3')

@app.route('/facialLogin', methods=['GET'])
def facial_login():
    try:
        # Fetch the 'Login.py' script from S3
        s3.download_file(S3_BUCKET_NAME, S3_OBJECT_KEY, '/tmp/LoginMoodMentor.py')

        # Execute the script
        result = subprocess.check_output(['python', '/tmp/LoginMoodMentor.py'], stderr=subprocess.STDOUT, text=True)

        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
