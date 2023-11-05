from flask import Flask, request, jsonify
import subprocess
import requests

app = Flask(__name__)


@app.route('/')
def hello_world():
    try:
         # Construct the S3 object URL
        s3_object_url = f'https://s3.amazonaws.com/{facial-login-model-bucket}/hello_world.py'
        print(f'S3 Object URL: {s3_object_url}')

        # Fetch the 'hello_world.py' script from the public S3 URL
        s3_script = requests.get(s3_object_url)
        
        if s3_script.status_code == 200:
            with open('/tmp/hello_world.py', 'wb') as f:
                f.write(s3_script.content)
            
            # Execute the script
            result = subprocess.check_output(['python', '/tmp/hello_world.py'], stderr=subprocess.STDOUT, text=True)
            
            # Return the result as JSON
            response_data = {'result': result}
            return jsonify(response_data)
        else:
            return jsonify({'error': f"Failed to fetch 'hello_world.py' from S3: {s3_script.status_code}"})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
