#!/usr/bin/python3

import sys
import urllib.parse
from flask import Flask, send_file, request

app = Flask(__name__)

@app.route('/play')
def serve_chromecast():
    try:
        filename = urllib.parse.unquote(request.args.get("name"))
        return send_file(filename)
    except Exception as e:
        return str(e)
     
if __name__ == '__main__':
    app.run(host='0.0.0.0')

