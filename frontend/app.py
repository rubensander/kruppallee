"""Simple Flask server to serve the frontend."""
from flask import Flask
import os

app = Flask(__name__, static_folder='.', static_url_path='')

@app.route('/')
def serve_index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=3000)
