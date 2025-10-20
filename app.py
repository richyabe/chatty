from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app=app, db=db)

import routes
import models

# ✅ Automatically create all tables if they don’t exist
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)

