from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import requests
import time
import socketio
import argparse
import threading
import numpy as np

# from picamera2 import Picamera2
from PIL import Image
from cv2 import VideoCapture, CAP_PROP_BUFFERSIZE
from tflite_runtime.interpreter import Interpreter

parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
    '--model', help='File path of .tflite file.', required=True)
parser.add_argument(
    '--labels', help='File path of labels file.', required=True)
parser.add_argument(
    '--video', help='video source', required=True)
parser.add_argument(
    '--width', help='video width', default=224)
parser.add_argument(
    '--height', help='video height', default=224)
parser.add_argument(
    '--server_ip', help='Server ip address.', required=True)
args = parser.parse_args()

# server_ip = "192.168.31.162"
sio = socketio.Client()

@sio.event
def connect():
    print("Connected!")

@sio.event
def connect_error(data):
    print("The connection failed!")

@sio.event
def disconnect():
    print("Disconnected!")

sio.connect(f"http://{args.server_ip}:5000")
post_url = f"http://{args.server_ip}:5000/result"

ret = False
frame = None
labels = None
interpreter = None
width = int(args.width)
height = int(args.height)
is_v3_model = args.model.find("v3") != -1

cam = VideoCapture(int(args.video) if str.isdigit(args.video) else args.video)
cam.set(CAP_PROP_BUFFERSIZE, 3)

def get_frame():
    global ret, frame, tmp
    while True:
        ret, frame = cam.read()
        time.sleep(0.01)

def get_cpuuse():
    return os.popen("top -n1 | grep \"CPU:\" | head -n 1 | awk '{print $2 + $4}'").readline().strip()

def get_memuse():
    return os.popen("free -m | grep Mem").readline().strip().split()[2]

def set_input_tensor(interpreter, image):
    tensor_index = interpreter.get_input_details()[0]['index']
    input_tensor = interpreter.tensor(tensor_index)()[0]
    input_tensor[:, :] = image


def classify_image(interpreter, image, top_k=1):
    """Returns a sorted array of classification results."""
    set_input_tensor(interpreter, image)
    interpreter.invoke()
    output_details = interpreter.get_output_details()[0]
    output = np.squeeze(interpreter.get_tensor(output_details['index']))
  
    # If the model is quantized (uint8 data), then dequantize the results
    if output_details['dtype'] == np.uint8:
      scale, zero_point = output_details['quantization']
      output = scale * (output - zero_point)

    ordered = np.argpartition(-output, top_k)
    return [(i, output[i]) for i in ordered[:top_k]]

@sio.on('pi')
def on_message(data):
    print("message received!")
    received_time = time.time()
    idx = data.split(' ')[-1]

    image = Image.fromarray(frame.astype('uint8')).convert('RGB').resize((width,height), Image.ANTIALIAS)
    if not is_v3_model:
        image = np.array(image) / 127.5 - 1
    else:
        image = np.array(image)

    results = classify_image(interpreter, image)
    label_id, prob = results[0]
    label_id += 1 # fix label index
    fps = 1 / (time.time() - received_time)
    cpu = get_cpuuse()
    mem = get_memuse()
    data = {"res": labels[label_id], 
            "fps": fps,
            "cpu": cpu,
            "mem": mem,
            "idx": idx}
    res = requests.post(url=post_url,data=data)
    print(data)


def load_labels(path):
    with open(path, 'r') as f:
        return {i: line.strip() for i, line in enumerate(f.readlines())}


if __name__ == '__main__':
    t = threading.Thread(target=get_frame)
    t.setDaemon(True)
    t.start()
    labels = load_labels(args.labels)
    interpreter = Interpreter(args.model)
    interpreter.allocate_tensors()
