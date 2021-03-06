import logging
from threading import Thread
import cv2
from flask import Flask, jsonify, render_template, Response
import numpy as np
from crac_client.retriever.retriever import Retriever
from crac_protobuf.camera_pb2 import (
    CameraStatus,
)
import webbrowser
from werkzeug.serving import make_server


logger = logging.getLogger(__name__)
app = Flask(__name__)
global list_cameras, camera_retriever
global server_thread
server_thread = None
list_cameras: dict = None
camera_retriever: Retriever = None
black_frame = np.zeros((720, 1280, 3), dtype = "uint8")
_, buffer = cv2.imencode('.jpg', black_frame)


@app.route('/camera/<int:id>')
def camera(id: int):
    """Video streaming route."""
    return Response(__gen_frames(f"camera{id}"), mimetype='multipart/x-mixed-replace; boundary=frame')

def __gen_frames(camera="camera1"):
    stream = camera_retriever.video(name=camera)
    for response in stream:
        if response.status is CameraStatus.CAMERA_DISCONNECTED:
            stream.cancel()
            break
        yield response.video

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

@app.route('/check')
def check():
    return jsonify(list_cameras)

@app.route('/black')
def black():
    return Response(buffer.tobytes(), mimetype="image/jpeg")

def start_server():
    global server_thread
    server_thread = ServerThread(app)
    server_thread.start()
    webbrowser.open_new(url="http://127.0.0.1:5000")

def stop_server():
    global server_thread
    server_thread.shutdown()
    server_thread = None

def set_cameras(cameras: dict):
    global list_cameras
    list_cameras = cameras

def set_camera_status(camera_key: str, camera_status: int):
    if list_cameras:
        camera = [list_cameras[camera_name] for camera_name in list_cameras if list_cameras[camera_name]["key"] == camera_key][0]
        camera["status"] = camera_status

def set_retriever(retriever: Retriever):
    global camera_retriever
    camera_retriever = retriever


class ServerThread(Thread):
    def __init__(self, app):
        Thread.__init__(self)
        self.server = make_server('127.0.0.1', 5000, app, threaded=True)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        logger.info('starting server')
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()