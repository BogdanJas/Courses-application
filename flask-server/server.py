import json
import sqlite3
import hashlib
import os
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'sources'
DATABASE = '../courseDataset.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/sources/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/topCourses", methods=['GET'])
def top_courses():
    with get_db_connection() as conn:
        courses = conn.execute('SELECT * FROM Courses ORDER BY AddingDate DESC LIMIT 5').fetchall()
        return jsonify([dict(course) for course in courses])

@app.route("/listOfCourses", methods=['GET'])
def courses_list():
    with get_db_connection() as conn:
        courses = conn.execute('''SELECT c.Id, c.Title, c.StartDate, c.EndDate, u.UserName as Instructor, c.CategoryId FROM Courses c 
                               INNER JOIN Users u ON u.Id == c.InstructorId''').fetchall()
        return jsonify([dict(course) for course in courses])

@app.route('/register', methods=['POST'])
def register_user():
    data = request.form
    with get_db_connection() as conn:
        conn.execute('INSERT INTO Users(UserName,Email,PasswordHash,JoinDate,UserRole) VALUES(?,?,?,?,?)',
                     (data['userName'], data['email'], hashlib.sha256(data['password'].encode()).hexdigest(), datetime.now(), data['userRole']))
        conn.commit()
    return jsonify({"status": "success"})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    with get_db_connection() as conn:
        user_info = conn.execute('SELECT Id, username, PasswordHash, UserRole FROM Users WHERE username = ?', (data['username'],)).fetchone()
        if user_info and hashlib.sha256(data['password'].encode()).hexdigest() == user_info['PasswordHash']:
            conn.execute('INSERT INTO Authentication(UserId, LoginSuccess, LoginDate) VALUES(?,?,?)', 
                         (user_info['Id'], True, datetime.now()))
            conn.commit()
            return jsonify({"userRole": user_info["UserRole"], "userName": user_info["username"], "userId": user_info["Id"]})
        else:
            return jsonify({"error": "Invalid credentials or user not found"}), 401

@app.route('/userRoles', methods=['GET'])
@app.route('/categories', methods=['GET'])
@app.route('/materialTypes', methods=['GET'])
@app.route('/statuses', methods=['GET'])
def get_resource():
    table = {
        "/userRoles": "UserRoles",
        "/categories": "CourseCategories",
        "/materialTypes": "ResourceTypes",
        "/statuses": "Statuses"
    }[request.path]
    with get_db_connection() as conn:
        rows = conn.execute(f'SELECT * FROM {table}').fetchall()
        return jsonify([dict(row) for row in rows])

@app.route('/saveCourse', methods=['POST'])
def create_course():
    data = request.form
    imagePath = save_uploaded_file(request.files.get('file'))
    materialPath = save_uploaded_file(request.files.get('courseMaterial'))
    path = materialPath if not data.get('linkToMaterial') else data['linkToMaterial']
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO courses (title, description, instructorid, startdate, enddate, addingdate, categoryid, courseavatarpath) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                       (data['title'], data['description'], data['instructorid'], data['startdate'], data['enddate'], datetime.now(), data['category'], imagePath))
        courseId = cursor.lastrowid
        cursor.execute('INSERT INTO CourseResources (courseId, resourcetype, title, path) VALUES (?,?,?,?)',
                       (courseId, data['materialType'], data['title'], path))
        conn.commit()
    return jsonify({'message': 'Course created successfully'}), 201

def save_uploaded_file(uploaded_file):
    if uploaded_file:
        filename = secure_filename(uploaded_file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        uploaded_file.save(file_path)
        return file_path
    return None

@app.route('/course/<course_id>', methods=['GET'])
def get_course(course_id):
    with get_db_connection() as conn:
        cursor = conn.execute('''SELECT c.Id, c.AddingDate, julianday(c.EndDate) - julianday(c.StartDate) AS Duration, 
                              c.CourseAvatarPath, c.Description, c.Title, u.UserName, u.Email as Contact,
                              cc.Name as CategoryName, rt.Name as ResourceType
                              FROM Courses c
                              INNER JOIN Users u ON u.Id = c.InstructorId
                              INNER JOIN CourseCategories cc on cc.Id = c.CategoryId
                              INNER JOIN CourseResources cr ON cr.CourseId = c.Id
                              INNER JOIN ResourceTypes rt ON rt.Id = cr.ResourceType
                              WHERE c.Id = ?''', (course_id,))
        rows = cursor.fetchall()
        courses = [dict(row) for row in rows]
    return jsonify(courses)

@app.route('/enroll', methods=['POST'])
def add_enrollment():
    data = request.json
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO Enrollments (UserId, CourseId, EnrollmentDate, CompletionStatus) 
                       VALUES (?, ?, ?, ?)''', (data['UserId'], data['CourseId'], data['EnrollmentDate'], 1))
        conn.commit()
    return jsonify({'message': 'Enrolled successfully'}), 201

@app.route('/mycourses/<user_id>', methods=['GET'])
def user_courses(user_id):
    with get_db_connection() as conn:
        courses = conn.execute('''SELECT c.Id, c.Title, c.StartDate, c.EndDate, u.UserName as Instructor, c.CategoryId, e.CompletionStatus as Status
                               FROM Courses c 
                               INNER JOIN Users u ON u.Id == c.InstructorId
                               INNER JOIN Enrollments e on e.CourseId = c.id
                               WHERE e.UserId = ?''', (user_id)).fetchall()
        return jsonify([dict(course) for course in courses])

@app.route('/enrolledcourse/<course_id>', methods=['GET'])
def enrolled_course(course_id):
    with get_db_connection() as conn:
        course = conn.execute('''SELECT c.Id, c.AddingDate, julianday(c.EndDate) - julianday(c.StartDate) AS Duration, 
                              c.CourseAvatarPath, c.Description, c.Title, u.UserName, u.Email as Contact,
                              cc.Name as CategoryName, rt.Name as ResourceType, cr.Path as PathToFile, e.CompletionStatus as Status
                              FROM Enrollments e
                              INNER JOIN Courses c ON c.Id = e.CourseiD
                              INNER JOIN Users u ON u.Id = c.InstructorId
                              INNER JOIN CourseCategories cc on cc.Id = c.CategoryId
                              INNER JOIN CourseResources cr ON cr.CourseId = c.Id
                              INNER JOIN ResourceTypes rt ON rt.Id = cr.ResourceType
                              WHERE e.CourseId = ?''', (course_id,)).fetchall()
        courses = [dict(row) for row in course]
    return jsonify(courses)

@app.route('/updatestatus/<course_id>/<user_id>/<status>', methods=['POST'])
def update_enrollment(course_id, user_id,status):
    with get_db_connection() as conn:
        conn.execute('UPDATE Enrollments SET CompletionStatus = ? WHERE CourseId = ? AND UserId = ?',(status,course_id,user_id))    
        return jsonify({'message': 'User updated successfully'}), 200

@app.route('/review/<course_id>', methods=['POST'])
def add_review(course_id):
    data = request.json
    with get_db_connection() as conn:
        conn.execute('INSERT INTO reviews (userId, courseId, rating, name, reviewDate) VALUES (?, ?, ?, ?, ?)',
                     (data['userId'], data['courseId'], data['rating'], data['review'], data['reviewwDate']))
        conn.commit()
    return jsonify({'message': 'Review added successfully'}), 200

@app.route('/reviews', methods=['GET'])
def get_reviews():
    with get_db_connection() as conn:
        reviews = conn.execute('SELECT c.Id, c.Title, r.Rating from courses c inner join reviews r on r.courseId = c.Id')
        return jsonify([dict(review) for review in reviews])

@app.route('/avggrades/<course_id>', methods=['GET'])
def get_average_reviews(course_id):
    with get_db_connection() as conn:
        reviews = conn.execute('''SELECT c.Id, AVG(r.Rating) as average from courses c inner join reviews r on r.courseId = c.Id 
                               WHERE c.Id = ?''',(course_id))
        return jsonify([dict(review) for review in reviews])

if __name__ == "__main__":
    app.run(debug=True)
