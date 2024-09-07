from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from models.db import db

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = {'extend_existing': True}

    def __repr__(self):
        return f'<Job {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'date_posted': self.date_posted
        }