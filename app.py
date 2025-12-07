from flask import Flask, render_template, request, redirect, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_flash_messages' # Required for flash messages

DB_NAME = "hospital.db"

# DB connection context manager
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row # Access columns by name
    return conn

def init_db():
    """Initialize the database with tables if they don't exist."""
    if not os.path.exists(DB_NAME):
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Patients Table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                gender TEXT,
                age INTEGER,
                phone TEXT,
                address TEXT
            )
        ''')

        # Doctors Table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS doctors (
                doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                specialization TEXT,
                phone TEXT,
                email TEXT
            )
        ''')

        # Appointments Table
        cur.execute('''
             CREATE TABLE IF NOT EXISTS appointments (
                appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                doctor_id INTEGER,
                appointment_date TEXT,
                appointment_time TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients (patient_id),
                FOREIGN KEY (doctor_id) REFERENCES doctors (doctor_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("Database initialized successfully.")

# Initialize DB on start
init_db()

# -------------------- ROUTES --------------------

@app.route('/')
def home():
    return render_template('index.html')

# --- PATIENTS ---
@app.route('/patients')
def show_patients():
    try:
        conn = get_db_connection()
        patients = conn.execute('SELECT * FROM patients').fetchall()
        conn.close()
        return render_template('patients.html', patients=patients)
    except Exception as e:
        flash(f"Error fetching patients: {e}", "error")
        return render_template('patients.html', patients=[])

@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        try:
            name = request.form['name']
            gender = request.form['gender']
            age = request.form['age']
            phone = request.form['phone']
            address = request.form['address']

            conn = get_db_connection()
            conn.execute(
                "INSERT INTO patients (name, gender, age, phone, address) VALUES (?, ?, ?, ?, ?)",
                (name, gender, age, phone, address)
            )
            conn.commit()
            conn.close()
            flash("Patient added successfully!", "success")
        except Exception as e:
            flash(f"Error adding patient: {e}", "error")
        return redirect('/patients')
            
    return render_template('add_patient.html')

# --- DOCTORS ---
@app.route('/doctors')
def show_doctors():
    try:
        conn = get_db_connection()
        doctors = conn.execute('SELECT * FROM doctors').fetchall()
        conn.close()
        return render_template('doctors.html', doctors=doctors)
    except Exception as e:
        flash(f"Error fetching doctors: {e}", "error")
        return render_template('doctors.html', doctors=[])

@app.route('/add_doctor', methods=['GET', 'POST'])
def add_doctor():
    if request.method == 'POST':
        try:
            name = request.form['name']
            specialization = request.form['specialization']
            phone = request.form['phone']
            email = request.form['email']

            conn = get_db_connection()
            conn.execute(
                "INSERT INTO doctors (name, specialization, phone, email) VALUES (?, ?, ?, ?)",
                (name, specialization, phone, email)
            )
            conn.commit()
            conn.close()
            flash("Doctor added successfully!", "success")
            return redirect('/doctors')
        except Exception as e:
            flash(f"Error adding doctor: {e}", "error")

    return render_template('add_doctor.html')

# --- APPOINTMENTS ---
@app.route('/appointments')
def show_appointments():
    try:
        conn = get_db_connection()
        query = """
            SELECT a.appointment_id, p.name AS patient_name, d.name AS doctor_name,
                   a.appointment_date, a.appointment_time
            FROM appointments a
            LEFT JOIN patients p ON a.patient_id = p.patient_id
            LEFT JOIN doctors d ON a.doctor_id = d.doctor_id
            ORDER BY a.appointment_date, a.appointment_time
        """
        appointments = conn.execute(query).fetchall()
        conn.close()
        return render_template('appointments.html', appointments=appointments)
    except Exception as e:
        flash(f"Error fetching appointments: {e}", "error")
        return render_template('appointments.html', appointments=[])

@app.route('/add_appointment', methods=['GET', 'POST'])
def add_appointment():
    conn = get_db_connection()
    patients = conn.execute('SELECT * FROM patients').fetchall()
    doctors = conn.execute('SELECT * FROM doctors').fetchall()
    conn.close()

    if request.method == 'POST':
        try:
            patient_id = request.form['patient_id']
            doctor_id = request.form['doctor_id']
            date = request.form['appointment_date']
            time = request.form['appointment_time']

            conn = get_db_connection()
            conn.execute(
                "INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time) VALUES (?, ?, ?, ?)",
                (patient_id, doctor_id, date, time)
            )
            conn.commit()
            conn.close()
            flash("Appointment scheduled successfully!", "success")
            return redirect('/appointments')
        except Exception as e:
            flash(f"Error scheduling appointment: {e}", "error")

    return render_template('add_appointment.html', patients=patients, doctors=doctors)

if __name__ == "__main__":
    app.run(debug=True)
