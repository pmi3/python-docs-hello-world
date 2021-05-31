from flask import Flask, request, make_response
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, Universe!"
