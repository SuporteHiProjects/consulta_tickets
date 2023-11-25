from flask import (Flask, make_response, request, render_template, redirect, url_for, flash, jsonify, send_file, Response)
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FileField
from wtforms.validators import DataRequired, Email
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import base64
import os
import requests
import datetime
import time
import json
import app_data as function
from forms import TicketForm
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import subprocess
import logging
from io import BytesIO
import mimetypes
import jwt
from jwt import encode
import hashlib