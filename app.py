from flask import Flask
from flask_restful import Resource, Api

from database.init import init_db

app = Flask(__name__)
api = Api(app)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
    