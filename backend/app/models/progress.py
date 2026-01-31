"""
Progress Model
Tracks lesson completion for students
"""

from app import db
from datetime import datetime

class Progress(db.Model):
    __tablename__ = 'progress'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # ensure one progress record per student per lesson
    __table_args__ = (
        db.UniqueConstraint('student_id', 'lesson_id', name='unique_progress'),
    )
    
    def __repr__(self):
        return f'<Progress student={self.student_id} lesson={self.lesson_id} completed={self.completed}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'lesson_id': self.lesson_id,
            'completed': self.completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }