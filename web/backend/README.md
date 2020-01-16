# spokessimpsons - web - backend

## Introduction

We use Flask to write our backend. There are two method: img2text and text2img.

* __img2text__: Please pass in base64 encoded image. Return value is the reply predicted by your screenshot.
* __text2img__: Please pass in text. Return value is a list consist of three images generated according to the text passed in.

## Getting Started

1. For development, run `python app.py`. Gunicorn or uWSGI is recommanded for production.
2. Config Nginx to forward requests.
3. CertBot is recommended for SSL.

## Credits

* https://github.com/pallets/flask
* https://github.com/mtobeiyf/keras-flask-deploy-webapp