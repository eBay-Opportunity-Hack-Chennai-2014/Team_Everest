import os

from flask import Blueprint, render_template

import models

backend = Blueprint('backend', __name__)

@backend.route('generate_receipt', methods=['POST'])
def generate_receipt():
    return render_template('test.html')
