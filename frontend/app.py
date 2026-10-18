"""Simple Flask server to serve the frontend."""
from dotenv import load_dotenv
from flask import Flask, render_template
import os

app = Flask(__name__, static_folder='.', static_url_path='', template_folder='.')
load_dotenv()  # Load environment variables from .env file

API_HOST = os.getenv("API_HOST")
API_PORT = int(os.getenv("API_PORT"))
WEBSERVER_PORT = int(os.getenv("WEBSERVER_PORT"))

@app.route('/')
def serve_index():
    return render_template('index.html', api_host=API_HOST, api_port=API_PORT)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=WEBSERVER_PORT)
