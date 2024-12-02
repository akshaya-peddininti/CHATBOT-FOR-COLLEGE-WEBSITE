from flask import Flask, flash,request, jsonify, render_template, session,redirect, url_for
import nltk
from googletrans import Translator
from flask_session import Session
import re
import json

with open('data.json', 'r') as file:  # Replace 'data.json' with your JSON file path
    data = json.load(file)

nltk.download('punkt')
nltk.download('stopwords')
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

app = Flask(__name__)
app.secret_key = '123'  # Necessary for session management

# Admin credentials (you can store these securely in env variables or a database)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password"

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

stop_words = set(stopwords.words('english'))
translator = Translator()

def clean_input(input_text):
    # Tokenize the text and remove stopwords
    words = word_tokenize(input_text.lower())
    filtered_words = [word for word in words if word not in stop_words]
    return filtered_words
def separate_text_and_links(text):
    """
    Separates text and HTML links. Returns a list where each entry is either plain text or an HTML link.
    """
    # Split the input text based on links
    return re.split(r'(<a [^>]*>.*?</a>)', text)

def translate_only_text_parts(text_parts, target_language):
    """
    Translates only plain text parts while leaving HTML links unchanged.
    """
    translated_parts = []
    for part in text_parts:
        if part.strip().startswith('<a '):  # Check if it's an HTML link
            translated_parts.append(part)  # Keep the link as it is
        else:
            try:
                # Translate the plain text part
                translated_text = translator.translate(part, dest=target_language).text
                translated_parts.append(translated_text)
            except Exception as e:
                translated_parts.append(part)  # Fallback to the original part if translation fails
    return ''.join(translated_parts)


def generate_response(words):
    # Define keywords for different responses
    greeting_keywords = ['hi', 'hello', 'greetings', 'sup', 'what\'s up']
    thanks_keywords = ['stop', 'end', 'exit']
    library_keywords = ['library', 'books', 'study', 'reading']
    department_query_keywords = ['department', 'departments', 'major', 'branch', 'study', 'program']
    academic_calendar_keywords = ['academic', 'calendar', 'schedule', 'events']
    college_info_keywords = ['college', 'institute', 'about', 'MGIT', 'information']
    syllabus_keywords = ['syllabus', 'subjects']
    transport_keywords = ['transport', 'transportation', 'bus']
    placement_keywords=['placements graph','placement report','placement','year-wise placement report']
    examination_center=['exam form','exam registration form']
    course_list_keywords = ['course list', 'ug course list', 'pg course list', 'courses', 'list of courses']
    
    
    department_info = {
        'ece': "Electronics and Communication Engineering (ECE) focuses on electronic devices and software interfaces. The fee for the ECE program is 60000 per semester.",
        'cse': "Computer Science and Engineering (CSE) covers programming, algorithm design, and computer systems. The fee for the CSE program is 60000 per semester.",
        'mec': "Mechanical Engineering (MEC) involves the design and manufacture of physical or automated systems. The fee for the MEC program is 60000 per semester.",
        'civil': "Civil Engineering deals with the design, construction, and maintenance of the environment. The fee for the Civil program is 60000 per semester."
    }

    # Links for different semesters in academic calendar
   
    
    
    

    # Syllabus links for each department and semester
    syllabus_links = {
        'cse': {
            'I & II Semester': "https://mgit.ac.in/wp-content/uploads/2024/04/MR22-CSE-I-II-SEM-SCHEME-AND-SYLLABUS.pdf",
            'III & IV Semester': "https://mgit.ac.in/wp-content/uploads/2024/07/MR22-CSE-III-IV-SEM-SCHEME-AND-SYLLABUS.pdf",
            'V & VIII Semester': "https://mgit.ac.in/wp-content/uploads/2024/07/05-CSE-528.pdf",
            
        },
        'eee': {
            'I & II Semester': "https://mgit.ac.in/wp-content/uploads/2023/11/EEE-MR22-I-and-II-SEM.pdf",
            'III & IV Semester': "https://mgit.ac.in/wp-content/uploads/2023/11/EEE-B.Tech-MR22-Syllabus-III-to-IV-Semesters.pdf",
            'V & VII Semester': "https://mgit.ac.in/wp-content/uploads/2022/11/MR21-III-IV-SEM.pdf",
            
        },
        'it': {
            'I & II Semester': "https://mgit.ac.in/wp-content/uploads/2022/12/IT-I-II-Sem-Scheme-and-Syllabus-Arial-14-11-2022.pdf",
            'III & IV Semester': "https://mgit.ac.in/wp-content/uploads/2023/11/IT-B.Tech-MR22-Syllabus-III-to-IV-Semesters.pdf",
            'V & VIII Semester': "https://mgit.ac.in/wp-content/uploads/2024/03/MR21_UG-IT_V-VIII_Sem_Syllabus.pdf",
            
        },
        'csb': {
            'I & II Semester': "https://mgit.ac.in/wp-content/uploads/2022/12/CSB-I-II-Sem-Scheme-and-Syllabus-Arial-14-11-2022.pdf",
            'III & IV Semester': "https://mgit.ac.in/wp-content/uploads/2023/11/CSB-B.Tech-MR22-Syllabus-III-to-IV-Semesters.pdf",
            'V & VIII Semester': "https://mgit.ac.in/wp-content/uploads/2024/03/MR21-CSBS-V-to-VIII-Scheme-and-Syllabus.pdf"
        }
        
        
    }

    # College information
    college_info = (
        "Mahatma Gandhi Institute of Technology (MGIT) was established by the Chaitanya Bharathi Educational Society (CBES) in 1997. "
        "MGIT has maintained an excellent academic track record and stands among the top engineering colleges in Telangana... "
    )
    academic_calendar_links = data.get("academic_calendar_links", {})
    # Greet new users or check for greetings
    if 'greeted' not in session:
        session['greeted'] = True
        return "Hello, welcome to our college! How can I assist you today?"
    
    if any(word in words for word in greeting_keywords):
        return "Hello again! How can I assist you further?"
    elif any(word in words for word in thanks_keywords):
        return "You're welcome! Have a good day."
    
    elif any(keyword in ' '.join(words) for keyword in library_keywords):
        return ("In the first floor of B-Block in MGIT, the Library & Information Center has grown by leaps and bounds. The original 400 titles and 1000 volumes have now grown to 53,852 volumes and 12,734 titles – an addition of 2500 volumes per year. It is now managed by seven technical and three non-technical members.")
    elif any(keyword in words for keyword in department_query_keywords):
        return "Which department do you want to enquire about? ECE, CSE, MEC, or Civil?"
    
    elif any(keyword in words for keyword in academic_calendar_keywords):
        links_response = "Here are the academic calendar links for different semesters:<br>"
        for semester, link in academic_calendar_links.items():
            links_response += f'<a href="{link}" target="_blank" aria-label="click here for {semester} calendar">{semester}</a><br>'
        return links_response

    elif any(word in words for word in college_info_keywords):
        return college_info

    elif any(word in words for word in syllabus_keywords):
        # Ask for department selection for syllabus
        session['awaiting_syllabus_department'] = True
        return "Please specify the department for syllabus information. Options are CSE, EEE, IT, or CSB."

    # Provide syllabus links if a department is specified after the syllabus prompt
    if 'awaiting_syllabus_department' in session:
        for dept, links in syllabus_links.items():
            if dept in words:
                session.pop('awaiting_syllabus_department', None)
                syllabus_response = f"Syllabus links for {dept.upper()} department:<br>"
                for semester, link in links.items():
                    syllabus_response += f'<a href="{link}" target="_blank" aria-label="click here for {semester}">{semester}</a><br>'
                return syllabus_response

    if any(keyword in words for keyword in transport_keywords):
        transport_link = "https://mgit.ac.in/wp-content/uploads/2024/08/Application-Form_Student-Transport_AY-2024-25.pdf"
        return f"You can find the transport application form  <a href='{transport_link}' target='_blank' aria-label='click here'>Transport Application Form</a>"

    if any(keyword in ' '.join(words) for keyword in examination_center):
        link='https://mgit.ac.in/wp-content/uploads/2024/07/MGIT-Registration-Form-I-III-V-VII-Sem-July-2024-25-01072024.pdf'
        return f'You can find the Exam registration form  <a href="{link}" target="_blank" aria-label="click here">Exam Registration Form</a>'
    
    if any(keyword in ' '.join(words) for keyword in course_list_keywords):
        link="https://mgit.ac.in/ug-pg-course-list/"
        return f"You can find the Course list <a href='{link}' target='_blank' aria-label='click here'>Course List</a>"
    
    if any(keyword in words for keyword in placement_keywords):
        link='https://mgit.ac.in/year-wise-placement/'
        return f"You can find the Year wise Placements report <a href='{link}' target='_blank' aria-label='click here'>Year wise Placements report</a>"

    # Check for specific department information
    for dept_key, dept_info in department_info.items():
        if dept_key in words:
            return dept_info

    # Default response for unrecognized input
    if 'error' not in session:
        session['error'] = True
        return "Sorry, I didn't understand that. Can you please specify your query?"
    
    return "Please specify your query or contact our support for more help."
def translate_text(text, target_language):
    return translator.translate(text, dest=target_language).text
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash("Login successful!", "success")
            return redirect(url_for('admin_page'))
        else:
            flash("Invalid credentials!", "danger")
    return render_template('admin3.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin_page():
    if not session.get('admin_logged_in'):
        flash("You must be logged in as admin to access this page.", "warning")
        return redirect(url_for('admin3.html'))

    if request.method == 'POST':
        # Logic to update JSON file
        try:
            updated_content = request.form.get('json_content')
            with open('data.json', 'w') as json_file:
                json_file.write(updated_content)
            flash("JSON file updated successfully!", "success")
        except Exception as e:
            flash(f"Error updating JSON file: {e}", "danger")

    # Read JSON file to display in admin page
    try:
        with open('data.json', 'r') as json_file:
            current_content = json_file.read()
    except Exception as e:
        current_content = "{}"
        flash(f"Error reading JSON file: {e}", "danger")

    return render_template('admin_page.html', json_content=current_content)

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash("Logged out successfully!", "success")
    return redirect(url_for('home'))
@app.route('/')
def home():
    session.clear()  # Correct method to reset session at new conversation start
    return render_template('index2.html')
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_input = data.get('message')
        
        # Ensure user_input is provided
        if not user_input:
            return jsonify({'response': 'Error: Message is missing or empty'}), 400

        language = data.get('language', 'en')  # Default to English
        
        # Translate user input to English for processing if needed
        if language != 'en':
            try:
                translated_input = translate_text(user_input, 'en')
                # Check if translation returned None or empty string
                if not translated_input:
                    return jsonify({'response': 'Error: Translation failed.'}), 500
                user_input = translated_input
            except Exception as e:
                return jsonify({'response': f'Error in translating message: {str(e)}'}), 500

        # Process the cleaned input and generate response
        cleaned_words = clean_input(user_input)
        response = generate_response(cleaned_words)

        # Translate the response back to the user's preferred language if necessary
        if language != 'en':
            text_parts = separate_text_and_links(response)
            response = translate_only_text_parts(text_parts, language)

        return jsonify({'response': response})

    except Exception as e:
        return jsonify({'response': f'Error processing your message: {str(e)}'}), 500
    
# Path to your JSON file
JSON_FILE_PATH = 'data.json'

def load_json_data():
    """Load existing JSON data from the file."""
    try:
        with open(JSON_FILE_PATH, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}  # Return an empty dict if the file doesn't exist

def save_json_data(data):
    """Save the updated JSON data back to the file."""
    with open(JSON_FILE_PATH, 'w') as file:
        json.dump(data, file, indent=4)

@app.route('/admin/update_json', methods=['POST'])
def update_json():
    """Admin route to append content to JSON."""
    if not request.json or 'new_content' not in request.json:
        return jsonify({'status': 'error', 'message': 'No content provided'}), 400

    new_content = request.json['new_content']  # The new content to append
    try:
        # Load existing data
        current_data = load_json_data()

        # Append the new content
        if isinstance(current_data, list):
            current_data.append(new_content)
        elif isinstance(current_data, dict):
            # Assuming the new content is a dictionary with a key-value pair
            current_data.update(new_content)
        else:
            return jsonify({'status': 'error', 'message': 'Unsupported JSON structure'}), 400

        # Save the updated data
        save_json_data(current_data)
        return jsonify({'status': 'success', 'message': 'Content appended successfully'}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
if __name__== '__main__':
    app.run(debug=True, use_reloader=False)