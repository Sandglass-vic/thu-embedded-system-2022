from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import numpy as np
import cv2
from time import time
from tflite_runtime.interpreter import Interpreter


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

parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
    '--model', help='File path of .tflite file.', required=True)
parser.add_argument(
    '--labels', help='File path of labels file.', required=True)
args = parser.parse_args()

valid = {}
for line in open("valid.txt").readlines():
    [idx, label, text] = line.strip().split(' ', 2)
    valid[int(idx)] = [label, text]

with open(args.labels, 'r') as f:
    labels = {i: line.strip() for i, line in enumerate(f.readlines())}

# init interpreter
interpreter = Interpreter(args.model)
interpreter.allocate_tensors()

# test
start = time()
correct = 0
cnt = 0
for key, val in valid.items():
    _, height, width, _ = interpreter.get_input_details()[0]['shape']
    image = cv2.resize(cv2.imread(f"valid/valid_{key}.jpeg"), (width,height))
    if args.model.find("v3") == -1:
        image = np.array(image) / 127.5 - 1

    results = classify_image(interpreter, image)
    label_id, prob = results[0]
    label_id += 1  # fix label index

    cnt = cnt + 1
    print(labels[label_id], "|", " ".join(val))
    if labels[label_id] == " ".join(val):
        correct = correct + 1
print(f"correct = {correct}, cnt = {cnt}, ratio = {correct/cnt}, elapsed = {time()-start}s")