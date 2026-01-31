"""
Lesson Routes
Lesson creation and viewing
"""

from flask import Blueprint, request, jsonify
from app import db
from app.models.course import Course
from app.models.lesson import Lesson
from app.models.enrollment import Enrollment
from app.models.progress import Progress
from app.utils.auth import token_required, role_required

bp = Blueprint('lessons', __name__, url_prefix='/api/lessons')

@bp.route('', methods=['POST'])
@token_required
@role_required('instructor')
def create_lesson(current_user):
    """
    Create a new lesson (instructors only)
    
    Expected JSON:
    {
        "course_id": 1,
        "title": "Variables and Data Types",
        "content": "In Python, variables are...",
        "order_index": 1
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['course_id', 'title', 'content', 'order_index']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        course_id = data['course_id']
        title = data['title'].strip()
        content = data['content'].strip()
        order_index = data['order_index']
        
        # Check if course exists
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        # Check if current user is the course instructor
        if course.instructor_id != current_user['user_id']:
            return jsonify({'error': 'You can only add lessons to your own courses'}), 403
        
        # Create lesson
        new_lesson = Lesson(
            course_id=course_id,
            title=title,
            content=content,
            order_index=order_index
        )
        
        db.session.add(new_lesson)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Lesson created successfully',
            'lesson': new_lesson.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:lesson_id>', methods=['GET'])
@token_required
def get_lesson(current_user, lesson_id):
    """
    Get a specific lesson
    Students must be enrolled in the course
    """
    try:
        lesson = Lesson.query.get(lesson_id)
        
        if not lesson:
            return jsonify({'error': 'Lesson not found'}), 404
        
        course = Course.query.get(lesson.course_id)
        
        # Check access permissions
        if current_user['role'] == 'student':
            # Check if student is enrolled
            enrollment = Enrollment.query.filter_by(
                student_id=current_user['user_id'],
                course_id=lesson.course_id
            ).first()
            
            if not enrollment:
                return jsonify({'error': 'You must be enrolled in this course to view lessons'}), 403
        
        elif current_user['role'] == 'instructor':
            # Check if instructor owns the course
            if course.instructor_id != current_user['user_id']:
                return jsonify({'error': 'Access denied'}), 403
        
        lesson_dict = lesson.to_dict()
        
        # Add course info
        lesson_dict['course_title'] = course.title
        
        # Check if student has completed this lesson
        if current_user['role'] == 'student':
            progress = Progress.query.filter_by(
                student_id=current_user['user_id'],
                lesson_id=lesson.id
            ).first()
            lesson_dict['completed'] = progress.completed if progress else False
        
        return jsonify({
            'status': 'success',
            'lesson': lesson_dict
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:lesson_id>/complete', methods=['POST'])
@token_required
@role_required('student')
def mark_lesson_complete(current_user, lesson_id):
    """
    Mark a lesson as completed (students only)
    """
    try:
        lesson = Lesson.query.get(lesson_id)
        
        if not lesson:
            return jsonify({'error': 'Lesson not found'}), 404
        
        # Check if student is enrolled
        enrollment = Enrollment.query.filter_by(
            student_id=current_user['user_id'],
            course_id=lesson.course_id
        ).first()
        
        if not enrollment:
            return jsonify({'error': 'You must be enrolled in this course'}), 403
        
        # Check if progress record exists
        progress = Progress.query.filter_by(
            student_id=current_user['user_id'],
            lesson_id=lesson_id
        ).first()
        
        if progress:
            # Update existing
            progress.completed = True
            from datetime import datetime
            progress.completed_at = datetime.utcnow()
        else:
            # Create new
            from datetime import datetime
            progress = Progress(
                student_id=current_user['user_id'],
                lesson_id=lesson_id,
                completed=True,
                completed_at=datetime.utcnow()
            )
            db.session.add(progress)
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Lesson marked as complete',
            'progress': progress.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:lesson_id>', methods=['PUT'])
@token_required
@role_required('instructor')
def update_lesson(current_user, lesson_id):
    """
    Update lesson content (instructors only, own courses)
    """
    try:
        lesson = Lesson.query.get(lesson_id)
        
        if not lesson:
            return jsonify({'error': 'Lesson not found'}), 404
        
        course = Course.query.get(lesson.course_id)
        
        # Check ownership
        if course.instructor_id != current_user['user_id']:
            return jsonify({'error': 'You can only edit lessons in your own courses'}), 403
        
        data = request.get_json()
        
        # Update fields
        if 'title' in data:
            lesson.title = data['title'].strip()
        if 'content' in data:
            lesson.content = data['content'].strip()
        if 'order_index' in data:
            lesson.order_index = data['order_index']
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Lesson updated successfully',
            'lesson': lesson.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:lesson_id>', methods=['DELETE'])
@token_required
@role_required('instructor')
def delete_lesson(current_user, lesson_id):
    """
    Delete a lesson (instructors only, own courses)
    """
    try:
        lesson = Lesson.query.get(lesson_id)
        
        if not lesson:
            return jsonify({'error': 'Lesson not found'}), 404
        
        course = Course.query.get(lesson.course_id)
        
        # Check ownership
        if course.instructor_id != current_user['user_id']:
            return jsonify({'error': 'You can only delete lessons in your own courses'}), 403
        
        db.session.delete(lesson)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Lesson deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500