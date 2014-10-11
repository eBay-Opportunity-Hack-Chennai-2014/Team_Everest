from flask import Flask

from blueprints.frontend import frontend
from blueprints.backend import backend

from models import db

app = Flask(__name__)
app.config.from_object('default_settings')
app.config.from_envvar('EVEREST_SETTINGS', silent=True)
app.register_blueprint(frontend, url_prefix='/')
app.register_blueprint(backend, url_prefix='/backend/')

app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = set([ 'xls', 'xlsx', 'csv'])

db.init_app(app)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=8000)
