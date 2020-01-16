import io
import jsonpickle
import cv2
from sys import path

path.append('/root/')
from img2img import *
from flask import Flask, redirect, url_for, request, render_template, Response, jsonify, redirect
import numpy as np
import base64
from PIL import Image
from flask_cors import CORS

# Declare a flask app
app = Flask(__name__)
CORS(app)


@app.route('/text2img', methods=['POST'])
def _text2img():
    if request.method == 'POST':
        # print(request.data)

        text = request.data.decode("utf-8")
        print(text)
        paths = text2img(text)

        imgs = list()
        for path in paths:
            img = cv2.imread(path)
            img = np.array(img)

            is_success, im_buf_arr = cv2.imencode(".jpg", img)
            byte_im = im_buf_arr.tobytes()

            imgs.append(byte_im)

            # imgdata = base64.b64encode(byte_im)
            # print(byte_im)

        response = {'message': 'image received. size={}x{}'.format(img.shape[1], img.shape[0]), 'data': imgs}
        # encode response using jsonpickle
        response_pickled = jsonpickle.encode(response)

        return Response(response=response_pickled, status=200, mimetype="application/json")
    return None


@app.route('/img2text', methods=['POST'])
def _img2text():
    if request.method == 'POST':

        imgdata = base64.b64decode(request.data)
        img = Image.open(io.BytesIO(imgdata))
        img = img.convert("RGB")

        img = np.array(img)

        im = Image.fromarray(img)
        im.save('./tmp/loaded.jpeg')
        text = img2text('./tmp/loaded.jpeg')

        text = text.split(',')[0].split('.')[0]

        response = {'message': 'image received. size={}x{}'.format(img.shape[1], img.shape[0]), 'data': text}
        response_pickled = jsonpickle.encode(response)

        return Response(response=response_pickled, status=200, mimetype="application/json")
    return None


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=False)
