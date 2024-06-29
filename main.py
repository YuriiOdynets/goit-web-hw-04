from flask import Flask, render_template, request, send_from_directory, redirect
import socket
import threading
import json
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/message.html')
def message():
    return render_template('message.html')

@app.route('/message', methods=['POST'])
def handle_message():
    username = request.form['username']
    message = request.form['message']
    data = {
        'username': username,
        'message': message
    }
    send_udp_message(data)
    return redirect('/')

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404

def send_udp_message(data):
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5000
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    message = json.dumps(data).encode('utf-8')
    sock.sendto(message, (UDP_IP, UDP_PORT))

def start_flask():
    app.run(port=3000)

def start_udp_server():
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5000
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    if not os.path.exists('storage'):
        os.makedirs('storage')

    while True:
        data, addr = sock.recvfrom(1024)
        message = json.loads(data.decode('utf-8'))
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        file_path = os.path.join('storage', 'data.json')
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                content = json.load(file)
        else:
            content = {}
        content[timestamp] = message
        with open(file_path, 'w') as file:
            json.dump(content, file, indent=4)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=start_flask)
    udp_thread = threading.Thread(target=start_udp_server)

    flask_thread.start()
    udp_thread.start()

    flask_thread.join()
    udp_thread.join()