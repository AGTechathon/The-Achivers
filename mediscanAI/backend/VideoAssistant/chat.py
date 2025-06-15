from flask import Flask, request, jsonify, render_template
from openai import OpenAI
import os
from datetime import datetime
import logging
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
