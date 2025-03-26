# app.py
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import requests
import json

app = Flask(__name__)
app.secret_key = "your_secret_key" # Change this to a strong random key

# Firebase Database URL - IMPORTANT: Replace this!
FIREBASE_URL = "https://your-firebase-project-default-rtdb.firebaseio.com//"

# ------------------------------------------------------------------------------
# Utility Functions (Python equivalents of R functions)
# ------------------------------------------------------------------------------

def is_valid_email(email):
    """Validate an email address using a simple regex."""
    import re
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(email_regex, email) is not None

def generate_email_key(email):
    """Generate a key from an email by replacing "@" and "." with underscores."""
    return email.replace("@", "_").replace(".", "_")

def fetch_user_by_email(email):
    """Function to fetch user data from Firebase by email"""
    key = generate_email_key(email)
    url = f"{FIREBASE_URL}users/{key}.json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data: # Check if data is not None and not empty (Firebase returns None for no data)
            return data
    return None

def update_user_data_firebase(email, updated_data):
    """Function to update user data in Firebase"""
    key = generate_email_key(email)
    url = f"{FIREBASE_URL}users/{key}.json"
    headers = {'Content-Type': 'application/json'}
    response = requests.put(url, json=updated_data, headers=headers)
    return response.status_code == 200

def add_new_user_firebase(email, new_user_data):
    """Function to add new user to Firebase"""
    key = generate_email_key(email)
    url = f"{FIREBASE_URL}users/{key}.json"
    headers = {'Content-Type': 'application/json'}
    response = requests.put(url, json=new_user_data, headers=headers) # Use PUT for creating with a specific key
    return response.status_code == 200


# ------------------------------------------------------------------------------
# Flask Routes - UI and Server Logic (Python equivalents of R server logic)
# ------------------------------------------------------------------------------

@app.route("/", methods=['GET', 'POST'])
def index():
    user_role = session.get('user_role', 'Researcher') # Default role
    if request.method == 'POST':
        session['user_role'] = request.form['user_role']
        user_role = session['user_role']
        return redirect(url_for('index')) # Redirect to refresh sidebar

    return render_template('index.html', user_role=user_role)

@app.route("/shaheen_clinic_supervisor")
def shaheen_clinic_supervisor():
    # In R: htmlOutput("shaheen_clinic_content_supervisor")
    shaheen_clinic_content_supervisor = "<h2>Shaheen Clinic Supervisor Page Content</h2><p>This is content for the Shaheen Clinic Supervisor page.</p>" # Replace with dynamic content if needed
    return render_template('shaheen_clinic_supervisor.html', shaheen_clinic_content_supervisor=shaheen_clinic_content_supervisor)

@app.route("/shaheen_clinic_researcher")
def shaheen_clinic_researcher():
    shaheen_clinic_content_researcher = "<h2>Shaheen Clinic Researcher Page Content</h2><p>This is content for the Shaheen Clinic Researcher page.</p>" # Replace with dynamic content
    return render_template('shaheen_clinic_researcher.html', shaheen_clinic_content_researcher=shaheen_clinic_content_researcher)

@app.route("/shaheen_clinic_admin", methods=['GET', 'POST'])
def shaheen_clinic_admin():
    shaheen_clinic_editor_content = "" # Fetch initial content if needed
    if request.method == 'POST':
        if 'save_shaheen_clinic_page' in request.form:
            shaheen_clinic_editor_content = request.form['shaheen_clinic_editor']
            # In R, you'd save to GCS. Here, you'd save to Firebase or a database.
            # Placeholder save action:
            print("Saving Shaheen Clinic Page Content:", shaheen_clinic_editor_content)
            # You would add Firebase update logic here to save the content
            return redirect(url_for('shaheen_clinic_admin_preview', content=shaheen_clinic_editor_content)) # Redirect to preview

    return render_template('shaheen_clinic_admin.html', shaheen_clinic_editor_content=shaheen_clinic_editor_content)

@app.route("/shaheen_clinic_admin_preview")
def shaheen_clinic_admin_preview():
    content = request.args.get('content', '') # Get content from query parameter
    return render_template('shaheen_clinic_admin_preview.html', shaheen_clinic_content_preview_admin=content)


@app.route("/dashboard")
def dashboard():
    # --- Fetch Data from Firebase ---
    studies_response = requests.get(f"{FIREBASE_URL}studies.json")
    users_response = requests.get(f"{FIREBASE_URL}users.json") # Assuming users are stored under 'users' node

    total_studies_box = 0
    active_studies_box = 0
    completed_studies_box = 0
    team_members_box = 0
    recent_studies_table_data = []

    if studies_response.status_code == 200 and studies_response.json():
        studies_data = studies_response.json()
        total_studies_box = len(studies_data)
        for study_key, study_info in studies_data.items():
            if study_info.get("status") == "Active":  # You'll need to define 'status' in your study data in Firebase
                active_studies_box += 1
            elif study_info.get("status") == "Completed": #  Same for 'Completed' status
                completed_studies_box += 1
            # For recent studies, let's just take the last 5 added (Firebase doesn't guarantee order, so better to order by date if possible)
            recent_studies_table_data.append({
                "title": study_info.get("title", "N/A"),
                "status": study_info.get("status", "N/A"),
                "start_date": study_info.get("start_date", "N/A")
            })
        recent_studies_table_data = recent_studies_table_data[-5:] # Get last 5

    if users_response.status_code == 200 and users_response.json():
        users_data = users_response.json()
        team_members_box = len(users_data)

    # --- Placeholder Plot URLs (You'll need to implement plot generation or use static plots) ---
    completion_plot_url = "url_to_completion_plot.png" # Replace with actual plot URL or generate dynamically
    progress_plot_url = "url_to_progress_plot.png" # Replace with actual plot URL or generate dynamically

    return render_template('dashboard.html',
                           total_studies_box=total_studies_box,
                           active_studies_box=active_studies_box,
                           completed_studies_box=completed_studies_box,
                           team_members_box=team_members_box,
                           recent_studies_table_data=recent_studies_table_data,
                           completion_plot_url=completion_plot_url,
                           progress_plot_url=progress_plot_url)

@app.route("/new_school_supervisor", methods=['GET', 'POST'])
def new_school_supervisor():
    schools_table_supervisor_data = [] # Fetch existing schools from Firebase for Supervisor view

    if request.method == 'POST':
        if 'create_school_supervisor' in request.form:
            school_name = request.form['school_name_supervisor']
            school_description = request.form['school_description_supervisor']
            # Save new school data to Firebase under 'schools' node
            school_data = {"name": school_name, "description": school_description}
            school_key = generate_email_key(school_name) # Or generate a unique ID
            url = f"{FIREBASE_URL}schools/{school_key}.json" # Use school_key as path
            headers = {'Content-Type': 'application/json'}
            response = requests.put(url, json=school_data, headers=headers) # Use PUT for specific key

            if response.status_code == 200:
                print(f"School '{school_name}' created successfully.")
                return redirect(url_for('new_school_supervisor')) # Refresh to show updated table
            else:
                print(f"Error creating school: {response.status_code}")

    # Fetch schools data to display in the table on each page load (GET request)
    schools_data_response = requests.get(f"{FIREBASE_URL}schools.json") # Fetch all schools
    if schools_data_response.status_code == 200 and schools_data_response.json(): # Check if response is OK and not empty
        schools_firebase_data = schools_data_response.json()
        for school_key, school_info in schools_firebase_data.items():
            schools_table_supervisor_data.append({"name": school_info.get("name", "N/A"), "description": school_info.get("description", "N/A")})


    return render_template('new_school_supervisor.html', schools_table_supervisor_data=schools_table_supervisor_data)


@app.route("/new_school_admin", methods=['GET', 'POST'])
def new_school_admin():
    schools_table_admin_data = [] # Fetch existing schools from Firebase

    if request.method == 'POST':
        if 'create_school_admin' in request.form:
            school_name = request.form['school_name_admin']
            school_description = request.form['school_description_admin']
            # Save new school data to Firebase under 'schools' node
            school_data = {"name": school_name, "description": school_description}
            school_key = generate_email_key(school_name) # Or generate a unique ID
            url = f"{FIREBASE_URL}schools/{school_key}.json" # Use school_key as path
            headers = {'Content-Type': 'application/json'}
            response = requests.put(url, json=school_data, headers=headers) # Use PUT for specific key

            if response.status_code == 200:
                print(f"School '{school_name}' created successfully (Admin).")
                return redirect(url_for('new_school_admin')) # Refresh to show updated table
            else:
                print(f"Error creating school (Admin): {response.status_code}")

    # Fetch schools data to display in the table on each page load (GET request)
    schools_data_response = requests.get(f"{FIREBASE_URL}schools.json") # Fetch all schools
    if schools_data_response.status_code == 200 and schools_data_response.json(): # Check if response is OK and not empty
        schools_firebase_data = schools_data_response.json()
        for school_key, school_info in schools_firebase_data.items():
            schools_table_admin_data.append({"name": school_info.get("name", "N/A"), "description": school_info.get("description", "N/A")})


    return render_template('new_school_admin.html', schools_table_admin_data=schools_table_admin_data)


@app.route("/new_study", methods=['GET', 'POST'])
def new_study():
    study_school_choices = []
    study_supervisor_email_choices = []

    # --- Fetch Schools from Firebase ---
    schools_response = requests.get(f"{FIREBASE_URL}schools.json")
    if schools_response.status_code == 200 and schools_response.json():
        schools_data = schools_response.json()
        for school_key, school_info in schools_data.items():
            study_school_choices.append(school_info.get("name", "N/A"))

    # --- Fetch Supervisors from Firebase (assuming users with role 'Supervisor') ---
    users_response = requests.get(f"{FIREBASE_URL}users.json")
    if users_response.status_code == 200 and users_response.json():
        users_data = users_response.json()
        for user_key, user_info in users_data.items():
            if user_info.get("role") == "Supervisor": # Assuming 'role' field exists
                study_supervisor_email_choices.append(user_info.get("email", "N/A"))


    new_studies_table_data = [] # Fetch existing studies for the table

    if request.method == 'POST':
        if 'announce_study' in request.form:
            # ... (rest of your POST handling code for new study - saving to Firebase is already implemented)
            pass # No changes needed in the POST part for now, focus on GET data fetching

    # Fetch studies data for the table (GET request part remains the same)
    studies_data_response = requests.get(f"{FIREBASE_URL}studies.json")
    if studies_data_response.status_code == 200 and studies_data_response.json():
        studies_firebase_data = studies_data_response.json()
        for study_key, study_info in studies_firebase_data.items():
            new_studies_table_data.append({
                "title": study_info.get("title", "N/A"),
                "category": study_info.get("category", "N/A"),
                "school": study_info.get("school", "N/A"),
                "start_date": study_info.get("start_date", "N/A")
            })


    return render_template('new_study.html',
                           study_school_choices=study_school_choices,
                           study_supervisor_email_choices=study_supervisor_email_choices,
                           new_studies_table_data=new_studies_table_data)


@app.route("/join_study", methods=['GET', 'POST'])
def join_study():
    available_studies_table_data = [] # Fetch available studies for the table
    study_choices = [] # For the dropdown

    # Fetch studies for dropdown and table
    studies_data_response = requests.get(f"{FIREBASE_URL}studies.json")
    if studies_data_response.status_code == 200 and studies_data_response.json():
        studies_firebase_data = studies_data_response.json()
        for study_key, study_info in studies_firebase_data.items():
            study_choices.append(study_info.get("title", "N/A"))
            available_studies_table_data.append({
                "title": study_info.get("title", "N/A"),
                "category": study_info.get("category", "N/A"),
                "school": study_info.get("school", "N/A"),
                "start_date": study_info.get("start_date", "N/A")
            })

    if request.method == 'POST':
        if 'request_join' in request.form:
            requested_study = request.form['requested_study']
            member_name = request.form['member_name']
            member_email = request.form['member_email']
            member_role = request.form['member_role']
            other_role = request.form.get('other_role', '') # Use .get to avoid KeyError if not present
            member_comment = request.form['member_comment']

            # Save join request to Firebase (e.g., under 'join_requests' node)
            join_request_data = {
                "study": requested_study,
                "name": member_name,
                "email": member_email,
                "role": member_role if member_role != 'Other' else other_role,
                "comment": member_comment,
                "status": "pending" # Initial status
            }
            request_key = generate_email_key(member_email + "_" + requested_study) # Unique key
            url = f"{FIREBASE_URL}join_requests/{request_key}.json"
            headers = {'Content-Type': 'application/json'}
            response = requests.put(url, json=join_request_data, headers=headers)

            if response.status_code == 200:
                print(f"Join request for study '{requested_study}' by '{member_name}' submitted.")
                return redirect(url_for('join_study')) # Refresh page
            else:
                print(f"Error submitting join request: {response.status_code}")


    return render_template('join_study.html',
                           study_choices=study_choices,
                           available_studies_table_data=available_studies_table_data)


@app.route("/study_announcements")
def study_announcements():
    public_studies_announcements_table_data = []

    # Fetch public studies announcements from Firebase (studies with privacy='public')
    studies_data_response = requests.get(f"{FIREBASE_URL}studies.json")
    if studies_data_response.status_code == 200 and studies_data_response.json():
        studies_firebase_data = studies_data_response.json()
        for study_key, study_info in studies_firebase_data.items():
            if study_info.get("privacy") == 'public':
                public_studies_announcements_table_data.append({
                    "title": study_info.get("title", "N/A"),
                    "category": study_info.get("category", "N/A"),
                    "school": study_info.get("school", "N/A"),
                    "start_date": study_info.get("start_date", "N/A"),
                    "privacy": study_info.get("privacy", "N/A")
                })

    return render_template('study_announcements.html',
                           public_studies_announcements_table_data=public_studies_announcements_table_data)


@app.route("/joined_studies_researcher")
def joined_studies_researcher():
    joined_studies_table_researcher_dt_data = [] # Data for table

    # Placeholder - In real app, filter by researcher's email (session or input)
    member_email_filter_researcher_choices = ["researcher1@example.com", "researcher2@example.com"] # Replace with actual emails
    selected_email = member_email_filter_researcher_choices[0] # Default selected email

    # Fetch join requests and filter for approved/joined studies based on selected email
    join_requests_response = requests.get(f"{FIREBASE_URL}join_requests.json")
    if join_requests_response.status_code == 200 and join_requests_response.json():
        join_requests_data = join_requests_response.json()
        for request_key, request_info in join_requests_data.items():
            if request_info.get("email") == selected_email and request_info.get("status") == "approved": # Filter by email and status
                joined_studies_table_researcher_dt_data.append({
                    "study": request_info.get("study", "N/A"),
                    "role": request_info.get("role", "N/A"),
                    "comment": request_info.get("comment", "N/A"),
                    "status": request_info.get("status", "N/A")
                })

    return render_template('joined_studies_researcher.html',
                           member_email_filter_researcher_choices=member_email_filter_researcher_choices,
                           joined_studies_table_researcher_dt_data=joined_studies_table_researcher_dt_data)


@app.route("/affiliated_schools_researcher")
def affiliated_schools_researcher():
    schools_table_researcher_data = [] # Data for table

    # Fetch schools data for display
    schools_data_response = requests.get(f"{FIREBASE_URL}schools.json")
    if schools_data_response.status_code == 200 and schools_data_response.json():
        schools_firebase_data = schools_data_response.json()
        for school_key, school_info in schools_firebase_data.items():
            schools_table_researcher_data.append({
                "name": school_info.get("name", "N/A"),
                "description": school_info.get("description", "N/A")
            })

    return render_template('affiliated_schools_researcher.html',
                           schools_table_researcher_data=schools_table_researcher_data)


@app.route("/add_app_members_admin", methods=['GET', 'POST'])
def add_app_members_admin():
    app_users_table_admin_data = [] # For displaying current app users
    app_user_supervisor_admin_choices = ["supervisor1@example.com", "supervisor2@example.com"] # Replace with actual supervisors

    if request.method == 'POST':
        if 'add_app_user_admin' in request.form:
            app_user_name_admin = request.form['app_user_name_admin']
            app_user_email_admin = request.form['app_user_email_admin']
            app_user_role_admin = request.form['app_user_role_admin']
            app_user_supervisor_admin = request.form['app_user_supervisor_admin']

            # Create new app user data
            new_app_user_data = {
                "name": app_user_name_admin,
                "email": app_user_email_admin,
                "role": app_user_role_admin,
                "supervisor": app_user_supervisor_admin,
                "account_status": "Active" # Default status
                # ... other default fields as in R code comments
            }

            # Save to Firebase (under 'app_users' node, or 'users' if you structure users differently)
            user_key = generate_email_key(app_user_email_admin) # Use email as key
            url = f"{FIREBASE_URL}users/{user_key}.json" # Assuming 'users' node for app users
            headers = {'Content-Type': 'application/json'}
            response = requests.put(url, json=new_app_user_data, headers=headers) # Use PUT for specific key

            if response.status_code == 200:
                print(f"App user '{app_user_name_admin}' added successfully.")
                return redirect(url_for('add_app_members_admin')) # Refresh page
            else:
                print(f"Error adding app user: {response.status_code}")

    # Fetch app users data to display in table
    app_users_response = requests.get(f"{FIREBASE_URL}users.json") # Fetch from 'users' or your user node
    if app_users_response.status_code == 200 and app_users_response.json():
        app_users_firebase_data = app_users_response.json()
        for user_key, user_info in app_users_firebase_data.items():
            app_users_table_admin_data.append({
                "name": user_info.get("name", "N/A"),
                "email": user_info.get("email", "N/A"),
                "role": user_info.get("role", "N/A"),
                "supervisor": user_info.get("supervisor", "N/A")
            })


    return render_template('add_app_members_admin.html',
                           app_user_supervisor_admin_choices=app_user_supervisor_admin_choices,
                           app_users_table_admin_data=app_users_table_admin_data)


@app.route("/assign_supervisors_admin")
def assign_supervisors_admin():
    return render_template('assign_supervisors_admin.html') # Placeholder

@app.route("/study_progress", methods=['GET', 'POST'])
def study_progress():
    progress_study_choices = ["Study A", "Study B", "Study C"] # Replace with actual studies
    study_progress_table_data = [] # For the table

    if request.method == 'POST':
        if 'update_progress' in request.form:
            progress_study = request.form['progress_study']
            tasks_completed = request.form.getlist('tasks') # Get list of checked tasks
            completion_percentage = request.form['completion_percentage']
            progress_notes = request.form['progress_notes']

            # Save progress data to Firebase (under 'study_progress' node)
            progress_data = {
                "study": progress_study,
                "tasks_completed": tasks_completed,
                "completion_percentage": completion_percentage,
                "notes": progress_notes,
                "last_updated": "TODO: Timestamp" # Add timestamp logic
            }
            progress_key = generate_email_key(progress_study) # Or generate unique ID
            url = f"{FIREBASE_URL}study_progress/{progress_key}.json"
            headers = {'Content-Type': 'application/json'}
            response = requests.put(url, json=progress_data, headers=headers)

            if response.status_code == 200:
                print(f"Progress for study '{progress_study}' updated.")
                return redirect(url_for('study_progress')) # Refresh page
            else:
                print(f"Error updating study progress: {response.status_code}")

    # Fetch study progress data for table
    study_progress_response = requests.get(f"{FIREBASE_URL}study_progress.json")
    if study_progress_response.status_code == 200 and study_progress_response.json():
        study_progress_firebase_data = study_progress_response.json()
        for progress_key, progress_info in study_progress_firebase_data.items():
            study_progress_table_data.append({
                "study": progress_info.get("study", "N/A"),
                "completion_percentage": progress_info.get("completion_percentage", "N/A"),
                "tasks_completed": ", ".join(progress_info.get("tasks_completed", [])), # Join tasks to string
                "notes": progress_info.get("notes", "N/A")
            })


    return render_template('study_progress.html',
                           progress_study_choices=progress_study_choices,
                           study_progress_table_data=study_progress_table_data)


@app.route("/study_protocols", methods=['GET', 'POST'])
def study_protocols():
    protocol_study_choices = ["Study A", "Study B", "Study C"] # Replace with actual studies
    protocol_history_table_data = [] # For history table

    if request.method == 'POST':
        if 'export_protocol' in request.form:
            protocol_study = request.form['protocol_study']
            print(f"Export Protocol requested for: {protocol_study}")
            # In R, you'd generate PDF. Here, use Python PDF libraries (reportlab, etc.) or generate HTML for PDF conversion.
            # Placeholder PDF generation logic:
            pdf_file_url = "/static/dummy_protocol.pdf" # Example static PDF
            return redirect(pdf_file_url) # Redirect to static PDF for download


    # Fetch protocol history (placeholder data for now)
    protocol_history_table_data = [
        {"study": "Study A", "version": "1.0", "date": "2023-01-01", "updated_by": "User 1"},
        {"study": "Study A", "version": "1.1", "date": "2023-02-15", "updated_by": "User 2"},
        # ... more history data
    ]


    return render_template('study_protocols.html',
                           protocol_study_choices=protocol_study_choices,
                           protocol_history_table_data=protocol_history_table_data)


@app.route("/team_management")
def team_management():
    team_study_choices = ["Study A", "Study B", "Study C"] # Replace with actual studies
    pending_study_choices = ["Study X", "Study Y"] # Replace with studies with pending requests
    remove_study_choices = ["Study Z", "Study W"] # Replace with studies for member removal

    team_members_table_data = [] # For current team members table
    pending_requests_ui_data = [] # For pending requests UI
    remove_member_ui_data = [] # For remove member UI

    # Placeholder data for tables and UI elements. Replace with Firebase data fetching.
    team_members_table_data = [
        {"name": "Member 1", "email": "member1@example.com", "role": "Researcher"},
        {"name": "Member 2", "email": "member2@example.com", "role": "Data Analyst"},
        # ... more team members
    ]
    pending_requests_ui_data = [
        {"name": "Request User 1", "email": "req1@example.com", "role": "Researcher", "study": "Study X"},
        {"name": "Request User 2", "email": "req2@example.com", "role": "Statistician", "study": "Study Y"},
        # ... more requests
    ]
    remove_member_ui_data = [
        {"name": "Member to Remove 1", "email": "rem1@example.com", "role": "Researcher", "study": "Study Z"},
        {"name": "Member to Remove 2", "email": "rem2@example.com", "role": "Data Analyst", "study": "Study W"},
        # ... members to remove
    ]


    return render_template('team_management.html',
                           team_study_choices=team_study_choices,
                           pending_study_choices=pending_study_choices,
                           remove_study_choices=remove_study_choices,
                           team_members_table_data=team_members_table_data,
                           pending_requests_ui_data=pending_requests_ui_data,
                           remove_member_ui_data=remove_member_ui_data)


@app.route("/manage_school_studies_supervisor")
def manage_school_studies_supervisor():
    supervisor_school_studies_table_data = [] # For table

    # Placeholder data - In real app, filter studies by supervisor's school affiliation
    supervisor_school_studies_table_data = [
        {"title": "Study S1", "category": "Clinical", "school": "School A", "start_date": "2023-05-01"},
        {"title": "Study S2", "category": "Basic Science", "school": "School A", "start_date": "2023-08-15"},
        # ... more studies for supervisor's school
    ]

    return render_template('manage_school_studies_supervisor.html',
                           supervisor_school_studies_table_data=supervisor_school_studies_table_data)


@app.route("/manage_all_studies_admin")
def manage_all_studies_admin():
    admin_all_studies_table_data = [] # For table

    # Placeholder data - In real app, fetch all studies
    admin_all_studies_table_data = [
        {"title": "Study A1", "category": "Clinical", "school": "School X", "start_date": "2022-12-01"},
        {"title": "Study A2", "category": "Public Health", "school": "School Y", "start_date": "2023-02-20"},
        # ... all studies data
    ]

    return render_template('manage_all_studies_admin.html',
                           admin_all_studies_table_data=admin_all_studies_table_data)


@app.route("/manage_schools_admin")
def manage_schools_admin():
    admin_schools_table_data = [] # For table

    # Fetch schools data for admin view
    schools_data_response = requests.get(f"{FIREBASE_URL}schools.json")
    if schools_data_response.status_code == 200 and schools_data_response.json():
        schools_firebase_data = schools_data_response.json()
        for school_key, school_info in schools_firebase_data.items():
            admin_schools_table_data.append({
                "name": school_info.get("name", "N/A"),
                "description": school_info.get("description", "N/A")
            })

    return render_template('manage_schools_admin.html',
                           admin_schools_table_data=admin_schools_table_data)


@app.route("/firebase_create_school_admin", methods=['POST'])
def firebase_create_school_admin():
    if request.method == 'POST':
        school_name = request.form['firebase_school_name_admin']
        school_description = request.form['firebase_school_description_admin']

        school_data = {"name": school_name, "description": school_description}
        school_key = generate_email_key(school_name) # Or generate unique ID
        url = f"{FIREBASE_URL}schools/{school_key}.json"
        headers = {'Content-Type': 'application/json'}
        response = requests.put(url, json=school_data, headers=headers)

        if response.status_code == 200:
            confirmation_message = f"School '{school_name}' created in Firebase successfully!"
        else:
            confirmation_message = f"Error creating school in Firebase: {response.status_code}"

        return render_template('manage_schools_admin.html', firebase_school_confirmation_admin=confirmation_message)
    else:
        return redirect(url_for('manage_schools_admin')) # Redirect if accessed directly


@app.route("/manage_app_users_admin")
def manage_app_users_admin():
    admin_app_users_table_data = [] # For table

    # Fetch app users data for admin view
    app_users_response = requests.get(f"{FIREBASE_URL}users.json") # Fetch from 'users' or your user node
    if app_users_response.status_code == 200 and app_users_response.json():
        app_users_firebase_data = app_users_response.json()
        for user_key, user_info in app_users_firebase_data.items():
            admin_app_users_table_data.append({
                "name": user_info.get("name", "N/A"),
                "email": user_info.get("email", "N/A"),
                "role": user_info.get("role", "N/A"),
                "supervisor": user_info.get("supervisor", "N/A")
            })

    return render_template('manage_app_users_admin.html',
                           admin_app_users_table_data=admin_app_users_table_data)


@app.route("/societies_network")
def societies_network():
    forum_topics_list_content = "<ul><li>Topic 1</li><li>Topic 2</li></ul>" # Placeholder
    community_posts_display_content = "<p>Post 1...</p><p>Post 2...</p>" # Placeholder
    available_societies_list_content = "<ul><li>Society A</li><li>Society B</li></ul>" # Placeholder

    return render_template('societies_network.html',
                           forum_topics_list_content=forum_topics_list_content,
                           community_posts_display_content=community_posts_display_content,
                           available_societies_list_content=available_societies_list_content)


@app.route("/complete_user_profile", methods=['GET', 'POST'])
def complete_user_profile():
    if request.method == 'POST':
        # Fetch data from form
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        date_of_birth = request.form['date_of_birth']
        gender = request.form['gender']
        contact_number = request.form['contact_number']
        current_institution = request.form['current_institution']
        department = request.form['department']
        academic_degree = request.form['academic_degree']
        academic_position = request.form['academic_position']
        research_experience_years = request.form['research_experience_years']
        publications_count = request.form['publications_count']
        research_interests = request.form['research_interests']

        # Assuming you have a way to know the current user's email (e.g., from session)
        current_user_email = "user@example.com" # Replace with actual current user email from session

        profile_data = {
            "first_name": first_name,
            "last_name": last_name,
            "date_of_birth": date_of_birth,
            "gender": gender,
            "contact_number": contact_number,
            "current_institution": current_institution,
            "department": department,
            "academic_degree": academic_degree,
            "academic_position": academic_position,
            "research_experience_years": int(research_experience_years) if research_experience_years else 0,
            "publications_count": int(publications_count) if publications_count else 0,
            "research_interests": research_interests
        }

        if update_user_data_firebase(current_user_email, profile_data):
            confirmation_message = "Profile updated successfully!"
        else:
            confirmation_message = "Failed to update profile."

        return render_template('complete_user_profile.html', confirmation_message=confirmation_message)

    return render_template('complete_user_profile.html')


@app.route("/manage_users", methods=['GET', 'POST'])
def manage_users():
    user_profile_management_ui_content = "" # Initialize empty content
    update_confirmation_message = ""

    if request.method == 'POST':
        if 'fetch_user_profile' in request.form:
            selected_user_email = request.form['selected_user_email']
            if is_valid_email(selected_user_email):
                user_data = fetch_user_by_email(selected_user_email)
                if user_data:
                    # Render UI with user data
                    user_profile_management_ui_content = render_template('user_profile_form.html', user=user_data)
                else:
                    update_confirmation_message = "User Not Found! No user profile found for the provided email."
            else:
                update_confirmation_message = "Error! Invalid email address."
        elif 'submit_update' in request.form:
            # Process update form submission (similar to R's observeEvent for submit_update)
            update_email = request.form['update_email']
            if not is_valid_email(update_email):
                update_confirmation_message = "Error! Invalid email address."
            else:
                updated_user_data = {
                    "first_name": request.form['update_first_name'],
                    "last_name": request.form['update_last_name'],
                    "date_of_birth": request.form['update_date_of_birth'],
                    "email": update_email,
                    "phone": request.form['update_phone'],
                    "address": request.form['update_address'],
                    "institution": request.form['update_institution'],
                    "department": request.form['update_department'],
                    "role": request.form['update_role'],
                    "research_interests": request.form['update_research_interests'],
                    "publications": int(request.form['update_publications']) if request.form['update_publications'] else 0,
                    "current_projects": request.form['update_current_projects']
                }
                if update_user_data_firebase(update_email, updated_user_data):
                    update_confirmation_message = "Success! User profile updated successfully."
                    # Re-render the user profile form with updated data (optional)
                    user_profile_management_ui_content = render_template('user_profile_form.html', user=updated_user_data)
                else:
                    update_confirmation_message = "Error! Failed to update user profile."

    return render_template('manage_users.html',
                           user_profile_management_ui_content=user_profile_management_ui_content,
                           update_confirmation_message=update_confirmation_message)


@app.route("/add_user", methods=['GET', 'POST'])
def add_user():
    add_confirmation_message = ""
    if request.method == 'POST':
        if 'submit_new' in request.form:
            new_email = request.form['new_email']
            if not is_valid_email(new_email):
                add_confirmation_message = "Error! Invalid email address."
            elif fetch_user_by_email(new_email):
                add_confirmation_message = "Warning! User with this email already exists."
            else:
                new_user_data = {
                    "first_name": request.form['new_first_name'],
                    "last_name": request.form['new_last_name'],
                    "date_of_birth": request.form['new_date_of_birth'],
                    "email": new_email,
                    "phone": request.form['new_phone'],
                    "address": request.form['new_address'],
                    "institution": request.form['new_institution'],
                    "department": request.form['new_department'],
                    "role": request.form['new_role'],
                    "research_interests": request.form['new_research_interests'],
                    "publications": int(request.form['new_publications']) if request.form['new_publications'] else 0,
                    "current_projects": request.form['new_current_projects'],
                    "account_created": "TODO: Date" # Add current date logic
                }
                if add_new_user_firebase(new_email, new_user_data):
                    add_confirmation_message = "Success! New user added successfully."
                else:
                    add_confirmation_message = "Error! Failed to add new user."

    return render_template('add_user.html', add_confirmation_message=add_confirmation_message)


if __name__ == '__main__':
    app.run(debug=True)