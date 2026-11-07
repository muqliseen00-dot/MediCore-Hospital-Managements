PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS departments (
 dept_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, floor TEXT NOT NULL,
 head_doctor_id INTEGER, FOREIGN KEY(head_doctor_id) REFERENCES doctors(doctor_id) ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS doctors (
 doctor_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, specialization TEXT NOT NULL,
 phone TEXT NOT NULL UNIQUE, email TEXT NOT NULL UNIQUE, dept_id INTEGER NOT NULL,
 consultation_fee REAL NOT NULL CHECK(consultation_fee >= 0), status TEXT NOT NULL DEFAULT 'Available' CHECK(status IN ('Available','On Leave')),
 FOREIGN KEY(dept_id) REFERENCES departments(dept_id)
);
CREATE TABLE IF NOT EXISTS patients (
 patient_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, age INTEGER NOT NULL CHECK(age BETWEEN 0 AND 120),
 gender TEXT NOT NULL CHECK(gender IN ('Male','Female','Other')), blood_group TEXT, phone TEXT NOT NULL,
 address TEXT NOT NULL, registered_on TEXT NOT NULL DEFAULT (date('now'))
);
CREATE TABLE IF NOT EXISTS appointments (
 appointment_id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id INTEGER NOT NULL, doctor_id INTEGER NOT NULL,
 date TEXT NOT NULL, time TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Scheduled' CHECK(status IN ('Scheduled','Completed','Cancelled')),
 reason TEXT NOT NULL, FOREIGN KEY(patient_id) REFERENCES patients(patient_id), FOREIGN KEY(doctor_id) REFERENCES doctors(doctor_id),
 UNIQUE(doctor_id,date,time)
);
CREATE TABLE IF NOT EXISTS rooms (
 room_id INTEGER PRIMARY KEY AUTOINCREMENT, room_type TEXT NOT NULL CHECK(room_type IN ('General','ICU','Private')),
 bed_count INTEGER NOT NULL CHECK(bed_count > 0), charge_per_day REAL NOT NULL CHECK(charge_per_day >= 0),
 availability INTEGER NOT NULL CHECK(availability BETWEEN 0 AND bed_count)
);
CREATE TABLE IF NOT EXISTS admissions (
 admission_id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id INTEGER NOT NULL, room_id INTEGER NOT NULL,
 admit_date TEXT NOT NULL, discharge_date TEXT, diagnosis TEXT NOT NULL,
 FOREIGN KEY(patient_id) REFERENCES patients(patient_id), FOREIGN KEY(room_id) REFERENCES rooms(room_id),
 CHECK(discharge_date IS NULL OR discharge_date >= admit_date)
);
CREATE TABLE IF NOT EXISTS medicines (
 medicine_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, stock INTEGER NOT NULL CHECK(stock >= 0),
 price REAL NOT NULL CHECK(price >= 0), expiry_date TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS prescriptions (
 prescription_id INTEGER PRIMARY KEY AUTOINCREMENT, appointment_id INTEGER NOT NULL, medicine_id INTEGER NOT NULL,
 dosage TEXT NOT NULL, days INTEGER NOT NULL CHECK(days > 0), quantity INTEGER NOT NULL DEFAULT 1 CHECK(quantity > 0),
 FOREIGN KEY(appointment_id) REFERENCES appointments(appointment_id), FOREIGN KEY(medicine_id) REFERENCES medicines(medicine_id)
);
CREATE TABLE IF NOT EXISTS lab_tests (
 test_id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id INTEGER NOT NULL, test_name TEXT NOT NULL,
 result TEXT NOT NULL DEFAULT 'Pending', test_date TEXT NOT NULL, cost REAL NOT NULL CHECK(cost >= 0),
 FOREIGN KEY(patient_id) REFERENCES patients(patient_id)
);
CREATE TABLE IF NOT EXISTS billing (
 bill_id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id INTEGER NOT NULL, consultation_total REAL NOT NULL DEFAULT 0,
 room_total REAL NOT NULL DEFAULT 0, medicine_total REAL NOT NULL DEFAULT 0, lab_total REAL NOT NULL DEFAULT 0,
 grand_total REAL NOT NULL DEFAULT 0, status TEXT NOT NULL DEFAULT 'Pending' CHECK(status IN ('Paid','Pending')),
 bill_date TEXT NOT NULL DEFAULT (date('now')), FOREIGN KEY(patient_id) REFERENCES patients(patient_id)
);
CREATE INDEX IF NOT EXISTS idx_appointments_patient ON appointments(patient_id);
CREATE INDEX IF NOT EXISTS idx_appointments_doctor_date ON appointments(doctor_id,date);
CREATE INDEX IF NOT EXISTS idx_admissions_patient ON admissions(patient_id);
CREATE INDEX IF NOT EXISTS idx_prescriptions_appointment ON prescriptions(appointment_id);
CREATE INDEX IF NOT EXISTS idx_lab_tests_patient ON lab_tests(patient_id);
CREATE INDEX IF NOT EXISTS idx_billing_patient ON billing(patient_id);
CREATE INDEX IF NOT EXISTS idx_patients_phone ON patients(phone);
CREATE INDEX IF NOT EXISTS idx_doctors_phone ON doctors(phone);
CREATE VIEW IF NOT EXISTS doctor_schedule_view AS
 SELECT a.appointment_id, a.date, a.time, a.status, p.name AS patient_name, d.name AS doctor_name, d.specialization
 FROM appointments a JOIN patients p ON a.patient_id=p.patient_id JOIN doctors d ON a.doctor_id=d.doctor_id;
CREATE VIEW IF NOT EXISTS patient_history_view AS
 SELECT p.patient_id,p.name AS patient_name,a.date,a.time,d.name AS doctor_name,a.reason,a.status
 FROM patients p LEFT JOIN appointments a ON p.patient_id=a.patient_id LEFT JOIN doctors d ON a.doctor_id=d.doctor_id;
CREATE VIEW IF NOT EXISTS pending_bills_view AS
 SELECT b.bill_id,p.name AS patient_name,p.phone,b.grand_total,b.bill_date
 FROM billing b JOIN patients p ON b.patient_id=p.patient_id WHERE b.status='Pending';
CREATE TRIGGER IF NOT EXISTS reduce_medicine_stock AFTER INSERT ON prescriptions
 BEGIN
  UPDATE medicines SET stock=stock-NEW.quantity WHERE medicine_id=NEW.medicine_id;
 END;
CREATE TRIGGER IF NOT EXISTS reserve_room_bed AFTER INSERT ON admissions
 WHEN NEW.discharge_date IS NULL
 BEGIN
  UPDATE rooms SET availability=availability-1 WHERE room_id=NEW.room_id AND availability>0;
 END;
CREATE TRIGGER IF NOT EXISTS release_room_bed AFTER UPDATE OF discharge_date ON admissions
 WHEN OLD.discharge_date IS NULL AND NEW.discharge_date IS NOT NULL
 BEGIN
  UPDATE rooms SET availability=MIN(bed_count,availability+1) WHERE room_id=NEW.room_id;
 END;
