import sqlite3 

def connect():
    return sqlite3.connect('database.db')

def table():
    con=connect()
    cur=con.cursor()

    cur.execute("""
        create table if not exists company_details(
                gmail text primary key not null,
                password text not null,
                cname text not null,
                hrname text,
                hrnum text not null,
                website text not null,
                industry text,
                address text,
                description text,
                status text not null
                )
    """)

    cur.execute("""
        create table if not exists placement_d(
                drive_id integer primary key autoincrement,
                gmail text,
                job_title text,
                type text,
                salary text,
                location text,
                created_at text default current_timestamp,
                application_deadline text,
                response_close_at text,
                interview_deadline text,
                job_description text,
                eligibility text,
                status text default 'pending',
                skills text,
                foreign key (gmail) references company_details(gmail)
                )
    """)

    try:
        cur.execute("alter table placement_d add column response_close_at text")
    except sqlite3.OperationalError:
        pass

    try:
        # SQLite ALTER TABLE does not allow non-constant defaults like current_timestamp.
        cur.execute("alter table placement_d add column created_at text")
        cur.execute("update placement_d set created_at = datetime('now') where created_at is null")
    except sqlite3.OperationalError:
        pass

    try:
        cur.execute("alter table placement_d add column status text default 'pending'")
    except sqlite3.OperationalError:
        pass

    cur.execute("""
        create table if not exists placement_applications(
                application_id integer primary key autoincrement,
                drive_id integer not null,
                student_username text not null,
                application_status text default 'applied',
                applied_at text default current_timestamp,
                unique(drive_id, student_username),
                foreign key (drive_id) references placement_d(drive_id),
                foreign key (student_username) references student_details(username)
                )
    """)

    cur.execute("""
        create table if not exists student_details(
                username text primary key not null,
                password text not null,
                name text not null,
                email text not null,
                phone text,
                college text,
                course text,
                cgpa text,
                skills text,
                certifications text,
                placement_status text default 'pending',
                account_status text default 'active',
                resume_path text
                )
    """)

    try:
        cur.execute("alter table student_details add column placement_status text default 'pending'")
    except sqlite3.OperationalError:
        pass

    try:
        cur.execute("alter table student_details add column account_status text default 'active'")
    except sqlite3.OperationalError:
        pass

    try:
        cur.execute("alter table student_details add column resume_path text")
    except sqlite3.OperationalError:
        pass

    con.commit()
    con.close()

def insert_cd(gmail, password, cname, hrname, hrnum, website, industry, address, descriptionn):
    con = connect()
    cur = con.cursor()

    cur.execute("""
        insert into company_details (
            gmail, password, cname, hrname, hrnum, website, industry, address, description, status
        ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
    """, (gmail, password, cname, hrname, hrnum, website, industry, address, descriptionn))


    con.commit()
    con.close()

def check_company_login(gmail, password):
    con = connect()
    cur = con.cursor()

    cur.execute("""
        select gmail, cname, status
        from company_details
        where gmail=? and password=?
    """, (gmail, password))
    company = cur.fetchone()

    con.close()
    return company

def get_company_details(gmail):
    con = connect()
    cur = con.cursor()

    cur.execute("""
        select gmail, cname, hrname, hrnum, website, industry, address, description, status
        from company_details
        where gmail=?
    """, (gmail,))
    data = cur.fetchall()

    con.close()
    return data

def show_all(gmail):
    con = connect()
    cur = con.cursor()

    cur.execute("SELECT * FROM info where gmail=?",(gmail,))
    data = cur.fetchall()

    con.close()
    return data

def update_dynamic(gmail, data):
    con = connect()
    cur = con.cursor()

    query = "UPDATE company_details SET "
    query += ", ".join([f"{key}=?" for key in data.keys()])
    query += " WHERE gmail=?"

    values = list(data.values())
    values.append(gmail)

    cur.execute(query, values)

    con.commit()
    con.close()
    
def show_all_companies():
    con = connect()
    cur = con.cursor()

    cur.execute("""
        select gmail, cname, hrname, hrnum, website, description, industry, status
        from company_details
        order by rowid desc
    """ )
    data = cur.fetchall()

    con.close()
    return data


def update_company_status(gmail, status):
    con = connect()
    cur = con.cursor()

    cur.execute("""
        update company_details
        set status=?
        where gmail=?
    """, (status, gmail))

    con.commit()
    con.close()


def get_company_status(gmail):
    con = connect()
    cur = con.cursor()
    cur.execute("select status from company_details where gmail=?", (gmail,))
    row = cur.fetchone()
    con.close()
    return row[0] if row else None


def insert_student(username, password, name, email, phone, college, course):
    con = connect()
    cur = con.cursor()

    cur.execute("""
        insert into student_details (
            username, password, name, email, phone, college, course, cgpa, skills, certifications, placement_status, account_status, resume_path
        ) values (?, ?, ?, ?, ?, ?, ?, '', '', '', 'pending', 'active', '')
    """, (username, password, name, email, phone, college, course))

    con.commit()
    con.close()


def check_student_login(student_gmail, password):
    con = connect()
    cur = con.cursor()

    cur.execute("""
        select username, name, email
        from student_details
        where email=? and password=? and account_status='active'
    """, (student_gmail, password))
    student = cur.fetchone()

    con.close()
    return student


def get_student_details(username):
    con = connect()
    cur = con.cursor()

    cur.execute("""
        select username, name, password, email, phone, college, course, cgpa, skills, certifications, placement_status, account_status, resume_path
        from student_details
        where username=?
    """, (username,))
    data = cur.fetchone()

    con.close()
    return data


def update_student_details(username, data):
    con = connect()
    cur = con.cursor()

    query = "UPDATE student_details SET "
    query += ", ".join([f"{key}=?" for key in data.keys()])
    query += " WHERE username=?"

    values = list(data.values())
    values.append(username)

    cur.execute(query, values)

    con.commit()
    con.close()


def show_all_students():
    con = connect()
    cur = con.cursor()

    cur.execute("""
        select username, name, email, phone, college, course, cgpa, skills, certifications, placement_status
        from student_details
        order by rowid desc
    """)
    data = cur.fetchall()

    con.close()
    return data


def update_student_placement_status(username, placement_status):
    con = connect()
    cur = con.cursor()

    cur.execute("""
        update student_details
        set placement_status=?
        where username=?
    """, (placement_status, username))

    con.commit()
    con.close()


def get_student_account_status(username):
    con = connect()
    cur = con.cursor()
    cur.execute("select account_status from student_details where username=?", (username,))
    row = cur.fetchone()
    con.close()
    return row[0] if row else None


def insert_placement_drive(gmail, job_title, drive_type, salary, location, application_deadline, response_close_at, interview_deadline, job_description, eligibility, skills):
    con = connect()
    cur = con.cursor()

    cur.execute("""
        insert into placement_d (
            gmail, job_title, type, salary, location, application_deadline, response_close_at, interview_deadline, job_description, eligibility, status, skills
        ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)
    """, (gmail, job_title, drive_type, salary, location, application_deadline, response_close_at, interview_deadline, job_description, eligibility, skills))

    con.commit()
    con.close()


def show_company_drives(gmail):
    con = connect()
    cur = con.cursor()

    cur.execute("""
        select p.drive_id, p.job_title, p.type, p.salary, p.location, p.application_deadline, p.response_close_at, p.interview_deadline, p.job_description, p.eligibility, p.skills, p.status, count(a.application_id)
        from placement_d p
        left join placement_applications a on a.drive_id = p.drive_id
        where p.gmail=?
        group by p.drive_id
        order by p.drive_id desc
    """, (gmail,))
    data = cur.fetchall()

    con.close()
    return data


def show_admin_drive_overview(search_term='', sort_by='newest', expiry_filter='all', min_applications=0):
    con = connect()
    cur = con.cursor()

    query = """
        select
            p.drive_id,
            p.gmail,
            c.cname,
            p.job_title,
            p.type,
            p.salary,
            p.location,
            p.created_at,
            p.application_deadline,
            p.response_close_at,
            p.interview_deadline,
            p.job_description,
            p.eligibility,
            p.skills,
            p.status,
            count(a.application_id) as total_applications,
            sum(case when a.application_status='selected' then 1 else 0 end) as selected_count
        from placement_d p
        left join company_details c on c.gmail = p.gmail
        left join placement_applications a on a.drive_id = p.drive_id
        where 1=1
    """

    params = []

    if search_term:
        query += """
            and (
                lower(p.job_title) like ?
                or lower(p.job_description) like ?
                or lower(p.skills) like ?
            )
        """
        like_term = f"%{search_term.lower()}%"
        params.extend([like_term, like_term, like_term])

    query += """
        group by p.drive_id
        having total_applications >= ?
    """
    params.append(min_applications)

    if sort_by == 'oldest':
        query += " order by p.created_at asc, p.drive_id asc"
    elif sort_by == 'expiry':
        query += " order by p.response_close_at asc, p.drive_id desc"
    else:
        query += " order by p.created_at desc, p.drive_id desc"

    cur.execute(query, params)
    rows = cur.fetchall()

    con.close()

    return rows


def show_student_available_drives(search_term=''):
    con = connect()
    cur = con.cursor()

    query = """
        select
            p.drive_id,
            p.gmail,
            c.cname,
            p.job_title,
            p.type,
            p.salary,
            p.location,
            p.application_deadline,
            p.response_close_at,
            p.job_description,
            p.skills
        from placement_d p
        left join company_details c on c.gmail = p.gmail
        where p.status='approved' and c.status='approved'
    """
    params = []

    if search_term:
        query += """
            and (
                lower(p.job_title) like ?
                or lower(p.job_description) like ?
                or lower(p.skills) like ?
            )
        """
        like_term = f"%{search_term.lower()}%"
        params.extend([like_term, like_term, like_term])

    query += " order by p.drive_id desc"

    cur.execute(query, params)
    data = cur.fetchall()

    con.close()
    return data


def apply_student_to_drive(drive_id, student_username):
    con = connect()
    cur = con.cursor()

    cur.execute("""
        insert or ignore into placement_applications (
            drive_id, student_username, application_status
        ) values (?, ?, 'applied')
    """, (drive_id, student_username))

    con.commit()
    con.close()


def show_student_applications(student_username):
    con = connect()
    cur = con.cursor()

    cur.execute("""
        select
            a.application_id,
            a.applied_at,
            p.drive_id,
            p.job_title,
            c.cname,
            c.gmail,
            p.type,
            p.response_close_at,
            a.application_status,
            p.status
        from placement_applications a
        left join placement_d p on p.drive_id = a.drive_id
        left join company_details c on c.gmail = p.gmail
        where a.student_username=?
        order by a.applied_at desc, a.application_id desc
    """, (student_username,))
    data = cur.fetchall()

    con.close()
    return data


def show_company_drive_participants(gmail, drive_id):
    con = connect()
    cur = con.cursor()

    cur.execute("""
        select
            a.application_id,
            a.applied_at,
            s.username,
            s.name,
            s.email,
            s.college,
            s.course,
            s.cgpa,
            a.application_status
        from placement_applications a
        inner join placement_d p on p.drive_id = a.drive_id
        inner join student_details s on s.username = a.student_username
        where p.gmail=? and a.drive_id=?
        order by a.applied_at desc, a.application_id desc
    """, (gmail, drive_id))
    data = cur.fetchall()

    con.close()
    return data


def update_company_application_status(gmail, application_id, new_status):
    con = connect()
    cur = con.cursor()

    cur.execute("""
        update placement_applications
        set application_status=?
        where application_id=?
          and drive_id in (
              select drive_id
              from placement_d
              where gmail=?
          )
    """, (new_status, application_id, gmail))

    con.commit()
    con.close()


def update_drive_status(drive_id, new_status):
    con = connect()
    cur = con.cursor()
    cur.execute("update placement_d set status=? where drive_id=?", (new_status, drive_id))
    con.commit()
    con.close()


def delete_company_drive(gmail, drive_id):
    con = connect()
    cur = con.cursor()
    cur.execute("delete from placement_applications where drive_id=?", (drive_id,))
    cur.execute("delete from placement_d where drive_id=? and gmail=?", (drive_id, gmail))
    con.commit()
    con.close()


def close_company_drive(gmail, drive_id):
    con = connect()
    cur = con.cursor()
    cur.execute("update placement_d set status='closed' where drive_id=? and gmail=?", (drive_id, gmail))
    con.commit()
    con.close()


def edit_company_drive(gmail, drive_id, data):
    con = connect()
    cur = con.cursor()
    query = "update placement_d set "
    query += ", ".join([f"{key}=?" for key in data.keys()])
    query += " where drive_id=? and gmail=?"
    values = list(data.values())
    values.append(drive_id)
    values.append(gmail)
    cur.execute(query, values)
    con.commit()
    con.close()


def show_admin_students(search=''):
    con = connect()
    cur = con.cursor()
    query = """
        select username, name, email, phone, college, course, cgpa, account_status
        from student_details
        where 1=1
    """
    params = []
    if search:
        query += " and (lower(name) like ? or lower(username) like ? or lower(email) like ? or lower(phone) like ?)"
        like = f"%{search.lower()}%"
        params.extend([like, like, like, like])
    query += " order by rowid desc"
    cur.execute(query, params)
    data = cur.fetchall()
    con.close()
    return data


def show_admin_companies(search=''):
    con = connect()
    cur = con.cursor()
    query = """
        select gmail, cname, hrname, hrnum, website, industry, status
        from company_details
        where 1=1
    """
    params = []
    if search:
        query += " and lower(cname) like ?"
        like = f"%{search.lower()}%"
        params.append(like)
    query += " order by rowid desc"
    cur.execute(query, params)
    data = cur.fetchall()
    con.close()
    return data


def admin_update_student_status(username, account_status):
    con = connect()
    cur = con.cursor()
    cur.execute("update student_details set account_status=? where username=?", (account_status, username))
    con.commit()
    con.close()


def admin_delete_student(username):
    con = connect()
    cur = con.cursor()
    cur.execute("delete from placement_applications where student_username=?", (username,))
    cur.execute("delete from student_details where username=?", (username,))
    con.commit()
    con.close()


def admin_delete_company(gmail):
    con = connect()
    cur = con.cursor()
    cur.execute("delete from placement_applications where drive_id in (select drive_id from placement_d where gmail=?)", (gmail,))
    cur.execute("delete from placement_d where gmail=?", (gmail,))
    cur.execute("delete from company_details where gmail=?", (gmail,))
    con.commit()
    con.close()


def admin_counts():
    con = connect()
    cur = con.cursor()
    cur.execute("select count(*) from student_details")
    students = cur.fetchone()[0]
    cur.execute("select count(*) from company_details")
    companies = cur.fetchone()[0]
    cur.execute("select count(*) from placement_d")
    drives = cur.fetchone()[0]
    cur.execute("select count(*) from placement_applications")
    applications = cur.fetchone()[0]
    con.close()
    return students, companies, drives, applications


def show_all_applications_admin():
    con = connect()
    cur = con.cursor()
    cur.execute("""
        select
            a.application_id,
            a.applied_at,
            a.application_status,
            s.username,
            s.name,
            c.gmail,
            c.cname,
            p.job_title,
            p.drive_id
        from placement_applications a
        left join student_details s on s.username=a.student_username
        left join placement_d p on p.drive_id=a.drive_id
        left join company_details c on c.gmail=p.gmail
        order by a.applied_at desc
    """)
    data = cur.fetchall()
    con.close()
    return data


def update_student_resume(username, resume_path):
    con = connect()
    cur = con.cursor()
    cur.execute("update student_details set resume_path=? where username=?", (resume_path, username))
    con.commit()
    con.close()

if __name__ == "__main__":
    table()