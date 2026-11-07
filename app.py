"""MediCore hospital management system - Flask application entry point."""
import os
from functools import wraps
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db, query_db, execute_db, init_db, close_db
from services.validators import valid_phone, valid_email, required_fields
from services.appointments import book_appointment
from services.billing import calculate_patient_bill, create_bill

app = Flask(__name__)
# Set a long random SECRET_KEY in the hosting provider's environment settings.
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'local-development-key-change-before-deployment')
app.teardown_appcontext(close_db)

USERS = {
    'admin': {'password': generate_password_hash('Admin@123'), 'role': 'Admin'},
    'reception': {'password': generate_password_hash('Reception@123'), 'role': 'Receptionist'},
    'doctor': {'password': generate_password_hash('Doctor@123'), 'role': 'Doctor'},
}


def login_required(view):
    """Protect a route so only authenticated users can access it."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    """Restrict management actions to the admin role."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get('role') != 'Admin':
            flash('Admin access is required for this action.', 'error')
            return redirect(url_for('dashboard'))
        return view(*args, **kwargs)
    return wrapped


@app.route('/')
def home():
    """Send authenticated users to dashboard and others to login."""
    return redirect(url_for('dashboard' if 'username' in session else 'login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Authenticate a demo user using Werkzeug password hashes."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = USERS.get(username)
        if user and check_password_hash(user['password'], password):
            session.update(username=username, role=user['role'])
            flash(f"Welcome to MediCore, {username.title()}!", 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid username or password.', 'error')
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Clear the login session."""
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Display hospital KPIs and chart-ready aggregate data."""
    db = get_db()
    stats = {
        'patients': db.execute('SELECT COUNT(*) FROM patients').fetchone()[0],
        'appointments': db.execute("SELECT COUNT(*) FROM appointments WHERE date=date('now') AND status='Scheduled'").fetchone()[0],
        'beds': db.execute('SELECT COALESCE(SUM(availability),0) FROM rooms').fetchone()[0],
        'revenue': db.execute("SELECT COALESCE(SUM(grand_total),0) FROM billing WHERE status='Paid'").fetchone()[0],
        'low_stock': db.execute('SELECT COUNT(*) FROM medicines WHERE stock<15').fetchone()[0],
        'doctors': db.execute('SELECT COUNT(*) FROM doctors').fetchone()[0],
    }
    weekly = db.execute("SELECT date,COUNT(*) total FROM appointments WHERE date>=date('now','-6 day') GROUP BY date ORDER BY date").fetchall()
    departments = db.execute("SELECT dep.name,COALESCE(SUM(d.consultation_fee),0) revenue FROM departments dep LEFT JOIN doctors d ON dep.dept_id=d.dept_id LEFT JOIN appointments a ON d.doctor_id=a.doctor_id AND a.status='Completed' GROUP BY dep.dept_id").fetchall()
    upcoming = db.execute("SELECT * FROM doctor_schedule_view WHERE date>=date('now') ORDER BY date,time LIMIT 6").fetchall()
    return render_template('dashboard.html', stats=stats, weekly=weekly, departments=departments, upcoming=upcoming)


MODULES = {
    'patients': {'table': 'patients', 'pk': 'patient_id', 'title': 'Patients', 'fields': [('name','Full name','text'),('age','Age','number'),('gender','Gender','select'),('blood_group','Blood group','text'),('phone','Phone','text'),('address','Address','text')], 'columns': ['patient_id','name','age','gender','blood_group','phone','registered_on']},
    'doctors': {'table': 'doctors', 'pk': 'doctor_id', 'title': 'Doctors', 'fields': [('name','Doctor name','text'),('specialization','Specialization','text'),('phone','Phone','text'),('email','Email','email'),('dept_id','Department','department'),('consultation_fee','Consultation fee','number'),('status','Status','status')], 'columns': ['doctor_id','name','specialization','phone','email','dept_id','consultation_fee','status']},
    'departments': {'table': 'departments', 'pk': 'dept_id', 'title': 'Departments', 'fields': [('name','Department name','text'),('floor','Floor','text')], 'columns': ['dept_id','name','floor','head_doctor_id']},
    'medicines': {'table': 'medicines', 'pk': 'medicine_id', 'title': 'Medicines', 'fields': [('name','Medicine name','text'),('stock','Stock','number'),('price','Unit price','number'),('expiry_date','Expiry date','date')], 'columns': ['medicine_id','name','stock','price','expiry_date']},
    'rooms': {'table': 'rooms', 'pk': 'room_id', 'title': 'Rooms', 'fields': [('room_type','Room type','roomtype'),('bed_count','Bed count','number'),('charge_per_day','Charge per day','number'),('availability','Available beds','number')], 'columns': ['room_id','room_type','bed_count','charge_per_day','availability']},
}


def module_rows(module):
    """Fetch all rows for a configured CRUD module."""
    config = MODULES[module]
    return query_db(f"SELECT * FROM {config['table']} ORDER BY {config['pk']} DESC")


@app.route('/<module>', methods=['GET', 'POST'])
@login_required
def crud_module(module):
    """Provide create, read, update and delete for core master tables."""
    if module not in MODULES:
        abort(404)
    config = MODULES[module]
    if request.method == 'POST':
        if session.get('role') != 'Admin' and module in ('doctors','departments','medicines','rooms'):
            flash('Only an admin can modify this module.', 'error')
            return redirect(url_for('crud_module', module=module))
        data = request.form.to_dict()
        missing = required_fields(data, [field[0] for field in config['fields']])
        if missing:
            flash('Please complete all required fields.', 'error')
        elif module == 'patients' and not valid_phone(data['phone']):
            flash('Enter a valid 10-digit Indian mobile number.', 'error')
        elif module == 'doctors' and (not valid_phone(data['phone']) or not valid_email(data['email'])):
            flash('Enter a valid phone number and email address.', 'error')
        else:
            try:
                edit_id = data.pop('edit_id', '')
                fields = [f[0] for f in config['fields']]
                values = [data.get(field) for field in fields]
                if edit_id:
                    assignments = ','.join(f'{field}=?' for field in fields)
                    execute_db(f"UPDATE {config['table']} SET {assignments} WHERE {config['pk']}=?", values + [edit_id])
                    flash(f"{config['title']} record updated.", 'success')
                else:
                    placeholders = ','.join('?' for _ in fields)
                    execute_db(f"INSERT INTO {config['table']} ({','.join(fields)}) VALUES ({placeholders})", values)
                    flash(f"{config['title']} record added.", 'success')
                return redirect(url_for('crud_module', module=module))
            except Exception as exc:
                flash(f'Unable to save record: {exc}', 'error')
    edit_id = request.args.get('edit')
    edit_row = query_db(f"SELECT * FROM {config['table']} WHERE {config['pk']}=?", (edit_id,), one=True) if edit_id else None
    return render_template(f'{module}.html', config=config, rows=module_rows(module), edit_row=edit_row, departments=query_db('SELECT * FROM departments'))


@app.route('/<module>/delete/<int:record_id>', methods=['POST'])
@login_required
@admin_required
def delete_record(module, record_id):
    """Delete a record from an allowed master-data table."""
    if module not in MODULES:
        abort(404)
    config = MODULES[module]
    try:
        execute_db(f"DELETE FROM {config['table']} WHERE {config['pk']}=?", (record_id,))
        flash('Record deleted.', 'success')
    except Exception:
        flash('Record cannot be deleted because related records depend on it.', 'error')
    return redirect(url_for('crud_module', module=module))


@app.route('/appointments', methods=['GET', 'POST'])
@login_required
def appointments():
    """Book appointments and list scheduled consultations."""
    if request.method == 'POST':
        try:
            book_appointment(request.form['patient_id'], request.form['doctor_id'], request.form['date'], request.form['time'], request.form['reason'])
            flash('Appointment booked successfully.', 'success')
        except (ValueError, KeyError) as exc:
            flash(str(exc) or 'Please complete all fields.', 'error')
        except Exception as exc:
            flash(f'Booking failed: {exc}', 'error')
        return redirect(url_for('appointments'))
    rows = query_db('SELECT * FROM doctor_schedule_view ORDER BY date DESC,time')
    return render_template('appointments.html', rows=rows, patients=query_db('SELECT patient_id,name FROM patients'), doctors=query_db("SELECT doctor_id,name,specialization FROM doctors WHERE status='Available'"))


@app.route('/appointments/status/<int:appointment_id>', methods=['POST'])
@login_required
def appointment_status(appointment_id):
    """Update appointment status."""
    status = request.form.get('status')
    if status in ('Scheduled','Completed','Cancelled'):
        execute_db('UPDATE appointments SET status=? WHERE appointment_id=?', (status, appointment_id))
        flash('Appointment status updated.', 'success')
    return redirect(url_for('appointments'))


@app.route('/admissions', methods=['GET','POST'])
@login_required
def admissions():
    """Admit patients to available rooms and discharge them."""
    if request.method == 'POST':
        room_id = request.form.get('room_id')
        room = query_db('SELECT availability FROM rooms WHERE room_id=?', (room_id,), one=True)
        if not room or room['availability'] < 1:
            flash('No beds are available in the selected room.', 'error')
        else:
            try:
                execute_db('INSERT INTO admissions(patient_id,room_id,admit_date,diagnosis) VALUES(?,?,?,?)', (request.form['patient_id'], room_id, request.form['admit_date'], request.form['diagnosis']))
                flash('Patient admitted and bed reserved.', 'success')
            except Exception as exc:
                flash(f'Admission failed: {exc}', 'error')
        return redirect(url_for('admissions'))
    rows = query_db('SELECT a.*,p.name patient_name,r.room_type,r.charge_per_day FROM admissions a JOIN patients p ON a.patient_id=p.patient_id JOIN rooms r ON a.room_id=r.room_id ORDER BY a.admission_id DESC')
    return render_template('admissions.html', rows=rows, patients=query_db('SELECT patient_id,name FROM patients'), rooms=query_db('SELECT * FROM rooms WHERE availability>0'), today=date.today().isoformat())


@app.route('/admissions/discharge/<int:admission_id>', methods=['POST'])
@login_required
def discharge(admission_id):
    """Discharge a patient safely and let the trigger release the bed."""
    admission = query_db(
        'SELECT admit_date, discharge_date FROM admissions WHERE admission_id=?',
        (admission_id,), one=True
    )
    if admission is None:
        flash('Admission record was not found.', 'error')
    elif admission['discharge_date'] is not None:
        flash('This patient has already been discharged.', 'warning')
    elif admission['admit_date'] > date.today().isoformat():
        flash(
            'Cannot discharge this patient because the admission date is in the future. '
            'Correct the admission date and try again.',
            'error'
        )
    else:
        try:
            execute_db(
                "UPDATE admissions SET discharge_date=date('now','localtime') "
                'WHERE admission_id=? AND discharge_date IS NULL',
                (admission_id,)
            )
            flash('Patient discharged; room availability updated automatically.', 'success')
        except Exception:
            app.logger.exception('Unable to discharge admission %s', admission_id)
            flash('Discharge could not be completed. Check the admission date and room record.', 'error')
    return redirect(url_for('admissions'))


@app.route('/prescriptions', methods=['GET','POST'])
@login_required
def prescriptions():
    """Create prescriptions and automatically reduce medicine stock."""
    if request.method == 'POST':
        try:
            medicine_id = request.form['medicine_id']
            quantity = int(request.form['quantity'])
            medicine = query_db('SELECT stock FROM medicines WHERE medicine_id=?', (medicine_id,), one=True)
            if quantity < 1 or not medicine or medicine['stock'] < quantity:
                raise ValueError('Insufficient medicine stock or invalid quantity.')
            execute_db('INSERT INTO prescriptions(appointment_id,medicine_id,dosage,days,quantity) VALUES(?,?,?,?,?)', (request.form['appointment_id'], medicine_id, request.form['dosage'], request.form['days'], quantity))
            flash('Prescription saved. Medicine stock reduced by database trigger.', 'success')
        except Exception as exc:
            flash(f'Unable to save prescription: {exc}', 'error')
        return redirect(url_for('prescriptions'))
    rows = query_db('SELECT pr.*,m.name medicine_name,a.date,p.name patient_name FROM prescriptions pr JOIN medicines m ON pr.medicine_id=m.medicine_id JOIN appointments a ON pr.appointment_id=a.appointment_id JOIN patients p ON a.patient_id=p.patient_id ORDER BY pr.prescription_id DESC')
    return render_template('prescriptions.html', rows=rows, appointments=query_db('SELECT a.appointment_id,a.date,p.name patient_name FROM appointments a JOIN patients p ON a.patient_id=p.patient_id'), medicines=query_db('SELECT * FROM medicines WHERE stock>0'))


@app.route('/lab-tests', methods=['GET','POST'])
@login_required
def lab_tests():
    """Record laboratory tests and their results."""
    if request.method == 'POST':
        try:
            execute_db('INSERT INTO lab_tests(patient_id,test_name,result,test_date,cost) VALUES(?,?,?,?,?)', (request.form['patient_id'],request.form['test_name'],request.form.get('result','Pending'),request.form['test_date'],request.form['cost']))
            flash('Lab test recorded.', 'success')
        except Exception as exc:
            flash(f'Unable to record test: {exc}', 'error')
        return redirect(url_for('lab_tests'))
    return render_template('lab_tests.html', rows=query_db('SELECT l.*,p.name patient_name FROM lab_tests l JOIN patients p ON l.patient_id=p.patient_id ORDER BY test_date DESC'), patients=query_db('SELECT patient_id,name FROM patients'))


@app.route('/billing', methods=['GET','POST'])
@login_required
def billing():
    """Generate bills from linked records and display bill history."""
    if request.method == 'POST':
        try:
            bill_id = create_bill(request.form['patient_id'])
            flash(f'Bill #{bill_id} generated successfully.', 'success')
            return redirect(url_for('invoice', bill_id=bill_id))
        except Exception as exc:
            flash(f'Bill generation failed: {exc}', 'error')
    return render_template('billing.html', rows=query_db('SELECT b.*,p.name patient_name FROM billing b JOIN patients p ON b.patient_id=p.patient_id ORDER BY bill_id DESC'), patients=query_db('SELECT patient_id,name FROM patients'))


@app.route('/invoice/<int:bill_id>')
@login_required
def invoice(bill_id):
    """Show a printable invoice."""
    bill = query_db('SELECT b.*,p.name patient_name,p.phone,p.address FROM billing b JOIN patients p ON b.patient_id=p.patient_id WHERE bill_id=?', (bill_id,), one=True)
    if not bill:
        abort(404)
    return render_template('invoice.html', bill=bill)


@app.route('/billing/pay/<int:bill_id>', methods=['POST'])
@login_required
def pay_bill(bill_id):
    """Mark a pending bill as paid."""
    execute_db("UPDATE billing SET status='Paid' WHERE bill_id=?", (bill_id,))
    flash('Payment marked as received.', 'success')
    return redirect(url_for('billing'))


@app.route('/search')
@login_required
def search():
    """Search patients, doctors and appointments using safe parameters."""
    term = request.args.get('q','').strip()
    date_filter = request.args.get('date','')
    like = f'%{term}%'
    patients = query_db('SELECT * FROM patients WHERE name LIKE ? OR phone LIKE ? ORDER BY name LIMIT 30', (like,like)) if term else []
    doctors = query_db('SELECT d.*,dep.name department FROM doctors d JOIN departments dep ON d.dept_id=dep.dept_id WHERE d.name LIKE ? OR d.specialization LIKE ? ORDER BY d.name LIMIT 30', (like,like)) if term else []
    appointments_rows = query_db('SELECT * FROM doctor_schedule_view WHERE date=? ORDER BY time', (date_filter,)) if date_filter else []
    return render_template('search.html', patients=patients, doctors=doctors, appointments=appointments_rows, term=term, date_filter=date_filter)


@app.route('/sql-playground')
@login_required
def sql_playground():
    """Run eight fixed, read-only SQL examples for DBMS viva practice."""
    examples = [
        ('INNER JOIN: appointments with patient and doctor', 'SELECT a.appointment_id,p.name patient,d.name doctor,a.date,a.time FROM appointments a JOIN patients p ON a.patient_id=p.patient_id JOIN doctors d ON a.doctor_id=d.doctor_id ORDER BY a.date LIMIT 10'),
        ('LEFT JOIN: patients and their appointment counts', 'SELECT p.name,COUNT(a.appointment_id) appointment_count FROM patients p LEFT JOIN appointments a ON p.patient_id=a.patient_id GROUP BY p.patient_id ORDER BY appointment_count DESC LIMIT 10'),
        ('GROUP BY: doctors by department', 'SELECT dep.name department,COUNT(d.doctor_id) doctors FROM departments dep LEFT JOIN doctors d ON dep.dept_id=d.dept_id GROUP BY dep.dept_id'),
        ('HAVING: departments with at least two doctors', 'SELECT dep.name,COUNT(d.doctor_id) total FROM departments dep JOIN doctors d ON dep.dept_id=d.dept_id GROUP BY dep.dept_id HAVING COUNT(d.doctor_id)>=2'),
        ('Aggregate: average consultation fee', 'SELECT ROUND(AVG(consultation_fee),2) average_fee,MIN(consultation_fee) minimum_fee,MAX(consultation_fee) maximum_fee FROM doctors'),
        ('Subquery: doctors charging above average', 'SELECT name,specialization,consultation_fee FROM doctors WHERE consultation_fee>(SELECT AVG(consultation_fee) FROM doctors)'),
        ('View: pending bills', 'SELECT * FROM pending_bills_view ORDER BY grand_total DESC'),
        ('Low stock: medicines below 15 units', 'SELECT name,stock,price FROM medicines WHERE stock<15 ORDER BY stock'),
    ]
    results = []
    for title, sql in examples:
        results.append({'title': title, 'sql': sql, 'rows': query_db(sql)})
    return render_template('sql_playground.html', examples=results)


with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
