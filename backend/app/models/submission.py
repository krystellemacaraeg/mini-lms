"""
Submission Model
Represents student assignment submissions
"""

from app import db
from datetime import datetime

class Submission(db.Model):
    __tablename__ = 'submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    grade = db.Column(db.Integer, nullable=True)  # NULL = not graded yet
    
    def __repr__(self):
        return f'<Submission assignment={self.assignment_id} student={self.student_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'assignment_id': self.assignment_id,
            'student_id': self.student_id,
            'content': self.content,
            'submitted_at': self.submitted_at.isoformat(),
            'grade': self.grade
        }