"""
Course Routes
Course creation, listing, and enrollment
"""

from flask import Blueprint, request, jsonify
from app import db
from app.models.user import User
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.utils.auth import token_required, role_required

bp = Blueprint('courses', __name__, url_prefix='/api/courses')

@bp.route('', methods=['POST'])
@token_required
@role_required('instructor')
def create_course(current_user):
    """
    Create a new course (instructors only)
    
    Expected JSON:
    {
        "title": "Introduction to Python",
        "description": "Learn Python from scratch"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('title'):
            return jsonify({'error': 'Title is required'}), 400
        
        title = data['title'].strip()
        description = data.get('description', '').strip()
        
        # Create course
        new_course = Course(
            title=title,
            description=description,
            instructor_id=current_user['user_id']
        )
        
        db.session.add(new_course)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Course created successfully',
            'course': new_course.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('', methods=['GET'])
@token_required
def get_all_courses(current_user):
    """
    Get all available courses
    """
    try:
        courses = Course.query.all()
        
        courses_data = []
        for course in courses:
            course_dict = course.to_dict()
            
            # Add instructor name
            instructor = User.query.get(course.instructor_id)
            course_dict['instructor_name'] = instructor.full_name if instructor else 'Unknown'
            
            # Add enrollment status for current user
            if current_user['role'] == 'student':
                enrollment = Enrollment.query.filter_by(
                    student_id=current_user['user_id'],
                    course_id=course.id
                ).first()
                course_dict['is_enrolled'] = enrollment is not None
            else:
                course_dict['is_enrolled'] = False
            
            # Add lesson count
            course_dict['lesson_count'] = len(course.lessons)
            
            courses_data.append(course_dict)
        
        return jsonify({
            'status': 'success',
            'courses': courses_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:course_id>', methods=['GET'])
@token_required
def get_course(current_user, course_id):
    """
    Get a specific course with its lessons
    """
    try:
        course = Course.query.get(course_id)
        
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        course_dict = course.to_dict()
        
        # Add instructor info
        instructor = User.query.get(course.instructor_id)
        course_dict['instructor_name'] = instructor.full_name if instructor else 'Unknown'
        
        # Add lessons (sorted by order_index)
        lessons_data = []
        for lesson in sorted(course.lessons, key=lambda x: x.order_index):
            lessons_data.append(lesson.to_dict())
        course_dict['lessons'] = lessons_data
        
        # Check enrollment status
        if current_user['role'] == 'student':
            enrollment = Enrollment.query.filter_by(
                student_id=current_user['user_id'],
                course_id=course.id
            ).first()
            course_dict['is_enrolled'] = enrollment is not None
        else:
            course_dict['is_enrolled'] = current_user['user_id'] == course.instructor_id
        
        return jsonify({
            'status': 'success',
            'course': course_dict
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:course_id>/enroll', methods=['POST'])
@token_required
@role_required('student')
def enroll_in_course(current_user, course_id):
    """
    Enroll student in a course (students only)
    """
    try:
        # Check if course exists
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        # Check if already enrolled
        existing_enrollment = Enrollment.query.filter_by(
            student_id=current_user['user_id'],
            course_id=course_id
        ).first()
        
        if existing_enrollment:
            return jsonify({'error': 'Already enrolled in this course'}), 409
        
        # Create enrollment
        new_enrollment = Enrollment(
            student_id=current_user['user_id'],
            course_id=course_id
        )
        
        db.session.add(new_enrollment)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Successfully enrolled in course',
            'enrollment': new_enrollment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/my-courses', methods=['GET'])
@token_required
def get_my_courses(current_user):
    """
    Get courses for current user
    - For students: enrolled courses
    - For instructors: created courses
    """
    try:
        if current_user['role'] == 'student':
            # Get enrolled courses
            enrollments = Enrollment.query.filter_by(
                student_id=current_user['user_id']
            ).all()
            
            courses_data = []
            for enrollment in enrollments:
                course = Course.query.get(enrollment.course_id)
                if course:
                    course_dict = course.to_dict()
                    
                    # Add instructor name
                    instructor = User.query.get(course.instructor_id)
                    course_dict['instructor_name'] = instructor.full_name if instructor else 'Unknown'
                    
                    # Add enrollment date
                    course_dict['enrolled_at'] = enrollment.enrolled_at.isoformat()
                    
                    # Add lesson count
                    course_dict['lesson_count'] = len(course.lessons)
                    
                    courses_data.append(course_dict)
        
        else:  # instructor
            # Get created courses
            courses = Course.query.filter_by(
                instructor_id=current_user['user_id']
            ).all()
            
            courses_data = []
            for course in courses:
                course_dict = course.to_dict()
                course_dict['instructor_name'] = current_user.get('full_name', 'You')
                course_dict['lesson_count'] = len(course.lessons)
                course_dict['student_count'] = len(course.enrollments)
                courses_data.append(course_dict)
        
        return jsonify({
            'status': 'success',
            'courses': courses_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:course_id>', methods=['PUT'])
@token_required
@role_required('instructor')
def update_course(current_user, course_id):
    """
    Update course details (instructors only, own courses)
    """
    try:
        course = Course.query.get(course_id)
        
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        # Check if current user is the course instructor
        if course.instructor_id != current_user['user_id']:
            return jsonify({'error': 'You can only edit your own courses'}), 403
        
        data = request.get_json()
        
        # Update fields
        if 'title' in data:
            course.title = data['title'].strip()
        if 'description' in data:
            course.description = data['description'].strip()
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Course updated successfully',
            'course': course.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:course_id>', methods=['DELETE'])
@token_required
@role_required('instructor')
def delete_course(current_user, course_id):
    """
    Delete a course (instructors only, own courses)
    """
    try:
        course = Course.query.get(course_id)
        
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        # Check ownership
        if course.instructor_id != current_user['user_id']:
            return jsonify({'error': 'You can only delete your own courses'}), 403
        
        db.session.delete(course)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Course deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500