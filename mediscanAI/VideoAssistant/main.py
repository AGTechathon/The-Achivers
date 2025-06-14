from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

if __name__ == '__main__':
    app.run(debug=True)