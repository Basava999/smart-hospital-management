from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

# DB connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",              # <-- your MySQL username
        password="Basava@999", # <-- your MySQL password
        database="hospital_management"
    )

# -------------------- PATIENTS --------------------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add_patient', methods=['POST'])
def add_patient():
    name = request.form['name']
    gender = request.form['gender']
    age = request.form['age']
    phone = request.form['phone']
    address = request.form['address']

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO patients (name, gender, age, phone, address) VALUES (%s,%s,%s,%s,%s)",
        (name, gender, age, phone, address)
    )
    conn.commit()
    conn.close()
    return redirect('/patients')

@app.route('/patients')
def show_patients():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM patients")
    patients = cur.fetchall()
    conn.close()
    return render_template('patients.html', patients=patients)

# -------------------- DOCTORS --------------------
@app.route('/doctors')
def show_doctors():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM doctors")
    doctors = cur.fetchall()
    conn.close()
    return render_template('doctors.html', doctors=doctors)

@app.route('/add_doctor', methods=['GET','POST'])
def add_doctor():
    if request.method == 'POST':
        name = request.form['name']
        specialization = request.form['specialization']
        phone = request.form['phone']
        email = request.form['email']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO doctors (name, specialization, phone, email) VALUES (%s,%s,%s,%s)",
            (name, specialization, phone, email)
        )
        conn.commit()
        conn.close()
        return redirect('/doctors')
    return render_template('add_doctor.html')

# -------------------- APPOINTMENTS --------------------
@app.route('/appointments')
def show_appointments():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT a.appointment_id, p.name AS patient_name, d.name AS doctor_name,
               a.appointment_date, a.appointment_time
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN doctors d ON a.doctor_id = d.doctor_id
        ORDER BY a.appointment_date, a.appointment_time
    """)
    appointments = cur.fetchall()
    conn.close()
    return render_template('appointments.html', appointments=appointments)

@app.route('/add_appointment', methods=['GET','POST'])
def add_appointment():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM patients")
    patients = cur.fetchall()
    cur.execute("SELECT * FROM doctors")
    doctors = cur.fetchall()
    conn.close()

    if request.method == 'POST':
        patient_id = request.form['patient_id']
        doctor_id = request.form['doctor_id']
        date = request.form['appointment_date']
        time = request.form['appointment_time']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time) VALUES (%s,%s,%s,%s)",
            (patient_id, doctor_id, date, time)
        )
        conn.commit()
        conn.close()
        return redirect('/appointments')

    return render_template('add_appointment.html', patients=patients, doctors=doctors)

if __name__ == "__main__":
    app.run(debug=True)
