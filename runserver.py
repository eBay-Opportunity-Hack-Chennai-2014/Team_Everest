from flask import Flask

from blueprints.frontend import frontend

app = Flask(__name__)
app.config.from_object('default_settings')
app.config.from_envvar('EVEREST_SETTINGS', silent=True)
app.register_blueprint(frontend, url_prefix='/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
