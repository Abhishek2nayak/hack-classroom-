# for backend

# Import flask and jsonify
from flask import Flask, request, jsonify, render_template, redirect, url_for
import datetime
app = Flask(__name__)

# Data dictionaries
students = {
    'abhishek': '123',
    'amanda': '123',
    # Add more student usernames and passwords as needed
}

teachers = {
    'xyz': '1234'
}

teacher_questions = {}


teacher_courses = {
    "xyz":[{"course_name":"abc", "class_code":"cd"}]
}

# Number of days after which a question becomes overdue
OVERDUE_DAYS = 7

# define routes to get index.html page


@app.route('/')
def selectRole():
    return render_template('index.html')


@app.route('/login')
def login():
    role = request.args.get('role')
    return render_template('login.html', role=role)


@app.route('/dashboard/<name>')
def dashboard(name):
    return render_template('dashboard.html', name=name)


@app.route('/process-login', methods=['POST'])
def process_login():
    role = request.form.get('role')
    name = request.form.get('name')
    classcode = request.form.get('classcode')

    if role == 'student':
        if name in students and students[name] == classcode:
            # Successful login for students
            return redirect(url_for('dashboard', name=name))
        else:
            # Invalid credentials for students
            return render_template('login.html', role=role, error="Invalid credentials")

    elif role == 'teacher':
        if name in teachers and teachers[name] == classcode:
            # Successful login for teachers
            return redirect(url_for('dashboard_teacher', name=name))
        else:
            # Invalid credentials for teachers
            return render_template('login.html', role=role, error="Invalid credentials")


@app.route('/dashboard_teacher/<name>')
def dashboard_teacher(name):
    courses = teacher_courses.get(name, [])  # Get the courses for the teacher
    print(courses)
    return render_template('dashboard_teacher.html', name=name, courses=courses)


@app.route('/add-course', methods=['POST'])
def add_course():
    teacher = request.form.get('name')
    course_name = request.form.get('course_name')
    class_code = request.form.get('class_code')

    # Check if the teacher is in the teacher_courses dictionary
    if teacher not in teacher_courses:
        teacher_courses[teacher] = []

    # Add the new course to the teacher's list of courses
    if course_name and class_code:
        course_info = {"course": course_name, "class_code": class_code}
        teacher_courses[teacher].append(course_info)

    # Redirect back to the teacher's dashboard
    return redirect(url_for('dashboard_teacher', name=teacher))









# Define a route for getting the status of a question
@app.route('/status/<int:question_id>', methods=['GET'])
def status(question_id):
    # If the request method is GET, return the status of the question if it exists, otherwise return an error message
    if request.method == 'GET':
        if question_id in questions:
            # Get the question data
            question = questions[question_id]
            # Check if the question has a correct answer marked by the teacher
            if question["correct"] is not None:
                status = "solved"
            else:
                now = datetime.datetime.now()
                posted = question["posted"]
                # Calculate the difference in days between now and posted
                days = (now - posted).days
                # Check if the difference is greater than or equal to the overdue days constant
                if days >= OVERDUE_DAYS:
                    status = "overdue"
                else:
                    status = "new"
            return jsonify({"status": status})
        else:
            return jsonify({"message": "Question not found"})

# Modify the route for posting a question to add a posted attribute to store the date and time when the question was posted


@app.route('/question/<string:name>', methods=['POST', 'PUT'])
def question(name):
    # If the request method is POST, increment the student's questions count and points by one, and create a new question with an id
    if request.method == 'POST':
        if name in students:
            students[name]["questions"] += 1
            students[name]["points"] += 1
            # generate a unique id for the question
            question_id = len(questions) + 1
            # Get the course parameter from the query string
            course = request.args.get("course")
            # Get the anonymous parameter from the query string and convert it to a boolean value
            anonymous = request.args.get("anonymous")
            anonymous = anonymous.lower() in ["true", "yes", "1"]
            questions[question_id] = {
                "asker": name,  # Name of the student who asked the question
                "answers": {},  # Answers as a dictionary of {answerer: answer}
                "correct": None,  # Name of the student who gave the correct answer, if any
                "rewarded": None,  # Name of the student who received the reward from the asker, if any
                "posted": datetime.datetime.now(),  # Date and time when the question was posted
                "course": course,  # Name of the course that the question belongs to
                "anonymous": anonymous  # Whether the question is anonymous or not
            }
            return jsonify({"message": "Question posted", "question_id": question_id})
        else:
            return jsonify({"message": "Student not found"})
    # If the request method is PUT, increment the student's responses count and points by one, and add an answer to the question with an id
    elif request.method == 'PUT':
        if name in students:
            students[name]["responses"] += 1
            students[name]["points"] += 1
            # get the question id from the query string
            question_id = request.args.get("question_id")
            # get the answer from the query string
            answer = request.args.get("answer")
            # Get the anonymous parameter from the query string and convert it to a boolean value
            anonymous = request.args.get("anonymous")
            anonymous = anonymous.lower() in ["true", "yes", "1"]
            if question_id and answer:  # check if both parameters are provided
                # convert the question id to an integer
                question_id = int(question_id)
                if question_id in questions:  # check if the question id exists
                    # Get the status of the question by calling another function that I defined earlier (not shown here)
                    status = status(question_id)["status"]
                    # Check if the status is not solved
                    if status != "solved":
                        questions[question_id]["answers"][name] = {
                            "answer": answer,  # store the answer text
                            "anonymous": anonymous  # store whether the answer is anonymous or not
                        }  # add an answer as a dictionary with two keys: answer and anonymous
                        return jsonify({"message": "Question answered"})
                    else:
                        return jsonify({"message": "Question already solved"})
                else:
                    return jsonify({"message": "Question not found"})
            else:
                return jsonify({"message": "Missing parameters"})
        else:
            return jsonify({"message": "Student not found"})


@app.route('/questions/<string:course>', methods=['GET'])
def questions_by_course(course):
    # If the request method is GET, return a list of questions that match the course parameter, or an error message if no questions are found
    if request.method == 'GET':
        # Declare a list to store the matching questions
        matching_questions = []
        # Loop through all the questions in the questions dictionary
        for q_id, question in questions.items():
            # Check if the course attribute of the question matches the course parameter
            if questions[q_id]["course"] == course:
                # Add the question to the matching list
                matching_questions.append(question)
        # Check if the matching list is not empty
        if matching_questions:
            # Return the matching list as a JSON object
            return jsonify(matching_questions)
        else:
            return jsonify({"message": "No questions found for this course"})

# Modify the route for rewarding a point to an answerer by adding another extra point if the question was overdue


@app.route('/reward/<string:name>', methods=['PUT'])
def reward(name):
    # If the request method is PUT, check if the user is the asker of a question with an id, and reward a point to an answerer of their choice, and give an extra point to the answerer
    if request.method == 'PUT':
        # get the question id from the query string
        question_id = request.args.get("question_id")
        # get the name of the student who gave the answer from the query string
        answerer = request.args.get("answerer")
        if question_id and answerer:  # check if both parameters are provided
            # convert the question id to an integer
            question_id = int(question_id)
            if question_id in questions:  # check if the question id exists
                # check if the user is the asker of the question
                if questions[question_id]["asker"] == name:
                    # check if there is no reward given yet
                    if questions[question_id]["rewarded"] is None:
                        # check if the answerer exists in the answers dictionary
                        if answerer in questions[question_id]["answers"]:
                            # mark the rewarded answer with the name of the answerer
                            questions[question_id]["rewarded"] = answerer
                            # give an extra point to the answerer
                            students[answerer]["points"] += 1
                            # Get the status of the question
                            status = status(question_id)["status"]
                            # Check if the status is overdue
                            if status == "overdue":
                                # give another extra point to the answerer for answering an overdue question
                                students[answerer]["points"] += 1
                            return jsonify({"message": "Reward given"})
                        else:
                            return jsonify({"message": "Answerer not found"})
                    else:
                        return jsonify({"message": "Reward already given"})
                else:
                    return jsonify({"message": "User not authorized"})
            else:
                return jsonify({"message": "Question not found"})
        else:
            return jsonify({"message": "Missing parameters"})

# Define a route for marking a correct answer and giving an extra point to the answerer


@app.route('/correct/<string:name>', methods=['PUT'])
def correct(name):
    # If the request method is PUT, check if the user is a teacher and mark a correct answer for a question with an id, and give an extra point to the answerer
    if request.method == 'PUT':
        # check if the user is a teacher
        if name in students and students[name]["role"] == "teacher":
            # get the question id from the query string
            question_id = request.args.get("question_id")
            # get the name of the student who gave the answer from the query string
            answerer = request.args.get("answerer")
            if question_id and answerer:  # check if both parameters are provided
                # convert the question id to an integer
                question_id = int(question_id)
                if question_id in questions:  # check if the question id exists
                    # check if there is no correct answer marked yet
                    if questions[question_id]["correct"] is None:
                        # check if the answerer exists in the answers dictionary
                        if answerer in questions[question_id]["answers"]:
                            # mark the correct answer with the name of the answerer
                            questions[question_id]["correct"] = answerer
                            # give an extra point to the answerer
                            students[answerer]["points"] += 1
                            # Get the status of the question
                            status = status(question_id)["status"]
                            # Check if the status is overdue
                            if status == "overdue":
                                # give another extra point to the answerer for answering an overdue question
                                students[answerer]["points"] += 1
                            return jsonify({"message": "Correct answer marked"})
                        else:
                            return jsonify({"message": "Answerer not found"})
                    else:
                        return jsonify({"message": "Correct answer already marked"})
                else:
                    return jsonify({"message": "Question not found"})
            else:
                return jsonify({"message": "Missing parameters"})
        else:
            return jsonify({"message": "User not authorized"})

# Define a route for getting the response rate for each student


@app.route('/response_rate/<string:name>', methods=['GET'])
def response_rate(name):
    # If the request method is GET, return the response rate for the student if it exists, otherwise return an error message
    if request.method == 'GET':
        if name in students:
            response_rate = students[name]["responses"] / \
                students[name]["questions"] * 100
            response_rate = round(response_rate)
            return jsonify({"response_rate": response_rate})
        else:
            return jsonify({"message": "Student not found"})


# Run the app in debug mode
if __name__ == "__main__":
    app.run(debug=True)
