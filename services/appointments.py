"""Appointment booking rules."""
from database import get_db


def book_appointment(patient_id, doctor_id, date, time, reason):
    """Book an appointment unless the doctor already has that slot."""
    db = get_db()
    conflict = db.execute("SELECT 1 FROM appointments WHERE doctor_id=? AND date=? AND time=? AND status!='Cancelled'", (doctor_id, date, time)).fetchone()
    if conflict:
        raise ValueError('This doctor already has an appointment in that time slot.')
    cursor = db.execute('INSERT INTO appointments(patient_id,doctor_id,date,time,reason) VALUES(?,?,?,?,?)', (patient_id, doctor_id, date, time, reason))
    db.commit()
    return cursor.lastrowid
