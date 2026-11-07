INSERT OR IGNORE INTO departments(dept_id,name,floor) VALUES
(1,'Cardiology','2nd Floor'),(2,'Neurology','3rd Floor'),(3,'Orthopedics','1st Floor'),(4,'Pediatrics','Ground Floor'),(5,'General Medicine','1st Floor');
INSERT OR IGNORE INTO doctors(doctor_id,name,specialization,phone,email,dept_id,consultation_fee,status) VALUES
(1,'Dr. Ananya Rao','Cardiologist','9876501001','ananya@medicore.in',1,800,'Available'),(2,'Dr. Rohan Shetty','Cardiologist','9876501002','rohan@medicore.in',1,750,'Available'),
(3,'Dr. Meera Nair','Neurologist','9876501003','meera@medicore.in',2,900,'Available'),(4,'Dr. Arjun Kumar','Neurologist','9876501004','arjun@medicore.in',2,850,'Available'),
(5,'Dr. Kavya Iyer','Orthopedic','9876501005','kavya@medicore.in',3,700,'Available'),(6,'Dr. Vikram Rao','Orthopedic','9876501006','vikram@medicore.in',3,650,'On Leave'),
(7,'Dr. Pooja Menon','Pediatrician','9876501007','pooja@medicore.in',4,600,'Available'),(8,'Dr. Nikhil Das','Pediatrician','9876501008','nikhil@medicore.in',4,550,'Available'),
(9,'Dr. Sneha Gowda','General Physician','9876501009','sneha@medicore.in',5,500,'Available'),(10,'Dr. Aditya Rao','General Physician','9876501010','aditya@medicore.in',5,450,'Available'),
(11,'Dr. Farah Khan','Cardiologist','9876501011','farah@medicore.in',1,800,'Available'),(12,'Dr. Suresh Bhat','Neurologist','9876501012','suresh@medicore.in',2,900,'Available'),
(13,'Dr. Divya Hegde','Orthopedic','9876501013','divya@medicore.in',3,700,'Available'),(14,'Dr. Rahul Jain','Pediatrician','9876501014','rahul@medicore.in',4,600,'Available'),(15,'Dr. Nandini Pai','General Physician','9876501015','nandini@medicore.in',5,500,'Available');
UPDATE departments SET head_doctor_id=1 WHERE dept_id=1; UPDATE departments SET head_doctor_id=3 WHERE dept_id=2;
UPDATE departments SET head_doctor_id=5 WHERE dept_id=3; UPDATE departments SET head_doctor_id=7 WHERE dept_id=4; UPDATE departments SET head_doctor_id=9 WHERE dept_id=5;
INSERT OR IGNORE INTO patients(patient_id,name,age,gender,blood_group,phone,address,registered_on) VALUES
(1,'Aarav Sharma',34,'Male','B+','9000010001','Jayanagar, Bengaluru','2026-10-01'),(2,'Diya Reddy',28,'Female','O+','9000010002','Indiranagar, Bengaluru','2026-10-02'),
(3,'Vivek Kumar',45,'Male','A+','9000010003','Whitefield, Bengaluru','2026-10-03'),(4,'Ananya Gowda',19,'Female','AB+','9000010004','Rajajinagar, Bengaluru','2026-10-04'),
(5,'Kiran Patil',56,'Male','O-','9000010005','Malleshwaram, Bengaluru','2026-10-05'),(6,'Sneha Kulkarni',31,'Female','B+','9000010006','HSR Layout, Bengaluru','2026-10-06'),
(7,'Rahul Menon',40,'Male','A-','9000010007','BTM Layout, Bengaluru','2026-10-07'),(8,'Ishita Nair',8,'Female','O+','9000010008','JP Nagar, Bengaluru','2026-10-08'),
(9,'Manoj Hegde',62,'Male','B-','9000010009','Vijayanagar, Bengaluru','2026-10-09'),(10,'Pallavi Rao',37,'Female','AB-','9000010010','Banashankari, Bengaluru','2026-10-10'),
(11,'Sanjay Bhat',51,'Male','A+','9000010011','Yelahanka, Bengaluru','2026-10-11'),(12,'Asha Khan',26,'Female','O+','9000010012','Koramangala, Bengaluru','2026-10-12'),
(13,'Pranav Shetty',15,'Male','B+','9000010013','Hebbal, Bengaluru','2026-10-13'),(14,'Lakshmi Iyer',70,'Female','A+','9000010014','Basavanagudi, Bengaluru','2026-10-14'),(15,'Girish Das',43,'Male','O+','9000010015','Electronic City, Bengaluru','2026-10-15');
INSERT OR IGNORE INTO rooms(room_id,room_type,bed_count,charge_per_day,availability) VALUES
(1,'General',20,1200,20),(2,'General',15,1200,15),(3,'ICU',8,5000,8),(4,'ICU',6,5000,6),(5,'Private',10,3000,10),(6,'Private',8,3000,8);
INSERT OR IGNORE INTO medicines(medicine_id,name,stock,price,expiry_date) VALUES
(1,'Paracetamol 500mg',120,2.5,'2027-12-31'),(2,'Amoxicillin 250mg',80,8,'2027-06-30'),(3,'Cetirizine 10mg',65,3,'2027-09-30'),(4,'Pantoprazole 40mg',90,5,'2028-01-31'),(5,'Azithromycin 500mg',45,12,'2027-04-30'),(6,'Metformin 500mg',100,4,'2028-03-31'),(7,'ORS Sachet',150,18,'2027-11-30'),(8,'Vitamin D3',55,9,'2027-08-31'),(9,'Ibuprofen 400mg',70,4,'2027-10-31'),(10,'Cough Syrup',8,65,'2027-05-31'),(11,'Calcium Tablets',40,6,'2028-02-28'),(12,'Amlodipine 5mg',75,7,'2027-12-31'),(13,'Salbutamol Inhaler',25,110,'2027-07-31'),(14,'Iron Folic Acid',95,3,'2028-04-30'),(15,'Antacid Gel',6,45,'2027-06-30');
INSERT OR IGNORE INTO appointments(appointment_id,patient_id,doctor_id,date,time,status,reason) VALUES
(1,1,1,date('now'),'09:00','Completed','Routine cardiac check'),(2,2,3,date('now'),'09:30','Completed','Recurring headache'),(3,3,5,date('now'),'10:00','Completed','Knee pain'),(4,4,7,date('now'),'10:30','Scheduled','Fever'),(5,5,9,date('now'),'11:00','Scheduled','Blood pressure review'),
(6,6,2,date('now','+1 day'),'09:00','Scheduled','Heart screening'),(7,7,4,date('now','+1 day'),'09:30','Scheduled','Migraine'),(8,8,8,date('now','+1 day'),'10:00','Scheduled','Child wellness'),(9,9,10,date('now','+2 day'),'10:30','Scheduled','Diabetes review'),(10,10,11,date('now','+2 day'),'11:00','Scheduled','Chest discomfort'),
(11,11,12,date('now','+3 day'),'09:00','Scheduled','Neurology follow-up'),(12,12,13,date('now','+3 day'),'09:30','Scheduled','Back pain'),(13,13,14,date('now','+4 day'),'10:00','Scheduled','Seasonal allergy'),(14,14,15,date('now','+4 day'),'10:30','Scheduled','General check-up'),(15,15,1,date('now','+5 day'),'11:00','Scheduled','Cardiac consultation');
INSERT OR IGNORE INTO lab_tests(test_id,patient_id,test_name,result,test_date,cost) VALUES
(1,1,'Lipid Profile','Normal',date('now'),450),(2,2,'CBC','Pending',date('now'),300),(3,3,'X-Ray Knee','Pending',date('now'),600),(4,4,'Complete Blood Count','Normal',date('now','-1 day'),300),(5,5,'ECG','Normal',date('now','-1 day'),500),(6,6,'Echocardiogram','Pending',date('now'),1500),(7,7,'MRI Brain','Pending',date('now'),4500),(8,8,'Vitamin D','Normal',date('now'),700),(9,9,'HbA1c','High',date('now'),400),(10,10,'Troponin','Pending',date('now'),900),(11,11,'EEG','Pending',date('now'),1200),(12,12,'Spine X-Ray','Normal',date('now'),600),(13,13,'Allergy Panel','Pending',date('now'),1100),(14,14,'Thyroid Profile','Normal',date('now'),550),(15,15,'ECG','Pending',date('now'),500);
INSERT OR IGNORE INTO billing(bill_id,patient_id,consultation_total,room_total,medicine_total,lab_total,grand_total,status,bill_date) VALUES
(1,1,800,0,0,450,1250,'Paid',date('now','-3 day')),(2,2,900,0,0,300,1200,'Pending',date('now','-2 day')),(3,3,700,0,0,600,1300,'Pending',date('now','-1 day'));
INSERT OR IGNORE INTO rooms(room_id,room_type,bed_count,charge_per_day,availability) VALUES
(7,'General',12,1200,12),(8,'General',10,1200,10),(9,'General',8,1200,8),(10,'General',6,1200,6),(11,'ICU',4,5000,4),(12,'ICU',4,5000,4),(13,'Private',6,3000,6),(14,'Private',5,3000,5),(15,'Private',4,3000,4);
INSERT OR IGNORE INTO admissions(admission_id,patient_id,room_id,admit_date,discharge_date,diagnosis) VALUES
(1,1,1,date('now','-1 day'),NULL,'Observation after cardiac review'),(2,2,2,date('now','-1 day'),NULL,'Migraine observation'),
(3,3,3,date('now','-1 day'),NULL,'Knee surgery recovery'),(4,4,1,date('now','-2 day'),date('now','-1 day'),'Viral fever'),
(5,5,5,date('now','-6 day'),date('now','-3 day'),'Blood pressure monitoring'),(6,6,2,date('now','-5 day'),date('now','-4 day'),'Cardiac observation'),
(7,7,3,date('now','-4 day'),date('now','-2 day'),'Neurological observation'),(8,8,1,date('now','-3 day'),date('now','-2 day'),'Dehydration'),
(9,9,4,date('now','-7 day'),date('now','-4 day'),'Diabetes management'),(10,10,5,date('now','-4 day'),date('now','-2 day'),'Chest pain evaluation'),
(11,11,2,date('now','-3 day'),date('now','-1 day'),'EEG observation'),(12,12,6,date('now','-5 day'),date('now','-3 day'),'Back pain treatment'),
(13,13,1,date('now','-2 day'),date('now','-1 day'),'Allergy observation'),(14,14,3,date('now','-6 day'),date('now','-4 day'),'General weakness'),
(15,15,4,date('now','-3 day'),date('now','-2 day'),'Cardiac observation');
INSERT OR IGNORE INTO prescriptions(prescription_id,appointment_id,medicine_id,dosage,days,quantity) VALUES
(1,1,1,'1 tablet after food',5,2),(2,2,3,'1 tablet at night',3,1),(3,3,9,'1 tablet twice daily',5,2),
(4,4,1,'1 tablet when required',3,2),(5,5,12,'1 tablet daily',30,1),(6,6,4,'1 tablet before breakfast',7,1),
(7,7,5,'1 tablet daily',3,1),(8,8,7,'1 sachet as directed',2,2),(9,9,6,'1 tablet twice daily',30,2),
(10,10,2,'1 capsule twice daily',5,2),(11,11,8,'1 capsule weekly',4,1),(12,12,11,'1 tablet daily',15,1),
(13,13,3,'1 tablet at night',5,1),(14,14,14,'1 tablet daily',30,1),(15,15,13,'2 puffs when required',7,1);
INSERT OR IGNORE INTO billing(bill_id,patient_id,consultation_total,room_total,medicine_total,lab_total,grand_total,status,bill_date) VALUES
(4,4,600,2400,5,300,3305,'Paid',date('now','-5 day')),(5,5,500,3600,7,500,4607,'Pending',date('now','-4 day')),
(6,6,750,1200,5,1500,3455,'Paid',date('now','-4 day')),(7,7,850,10000,24,4500,15374,'Pending',date('now','-3 day')),
(8,8,550,1200,36,700,2486,'Paid',date('now','-3 day')),(9,9,450,3600,8,400,4458,'Paid',date('now','-2 day')),
(10,10,800,6000,16,900,7716,'Pending',date('now','-2 day')),(11,11,900,2400,9,1200,4509,'Paid',date('now','-2 day')),
(12,12,700,6000,6,600,7306,'Pending',date('now','-1 day')),(13,13,600,1200,3,1100,2903,'Paid',date('now','-1 day')),
(14,14,500,9000,6,550,10056,'Pending',date('now','-1 day')),(15,15,800,3600,110,500,5010,'Paid',date('now'));
