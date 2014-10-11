import os

from flask import Blueprint, render_template

frontend = Blueprint('frontend', __name__,
        template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))

@frontend.route('/', methods=['GET'])
def test_page():
    return render_template('test.html')
