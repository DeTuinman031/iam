# manage.py
"""
Flask CLI entry point for IAM service.
Supports: flask run, flask db migrate, flask db upgrade, etc.

You can run this directly: python manage.py run
Or use flask CLI: flask run (requires FLASK_APP=manage.py or FLASK_APP=app)
"""
from app import create_app
from flask.cli import FlaskGroup

# Import all models so Flask-Migrate can detect them
from app.auth import models  # noqa: F401

app = create_app()

cli = FlaskGroup(create_app=create_app)

if __name__ == "__main__":
    cli()
