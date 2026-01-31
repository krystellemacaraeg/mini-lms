"""
Database Testing Routes
Endpoints to verify database operations
"""

from flask import Blueprint, jsonify
from app import db
from app.models import User, Course, Lesson

bp = Blueprint('database', __name__, url_prefix='/api/db')

@bp.route('/test', methods=['GET'])
def test_database():
    """
    Test database connectivity and basic operations
    """
    try:
        # count records in each table
        user_count = User.query.count()
        course_count = Course.query.count()
        lesson_count = Lesson.query.count()
        
        return jsonify({
            'status': 'success',
            'message': 'Database is connected',
            'tables': {
                'users': user_count,
                'courses': course_count,
                'lessons': lesson_count
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@bp.route('/seed', methods=['POST'])
def seed_database():
    """
    Add sample data for testing
    """
    try:
        # create sample instructor
        instructor = User(
            email='instructor@test.com',
            password_hash='temp_hash',  # implement real hashing later
            full_name='Dr. Jane Smith',
            role='instructor'
        )
        db.session.add(instructor)
        db.session.commit()
        
        # create sample course
        course = Course(
            title='Introduction to Python',
            description='Learn Python basics',
            instructor_id=instructor.id
        )
        db.session.add(course)
        db.session.commit()
        
        # create sample lesson
        lesson = Lesson(
            course_id=course.id,
            title='Python Variables',
            content='Variables store data...',
            order_index=1
        )
        db.session.add(lesson)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Sample data created',
            'data': {
                'instructor': instructor.to_dict(),
                'course': course.to_dict(),
                'lesson': lesson.to_dict()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500