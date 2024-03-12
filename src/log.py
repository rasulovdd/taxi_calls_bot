from flask import Flask, jsonify, abort, make_response, request, json, send_from_directory
import logging
from logging.handlers import RotatingFileHandler


app01 = Flask(__name__)
app01.config['JSON_SORT_KEYS'] = False
file_handler = RotatingFileHandler(
    'logs/taxi_calls.log', maxBytes=5242880,
    backupCount=10
)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]',
    datefmt='%d-%m-%Y %H:%M:%S'
    )
)
file_handler.setLevel(logging.INFO)
app01.logger.addHandler(file_handler) 
app01.logger.setLevel(logging.INFO)