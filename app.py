from flask import Flask,redirect,render_template,request,url_for,session
import model
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app=Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'placement-website-secret-key')
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads', 'resumes')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
model.table()

ALLOWED_RESUME_EXTENSIONS = {'pdf', 'doc', 'docx'}


def allowed_resume_file(filename):
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_RESUME_EXTENSIONS


def render_admin_dashboard():
    companies = model.show_all_companies()
    admin_msg = request.args.get('admin_msg', '')

    search_term = request.args.get('search', '').strip()
    sort_by = request.args.get('sort_by', 'newest').strip()
    expiry_filter = request.args.get('expiry_filter', 'all').strip()
    tab = request.args.get('tab', 'apr').strip()

    min_applications_raw = request.args.get('min_applications', '0').strip()
    try:
        min_applications = int(min_applications_raw)
    except ValueError:
        min_applications = 0

    drives = model.show_admin_drive_overview(
        search_term=search_term,
        sort_by=sort_by,
        expiry_filter=expiry_filter,
        min_applications=min_applications
    )

    student_search = request.args.get('student_search', '').strip()
    company_search = request.args.get('company_search', '').strip()
    student_detail = request.args.get('student_detail', '').strip()
    company_detail = request.args.get('company_detail', '').strip()
    students = model.show_admin_students(student_search)
    companies_managed = model.show_admin_companies(company_search)
    pending_companies = [company for company in companies if (company[7] or '').lower() == 'pending']
    app_history = model.show_all_applications_admin()
    total_students, total_companies, total_drives, total_applications = model.admin_counts()
    selected_student = model.get_student_details(student_detail) if student_detail else None
    company_rows = model.get_company_details(company_detail) if company_detail else []
    selected_company = company_rows[0] if company_rows else None

    def parse_datetime(value):
        if not value:
            return None
        value = value.strip().replace('T', ' ')
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y-%m-%d'
        ]
        for fmt in formats:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        return None

    now = datetime.now()
    ongoing_drives = []
    past_drives = []

    for drive in drives:
        response_close = parse_datetime(drive[9])
        drive_status = (drive[14] or '').lower()
        selected_count = drive[16] or 0

        is_expired = response_close is not None and response_close <= now
        is_completed = selected_count > 0
        is_rejected_or_closed = drive_status in ['rejected', 'closed']

        if is_expired or is_completed or is_rejected_or_closed:
            past_drives.append(drive)
        else:
            ongoing_drives.append(drive)

    if expiry_filter == 'active':
        ongoing_drives = [d for d in ongoing_drives]
        past_drives = []
    elif expiry_filter == 'expired':
        past_drives = [d for d in past_drives]
        ongoing_drives = []

    return render_template(
        'admins dashboard.html',
        data=companies,
        pending_companies=pending_companies,
        companies_managed=companies_managed,
        students=students,
        app_history=app_history,
        selected_student=selected_student,
        selected_company=selected_company,
        admin_msg=admin_msg,
        ongoing_drives=ongoing_drives,
        past_drives=past_drives,
        totals={
            'students': total_students,
            'companies': total_companies,
            'drives': total_drives,
            'applications': total_applications
        },
        filters={
            'search': search_term,
            'sort_by': sort_by,
            'expiry_filter': expiry_filter,
            'min_applications': min_applications,
            'student_search': student_search,
            'company_search': company_search,
            'student_detail': student_detail,
            'company_detail': company_detail
        },
        active_tab=tab
    )

@app.route('/')
def home():
    return render_template('starting page.html')

@app.route('/login')
def login(): 
    company_show = request.args.get('company_msg', '')
    return render_template('login.html', company_show=company_show, admin_show='', company_error='', student_show='')

@app.route('/admin_login', methods=['POST'])
def admin_login():
    # Grabbing input specifically from the Admin form
    user = request.form.get('admin-user')
    pw = request.form.get('admin-pass')

    if user == "admin123@gmail.com" and pw =='admin123#':
        return redirect(url_for('ad'))
    else:
        admin_show = "Access Denied: Only ADMIN can enter here."
        return render_template('login.html', admin_show=admin_show, company_show='', company_error='', student_show='')

@app.route('/ad')
def ad(): 
    return render_admin_dashboard()

@app.route('/admin_1p')
def admin_1p():
    return render_admin_dashboard()

@app.route('/company-login', methods=['GET', 'POST'])
def company_login():
    if request.method == 'GET':
        return redirect(url_for('login'))

    gmail = request.form.get('gmail', '').strip()
    password = request.form.get('password', '').strip()

    if not gmail or not password:
        company_error = "Please enter both company email and password."
        return render_template('login.html', company_show='', company_error=company_error, admin_show='', student_show=''), 400

    company = model.check_company_login(gmail, password)
    if company:
        status = (company[2] or '').lower()
        if status == 'approved':
            session['company_gmail'] = gmail
            return redirect(url_for('company_dashboard'))

        if status in ['blacklisted', 'revoked']:
            msg = "Your application is revoked. You cannot access portal."
            return redirect(url_for('login', company_msg=msg))

        if status == 'revoked':
            msg = "Your application is revoked. You cannot access portal."
            return redirect(url_for('login', company_msg=msg))

        msg = "Your application has been sent. You will be given access once approved by admin."
        return redirect(url_for('login', company_msg=msg))

    company_show = "Invalid company email or password."
    return render_template('login.html', company_show='', company_error=company_show, admin_show='', student_show=''), 401

@app.route('/admin-company-status', methods=['POST'])
def admin_company_status():
    gmail = request.form.get('gmail', '').strip()
    new_status = request.form.get('status', '').strip().lower()

    if new_status not in ['approved', 'revoked', 'pending', 'blacklisted']:
        return redirect(url_for('ad', admin_msg='Invalid status value.'))

    if not gmail:
        return redirect(url_for('ad', admin_msg='Company email missing.'))

    model.update_company_status(gmail, new_status)
    return redirect(url_for('ad', admin_msg=f'Status updated to {new_status} for {gmail}.'))


@app.route('/admin-drive-status', methods=['POST'])
def admin_drive_status():
    drive_id_raw = request.form.get('drive_id', '').strip()
    new_status = request.form.get('status', '').strip().lower()

    try:
        drive_id = int(drive_id_raw)
    except ValueError:
        return redirect(url_for('ad', tab='generator', admin_msg='Invalid drive id.'))

    if new_status not in ['approved', 'rejected', 'closed', 'pending']:
        return redirect(url_for('ad', tab='generator', admin_msg='Invalid drive status.'))

    model.update_drive_status(drive_id, new_status)
    return redirect(url_for('ad', tab='generator', admin_msg=f'Drive {drive_id} updated to {new_status}.'))


@app.route('/admin-student-action', methods=['POST'])
def admin_student_action():
    username = request.form.get('username', '').strip()
    action = request.form.get('action', '').strip().lower()

    if not username:
        return redirect(url_for('ad', tab='apr', admin_msg='Student username missing.'))

    current_status = model.get_student_account_status(username)

    if action == 'delete':
        model.admin_delete_student(username)
        return redirect(url_for('ad', tab='apr', admin_msg='Student deleted.'))

    if action == 'reject':
        model.admin_delete_student(username)
        return redirect(url_for('ad', tab='apr', admin_msg='Student registration rejected and deleted.'))

    if action == 'blacklist':
        if current_status != 'active':
            return redirect(url_for('ad', tab='apr', admin_msg='Activate the student before revoking access.'))
        model.admin_update_student_status(username, 'blacklisted')
        return redirect(url_for('ad', tab='apr', admin_msg='Student access revoked.'))

    if action == 'activate':
        model.admin_update_student_status(username, 'active')
        return redirect(url_for('ad', tab='apr', admin_msg='Student activated.'))

    return redirect(url_for('ad', tab='apr', admin_msg='Invalid action.'))


@app.route('/admin-company-action', methods=['POST'])
def admin_company_action():
    gmail = request.form.get('gmail', '').strip()
    action = request.form.get('action', '').strip().lower()

    if not gmail:
        return redirect(url_for('ad', tab='apr', admin_msg='Company email missing.'))

    current_status = model.get_company_status(gmail)

    if action == 'delete':
        model.admin_delete_company(gmail)
        return redirect(url_for('ad', tab='apr', admin_msg='Company deleted.'))

    if action == 'reject':
        model.admin_delete_company(gmail)
        return redirect(url_for('ad', tab='apr', admin_msg='Company registration rejected and deleted.'))

    if action == 'blacklist':
        if current_status != 'approved':
            return redirect(url_for('ad', tab='apr', admin_msg='Approve the company before revoking access.'))
        model.update_company_status(gmail, 'revoked')
        return redirect(url_for('ad', tab='apr', admin_msg='Company access revoked.'))

    if action == 'activate':
        model.update_company_status(gmail, 'approved')
        return redirect(url_for('ad', tab='apr', admin_msg='Company activated.'))

    return redirect(url_for('ad', tab='apr', admin_msg='Invalid action.'))

@app.route('/company-dashboard')
def company_dashboard():
    gmail = session.get('company_gmail')
    if not gmail:
        return redirect(url_for('login'))

    active_tab = request.args.get('tab', 'info').strip()
    selected_drive_id_raw = request.args.get('drive_id', '').strip()
    student_detail = request.args.get('student_detail', '').strip()
    try:
        selected_drive_id = int(selected_drive_id_raw) if selected_drive_id_raw else None
    except ValueError:
        selected_drive_id = None

    data = model.get_company_details(gmail)
    if not data:
        session.pop('company_gmail', None)
        return redirect(url_for('login', company_msg='Company profile not found.'))

    company = data[0] if data else None
    status = (company[8] or '').lower() if company else ''
    if status != 'approved':
        session.pop('company_gmail', None)
        if status in ['revoked', 'blacklisted']:
            msg = "Your application is revoked. You cannot access portal."
        else:
            msg = "Your application has been sent. You will be given access once approved by admin."
        return redirect(url_for('login', company_msg=msg))

    drives = model.show_company_drives(gmail)
    participants = model.show_company_drive_participants(gmail, selected_drive_id) if selected_drive_id else []
    selected_student = model.get_student_details(student_detail) if student_detail else None
    return render_template(
        'company dashboard.html',
        data=data,
        company=company,
        drives=drives,
        active_tab=active_tab,
        selected_drive_id=selected_drive_id,
        participants=participants,
        selected_student=selected_student
    )


@app.route('/create-drive', methods=['POST'])
def create_drive():
    gmail = session.get('company_gmail')
    if not gmail:
        return redirect(url_for('login'))

    company_rows = model.get_company_details(gmail)
    if not company_rows or (company_rows[0][8] or '').lower() != 'approved':
        session.pop('company_gmail', None)
        return redirect(url_for('login', company_msg='Your application has been sent. You will be given access once approved by admin.'))

    job_title = request.form.get('job_title', '').strip()
    drive_type = request.form.get('type', '').strip()
    salary = request.form.get('salary', '').strip()
    location = request.form.get('location', '').strip()
    application_deadline = request.form.get('application_deadline', '').strip()
    response_close_at = request.form.get('response_close_at', '').strip()
    interview_deadline = request.form.get('interview_deadline', '').strip()
    job_description = request.form.get('job_description', '').strip()
    eligibility = request.form.get('eligibility', '').strip()
    skills = request.form.get('skills', '').strip()

    if not all([job_title, drive_type, salary, location, application_deadline, response_close_at, interview_deadline, job_description, eligibility, skills]):
        return redirect(url_for('company_dashboard', tab='generator'))

    model.insert_placement_drive(gmail, job_title, drive_type, salary, location, application_deadline, response_close_at, interview_deadline, job_description, eligibility, skills)
    return redirect(url_for('company_dashboard', tab='past'))


@app.route('/company-drive-action', methods=['POST'])
def company_drive_action():
    gmail = session.get('company_gmail')
    if not gmail:
        return redirect(url_for('login'))

    drive_id_raw = request.form.get('drive_id', '').strip()
    action = request.form.get('action', '').strip().lower()

    try:
        drive_id = int(drive_id_raw)
    except ValueError:
        return redirect(url_for('company_dashboard', tab='past'))

    if action == 'delete':
        model.delete_company_drive(gmail, drive_id)
        return redirect(url_for('company_dashboard', tab='past'))

    if action == 'close':
        model.close_company_drive(gmail, drive_id)
        return redirect(url_for('company_dashboard', tab='past'))

    if action == 'approve-request':
        model.update_drive_status(drive_id, 'pending')
        return redirect(url_for('company_dashboard', tab='past'))

    return redirect(url_for('company_dashboard', tab='past'))


@app.route('/company-edit-drive', methods=['POST'])
def company_edit_drive():
    gmail = session.get('company_gmail')
    if not gmail:
        return redirect(url_for('login'))

    drive_id_raw = request.form.get('drive_id', '').strip()
    try:
        drive_id = int(drive_id_raw)
    except ValueError:
        return redirect(url_for('company_dashboard', tab='past'))

    data = {}
    job_title = request.form.get('job_title', '').strip()
    salary = request.form.get('salary', '').strip()
    location = request.form.get('location', '').strip()
    response_close_at = request.form.get('response_close_at', '').strip()

    if job_title:
        data['job_title'] = job_title
    if salary:
        data['salary'] = salary
    if location:
        data['location'] = location
    if response_close_at:
        data['response_close_at'] = response_close_at

    if data:
        model.edit_company_drive(gmail, drive_id, data)

    return redirect(url_for('company_dashboard', tab='past', drive_id=drive_id))


@app.route('/company-application-status', methods=['POST'])
def company_application_status():
    gmail = session.get('company_gmail')
    if not gmail:
        return redirect(url_for('login'))

    application_id_raw = request.form.get('application_id', '').strip()
    drive_id_raw = request.form.get('drive_id', '').strip()
    new_status = request.form.get('application_status', '').strip().lower()

    try:
        application_id = int(application_id_raw)
        drive_id = int(drive_id_raw)
    except ValueError:
        return redirect(url_for('company_dashboard', tab='past'))

    allowed = ['shortlisted', 'selected', 'rejected', 'not shortlisted', 'not selected']
    if new_status not in allowed:
        return redirect(url_for('company_dashboard', tab='past', drive_id=drive_id))

    if new_status in ['not shortlisted', 'not selected']:
        new_status = 'rejected'

    model.update_company_application_status(gmail, application_id, new_status)
    return redirect(url_for('company_dashboard', tab='past', drive_id=drive_id))


@app.route('/student-placement-status', methods=['POST'])
def student_placement_status():
    gmail = session.get('company_gmail')
    if not gmail:
        return redirect(url_for('login'))

    company_rows = model.get_company_details(gmail)
    if not company_rows or (company_rows[0][8] or '').lower() != 'approved':
        session.pop('company_gmail', None)
        return redirect(url_for('login', company_msg='Your application has been sent. You will be given access once approved by admin.'))

    username = request.form.get('username', '').strip()
    placement_status = request.form.get('placement_status', '').strip().lower()

    if placement_status not in ['shortlisted', 'not shortlisted', 'selected']:
        return redirect(url_for('company_dashboard'))

    if not username:
        return redirect(url_for('company_dashboard'))

    model.update_student_placement_status(username, placement_status)
    return redirect(url_for('company_dashboard'))

@app.route('/cr',methods=["GET","POST"])
def cr():
    if request.method == "POST":
        company_name = request.form.get('company_name', '').strip()
        hr_name = request.form.get('hr_name', '').strip()
        phone = request.form.get('hrnum', '').strip()
        gmail = request.form.get('gmail', '').strip()
        password = request.form.get('password', '').strip()
        website = request.form.get('website', '').strip()
        address = request.form.get('address', '').strip()
        industry = request.form.get('industry', '').strip()
        description = request.form.get('description', '').strip()

        if not all([company_name, hr_name, phone, gmail, password, website, address, industry, description]):
            show = "Please fill all fields before submitting the company registration form."
            return render_template('company_register.html', show=show), 400

        try:
            model.insert_cd(gmail, password, company_name, hr_name, phone, website, industry, address, description)
        except Exception:
            show = "Company email already registered. Try another email."
            return render_template('company_register.html', show=show), 400

        msg = "Your application has been sent. You will be given access once approved by admin."
        return redirect(url_for('login', company_msg=msg))
    return render_template('company_register.html')

@app.route('/edit-ci', methods=["GET", "POST"])
def edit_ci():
    if request.method == "POST":
        gmail = session.get('company_gmail')
        if not gmail:
            return redirect(url_for('login'))

        company_rows = model.get_company_details(gmail)
        if not company_rows:
            session.pop('company_gmail', None)
            return redirect(url_for('login', company_msg='Company profile not found.'))

        current_status = (company_rows[0][8] or '').lower()
        if current_status != 'approved':
            session.pop('company_gmail', None)
            if current_status == 'revoked':
                msg = "Your application is revoked. You cannot access portal."
            else:
                msg = "Your application has been sent. You will be given access once approved by admin."
            return redirect(url_for('login', company_msg=msg))

        company_name = request.form.get('company_name', '').strip()
        hr_name = request.form.get('hr_name', '').strip()
        phone = request.form.get('hrnum', '').strip()
        password = request.form.get('password', '').strip()
        website = request.form.get('website', '').strip()
        address = request.form.get('address', '').strip()
        industry = request.form.get('industry', '').strip()
        description = request.form.get('description', '').strip()

        data = {}

        if company_name:
            data['cname'] = company_name
        if hr_name:
            data['hrname'] = hr_name
        if phone:
            data['hrnum'] = phone
        if password:
            data['password'] = password
        if website:
            data['website'] = website
        if address:
            data['address'] = address
        if industry:
            data['industry'] = industry
        if description:
            data['description'] = description

        if data:
            model.update_dynamic(gmail, data)

        return redirect(url_for('company_dashboard'))

    return redirect(url_for('company_dashboard'))

@app.route('/sr')
def sr():
    return render_template('student_register.html')


@app.route('/sr', methods=['POST'])
def student_register_post():
    name = request.form.get('name', '').strip()
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    college = request.form.get('college', '').strip()
    course = request.form.get('course', '').strip()
    password = request.form.get('password', '').strip()

    if not all([name, username, email, phone, college, course, password]):
        return render_template('student_register.html', show='Please fill all student registration fields.'), 400

    try:
        model.insert_student(username, password, name, email, phone, college, course)
    except Exception:
        return render_template('student_register.html', show='Username already exists. Try another username.'), 400

    return redirect(url_for('login'))

@app.route('/student-login', methods=['POST'])
def student_login():
    student_gmail = request.form.get('student_gmail', '').strip()
    password = request.form.get('password', '').strip()

    if not student_gmail or not password:
        student_show = "Please enter both student gmail and password."
        return render_template('login.html', student_show=student_show, admin_show='', company_show='', company_error=''), 400

    student = model.check_student_login(student_gmail, password)
    if not student:
        student_show = "Invalid student gmail or password."
        return render_template('login.html', student_show=student_show, admin_show='', company_show='', company_error=''), 401

    session['student_username'] = student[0]
    return redirect(url_for('student_dashboard'))


@app.route('/logout-company')
def logout_company():
    session.pop('company_gmail', None)
    return redirect(url_for('login'))


@app.route('/logout-student')
def logout_student():
    session.pop('student_username', None)
    return redirect(url_for('login'))


@app.route('/student-dashboard')
def student_dashboard():
    username = session.get('student_username')
    if not username:
        return redirect(url_for('login'))

    student = model.get_student_details(username)
    if not student:
        session.pop('student_username', None)
        return redirect(url_for('login'))

    search_term = request.args.get('search', '').strip()
    tab = request.args.get('tab', 'Portal').strip()
    company_detail = request.args.get('company_detail', '').strip()

    drives = model.show_student_available_drives(search_term)
    applications = model.show_student_applications(username)
    company_rows = model.get_company_details(company_detail) if company_detail else []
    selected_company = company_rows[0] if company_rows else None

    def parse_datetime(value):
        if not value:
            return None
        value = value.strip().replace('T', ' ')
        formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d']
        for fmt in formats:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        return None

    now = datetime.now()
    ongoing_drives = []
    for drive in drives:
        response_close = parse_datetime(drive[8])
        if response_close is None or response_close > now:
            ongoing_drives.append(drive)

    return render_template(
        'student dasboard.html',
        student=student,
        drives=ongoing_drives,
        applications=applications,
        filters={'search': search_term},
        active_tab=tab,
        selected_company=selected_company
    )


@app.route('/student-apply', methods=['POST'])
def student_apply():
    username = session.get('student_username')
    if not username:
        return redirect(url_for('login'))

    drive_id_raw = request.form.get('drive_id', '').strip()
    try:
        drive_id = int(drive_id_raw)
    except ValueError:
        return redirect(url_for('student_dashboard', tab='generator'))

    model.apply_student_to_drive(drive_id, username)
    return redirect(url_for('student_dashboard', tab='past'))


@app.route('/edit-student', methods=['POST'])
def edit_student():
    username = session.get('student_username')
    if not username:
        return redirect(url_for('login'))

    data = {}

    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    college = request.form.get('college', '').strip()
    course = request.form.get('course', '').strip()
    cgpa = request.form.get('cgpa', '').strip()
    skills = request.form.get('skills', '').strip()
    certifications = request.form.get('certifications', '').strip()
    password = request.form.get('password', '').strip()
    resume_file = request.files.get('resume')

    if name:
        data['name'] = name
    if email:
        data['email'] = email
    if phone:
        data['phone'] = phone
    if college:
        data['college'] = college
    if course:
        data['course'] = course
    if cgpa:
        data['cgpa'] = cgpa
    if skills:
        data['skills'] = skills
    if certifications:
        data['certifications'] = certifications
    if password:
        data['password'] = password

    if resume_file and resume_file.filename:
        if not allowed_resume_file(resume_file.filename):
            return redirect(url_for('student_dashboard', tab='Portal'))
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        safe_name = secure_filename(f"{username}_{resume_file.filename}")
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)
        resume_file.save(save_path)
        model.update_student_resume(username, save_path)

    if data:
        model.update_student_details(username, data)

    return redirect(url_for('student_dashboard'))



if __name__=='__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(debug=debug_mode, port=8000)