"""Billing calculations assembled from related hospital tables."""
from database import get_db


def calculate_patient_bill(patient_id):
    """Calculate consultation, room, medicine and laboratory charges."""
    db = get_db()
    consultation = db.execute("SELECT COALESCE(SUM(d.consultation_fee),0) FROM appointments a JOIN doctors d ON a.doctor_id=d.doctor_id WHERE a.patient_id=? AND a.status!='Cancelled'", (patient_id,)).fetchone()[0]
    room = db.execute("SELECT COALESCE(SUM((julianday(COALESCE(discharge_date,date('now')))-julianday(admit_date)+1)*r.charge_per_day),0) FROM admissions a JOIN rooms r ON a.room_id=r.room_id WHERE a.patient_id=?", (patient_id,)).fetchone()[0]
    medicine = db.execute('SELECT COALESCE(SUM(m.price*pr.quantity),0) FROM prescriptions pr JOIN appointments a ON pr.appointment_id=a.appointment_id JOIN medicines m ON pr.medicine_id=m.medicine_id WHERE a.patient_id=?', (patient_id,)).fetchone()[0]
    lab = db.execute('SELECT COALESCE(SUM(cost),0) FROM lab_tests WHERE patient_id=?', (patient_id,)).fetchone()[0]
    parts = {'consultation': round(consultation, 2), 'room': round(room, 2), 'medicine': round(medicine, 2), 'lab': round(lab, 2)}
    parts['grand_total'] = round(sum(parts.values()), 2)
    return parts


def create_bill(patient_id):
    """Calculate and save a new pending bill for a patient."""
    parts = calculate_patient_bill(patient_id)
    cursor = get_db().execute('INSERT INTO billing(patient_id,consultation_total,room_total,medicine_total,lab_total,grand_total) VALUES(?,?,?,?,?,?)', (patient_id, parts['consultation'], parts['room'], parts['medicine'], parts['lab'], parts['grand_total']))
    get_db().commit()
    return cursor.lastrowid
