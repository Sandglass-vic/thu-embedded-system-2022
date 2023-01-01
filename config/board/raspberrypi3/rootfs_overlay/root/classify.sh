#!/usr/bin/bash

./dist/classify --model model/tflite/mobilenet-v1-1.0-224.tflite --labels synset_words.txt --server_ip 192.168.43.247 --video http://localhost:8080/?action=stream --width 224 --height 224
