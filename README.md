# MediCore – Hospital Management System

**Academic mini-project:** Python Programming + Database Management Systems (DBMS) Lab  
**Stack:** Python 3.10+, Flask, SQLite3, Jinja2, HTML, CSS and vanilla JavaScript.

## Problem statement
Hospitals handle patient registrations, doctor schedules, appointments, admissions, medicines, diagnostics and billing. When these activities are maintained separately, staff can face duplicate bookings, slow record retrieval and billing mistakes. MediCore provides one simple web application backed by a relational database to manage these workflows and demonstrate core DBMS concepts.

## Objectives
1. Design a relational database with primary keys, foreign keys, constraints, indexes and views.
2. Implement CRUD operations using Python functions and parameterized SQLite queries.
3. Prevent appointment conflicts and validate user input.
4. Demonstrate triggers for medicine stock and room availability.
5. Calculate patient bills using joins and aggregate functions.
6. Provide role-based login, dashboard reporting, search and a SQL viva playground.

## Features
- Login roles: Admin, Receptionist and Doctor (demo accounts below).
- Dashboard with patient count, today's appointments, available beds, paid revenue and low-stock count.
- CRUD: patients, doctors, departments, medicines and rooms.
- Appointment booking with same-doctor/same-date/same-time conflict detection.
- Patient admission and discharge; SQLite triggers reserve/release beds.
- Prescriptions; SQLite trigger deducts medicine stock.
- Lab-test registration and result tracking.
- Automatic billing from consultation, room, medicine and lab records; printable invoice.
- Global search for patients/doctors by name or phone and appointments by date.
- SQL Playground with eight read-only examples.

## ER diagram
See [`docs/ER_diagram.md`](docs/ER_diagram.md). The diagram shows all ten tables and their relationships.

## Tables and database objects
| Table | Purpose |
|---|---|
| departments | Department name, floor and head doctor |
| doctors | Doctor details, speciality, department and consultation fee |
| patients | Demographic and contact details |
| appointments | Patient-doctor time slots and appointment status |
| rooms | Room category, total beds, charge and available beds |
| admissions | Patient stay, room allocation and discharge date |
| medicines | Medicine inventory, price and expiry |
| prescriptions | Medicines prescribed during an appointment |
| lab_tests | Patient diagnostics, results, date and cost |
| billing | Itemized totals, grand total and payment status |

**Views:** `doctor_schedule_view`, `patient_history_view`, `pending_bills_view`.  
**Triggers:** `reduce_medicine_stock`, `reserve_room_bed`, `release_room_bed`.  
**Indexes:** foreign-key lookup columns and patient/doctor phone fields.

## Normalization (3NF)
- **1NF:** Each column stores one atomic value; there are no repeating groups or arrays in a row.
- **2NF:** Every table has a single-column primary key, and non-key attributes depend on the complete key.
- **3NF:** Department, doctor, patient, medicine and room facts are stored in their own tables. Appointment, admission, prescription and billing rows refer to those entities through foreign keys rather than repeating descriptive details. Thus non-key attributes depend on the key, the whole key and nothing but the key. The billing table intentionally stores a generated financial snapshot for an invoice; it is a transaction record, not a replacement for the source tables.

## Setup and execution
Requirements: Python 3.10 or newer.

```bash
cd medicore
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
Open **http://127.0.0.1:5000**. On first launch, `schema.sql` creates the database and `seed.sql` inserts Bengaluru-themed demo data. The SQLite file `medicore.db` is generated automatically in the project folder.

## Default login credentials
| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `Admin@123` |
| Receptionist | `reception` | `Reception@123` |
| Doctor | `doctor` | `Doctor@123` |

Passwords are hashed with Werkzeug at application startup. These are classroom demo credentials; change the secret key and configure persistent user storage before real deployment.

## Screenshots
Capture screenshots after running the project and add them here, for example:
- `docs/screenshots/login.png` – Login page
- `docs/screenshots/dashboard.png` – KPI dashboard
- `docs/screenshots/patients.png` – Patient CRUD
- `docs/screenshots/sql-playground.png` – SQL examples

## Security and validation notes
All form values used in SQL statements are passed as bound parameters. Dynamic table and column identifiers are selected only from the fixed `MODULES` allow-list. Password verification uses Werkzeug hashes. This is an educational demo: add CSRF protection, persistent user administration, audit logging, HTTPS, stronger session secrets and production-grade authorization before deployment. The doctor role is a demonstration role and should be restricted further in a production system.

## Future scope
- Persistent user/role tables with per-route permissions.
- Email/SMS appointment reminders and patient portal.
- PDF invoice export, payment gateway and insurance support.
- Doctor availability calendars and room-wise occupancy reports.
- REST API, automated tests, audit trails and deployment with HTTPS.

## One-minute viva explanation
“Good morning. My project is MediCore, a Hospital Management System developed using Python Flask and SQLite. It manages patients, doctors, departments, appointments, rooms, admissions, medicines, prescriptions, lab tests and billing. I designed ten relational tables using primary keys, foreign keys, UNIQUE, NOT NULL and CHECK constraints. The design follows 3NF by separating entities and connecting them through foreign keys. I used Python functions for database connections, validation, appointment booking and bill calculation. Parameterized SQL queries help prevent SQL injection. Three views simplify common reports. Triggers automatically reduce medicine stock after a prescription and update bed availability during admission and discharge. The dashboard uses aggregate queries, and the SQL Playground demonstrates joins, GROUP BY, HAVING, subqueries and aggregate functions. This project demonstrates database design, CRUD operations and Python function-based programming in one application.”

## Exam mapping (100 marks)
| Exam component | Evidence in this project | Marks preparation |
|---|---|---:|
| Procedure | Problem statement, ER diagram, schema, normalization, setup and algorithm explanations | 15 |
| Execution | Login, dashboard, CRUD, booking conflict, admission/discharge, trigger tests, prescriptions, lab, billing, search and SQL playground | 70 |
| Viva-Voce | 30 prepared questions, SQL concepts, Python functions, Flask routing and database design | 15 |

**Suggested execution demonstration:** Login as admin → dashboard → add a patient → book two appointments to demonstrate conflict detection → admit and discharge a patient to show room triggers → prescribe medicine to show stock deduction → create invoice → run SQL Playground queries.
