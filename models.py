from sqlalchemy import create_engine, text
from flask import request,Flask,redirect,url_for
from datetime import datetime, time, date
from flask_bcrypt import Bcrypt
from datetime import datetime


engine = create_engine("mysql+pymysql://root:mysqlpassword@127.0.0.1:3306/hospital_management")
connection = engine.connect() 

app = Flask(__name__)
bcrypt=Bcrypt(app)

def get(email):
    query = text("select email from users where email = :email")
    result = connection.execute(query,{'email':email})
    return result.fetchall()


def get_user_name(email):
    query = text("SELECT name FROM users WHERE email = :email")
    result = connection.execute(query, {'email': email})
    user = result.fetchone()  # Fetch the first row
    if user:
        return user['name']  # Assuming 'name' is the column name in your 'users' table
    else:
        return None  # Return None if no user with the given email is found

def get_patient_data():
    query = text("SELECT * FROM patient ")
    result = connection.execute(query)
    return result.fetchall()

def room_patient():
    query = text("SELECT p.patient_id, p.p_name, p.p_gender, p.p_age, p.address, r.room_id, r.in_date, r.out_date from patient p join patient_room r on p.patient_id = r.patient_id")
    result = connection.execute(query)
    return result.fetchall()

def get_pharmacy_data():
    query = text("SELECT * FROM pharmacy")
    result = connection.execute(query)
    return result.fetchall()

def get_billing_data():
    query = text("SELECT * FROM bill")
    result = connection.execute(query)
    return result.fetchall()

def get_transaction_details():
    query = text("SELECT * FROM transaction")
    result = connection.execute(query)
    return result.fetchall()

def add_patient():
    if request.method == 'POST':
     p_name=request.form.get('p_name')
     address=request.form.get('address')
     p_gender=request.form.get('p_gender')
     p_age=request.form.get('p_age')
     query=text("insert into Patient (p_name,address, p_gender,p_age) values (:p_name,:address, :p_gender,:p_age)")
     connection.execute(query,{'p_name':p_name,'address':address,'p_gender':p_gender,'p_age':p_age})
     connection.commit()
     return redirect(url_for('patient'))
    return redirect(url_for('patient'))

def add_doctor():
    if request.method == 'POST':
     doc_name=request.form.get('doc_name')
     doc_age=request.form.get('doc_age')
     doc_gender=request.form.get('doc_gender')
     doc_address=request.form.get('doc_address')
     doc_remuneration=request.form.get('doc_remuneration')
     doc_specialisation=request.form.get('doc_specialisation')
     doc_cabin_no=request.form.get('doc_cabin_no')
     doc_floorno=request.form.get('doc_floorno')
     
     
     query=text("insert into doctor (doc_name, doc_age, doc_gender, doc_address, doc_remuneration, doc_specialisation, doc_cabin_no, doc_floorno) values (:doc_name, :doc_age, :doc_gender, :doc_address, :doc_remuneration, :doc_specialisation, :doc_cabin_no, :doc_floorno)")
     connection.execute(query,{'doc_name':doc_name,'doc_age':doc_age,'doc_gender':doc_gender,'doc_address':doc_address,'doc_remuneration':doc_remuneration,'doc_specialisation':doc_specialisation, 'doc_cabin_no': doc_cabin_no, 'doc_floorno': doc_floorno})
     connection.commit()
     return redirect(url_for('doctors'))
    return redirect(url_for('doctors'))

def add_research():
    if request.method == 'POST':
     r_name=request.form.get('r_name')
     r_age=request.form.get('r_age')
     r_gender=request.form.get('r_gender')
     r_address=request.form.get('r_address')
     r_joining=request.form.get('r_joining')
     r_stiphend=request.form.get('r_stiphend')
     r_field=request.form.get('r_field')
     
     
     query=text("insert into research_interns (r_name, r_age, r_address, r_joining, r_stiphend, r_field, r_gender) values (:r_name, :r_age, :r_address, r_joining, :r_stiphend, :r_field, :r_gender)")
     connection.execute(query,{'r_name':r_name,'r_age':r_age,'r_address':r_address, 'r_stiphend':r_stiphend,'r_field':r_field, 'r_gender': r_gender, 'r_joining': r_joining})
     connection.commit()
     return redirect(url_for('research'))
    return redirect(url_for('research'))


def get_doctor_data():
    query = text("SELECT * FROM doctor")
    result = connection.execute(query)
    return result.fetchall()

def get_equip_data():
    query = text("SELECT * FROM equipment")
    result = connection.execute(query)
    return result.fetchall()

def get_billing_data():
    # Establish a new connection within the function
    with engine.connect() as connection:
        query = text("SELECT * FROM bill;")
        result = connection.execute(query)
        return result.fetchall()

def get_research_interns_data():
    query = text("SELECT * FROM research_interns")
    result = connection.execute(query)
    return result.fetchall()

def allot_room(room_id, patient_id, in_date, out_date):
    try:
        query = text("INSERT INTO patient_room (room_id, patient_id, in_date, out_date) VALUES (:room_id, :patient_id, :in_date, :out_date)")
        connection.execute(query, {
            'room_id': room_id,
            'patient_id': patient_id, 
            'in_date': in_date,
            'out_date': out_date
        })
        connection.commit()
        return True  # Room successfully allotted
    except Exception as e:
        print(f"Error allotting room: {e}")
        connection.rollback()  # Roll back the transaction in case of error
        return False  # Room allotment failed




def get_room_alloted(room_id):
    try:
        query = text("SELECT COUNT(*) FROM patient_room WHERE room_id=:room_id")
        count = connection.execute(query, {'room_id': room_id}).fetchone()[0]
        return count
    except Exception as e:
        print(f"Error getting room allotment count: {str(e)}")
        return -1  # Return a default value in case of an error

def get_room_occupancy(room_id):
    try:
        query = text("SELECT occupancy FROM room WHERE room_id=:room_id")
        result = connection.execute(query, {'room_id': room_id}).fetchone()
        if result:
            return result[0]  # Return the occupancy value if the room exists
        else:
            return 0  # Return 0 if the room doesn't exist
    except Exception as e:
        print(f"Error getting room occupancy: {str(e)}")
        return -1  # Return a default value in case of an error

    

def insert_appointment(appointment_date, appointment_time):
    # Combine the appointment date with the appointment time to create a full datetime object
    full_datetime = datetime.combine(appointment_date, appointment_time)
    
    # Now, you can insert the full datetime into the database
    query = text("INSERT INTO appointment (appointment_date, appointment_time) VALUES (:appointment_date, :appointment_time)")
    result = connection.execute(query, {
        'appointment_date': full_datetime,
        'appointment_time': full_datetime  # Use the full datetime object
    })
    connection.commit()
    
    # Get the ID of the newly inserted appointment
    appointment_id = result.lastrowid
    
    # Return the appointment ID
    return appointment_id





def insert_appointment_patient(appointment_id, patient_id, doc_id):
    query = text("INSERT INTO patient_appointment (appointment_id, patient_id, doc_id) VALUES (:appointment_id, :patient_id, :doc_id)")
    connection.execute(query, {
        'appointment_id': appointment_id,
        'patient_id': patient_id,
        'doc_id': doc_id
    })
    connection.commit()

from sqlalchemy import text
import datetime

from datetime import datetime

from datetime import datetime, time
from sqlalchemy import text

from sqlalchemy import text

from sqlalchemy import text

def appointcheck(doc_id, patient_id, appointment_date, appointment_time):
    formatted_time = appointment_time.strftime('%H:%M:%S')  # Format time as 'HH:MM:SS' string

    query = text("""
                SELECT COUNT(*)
                FROM appointment a JOIN patient_appointment p ON a.appointment_id = p.appointment_id
                WHERE 
                    (p.doc_id = :doc_id AND
                    a.appointment_date = :appointment_date AND
                    TIME(a.appointment_time) = :appointment_time)
    """)

    result = connection.execute(query, {
        'doc_id': doc_id,
        'appointment_date': appointment_date,
        'appointment_time': formatted_time  # Pass the formatted time string
    }).fetchone()

    existing = result[0] if result else 0  # Access the count value or default to 0 if no result
    print(existing)
    if existing > 0:
        return False  # Appointment exists for the same doctor, time, and date
    else:
        return True  # Appointment slot is available


    
def user_exist(email):
    with engine.connect() as connection:
        query = text("select count(*) from users where email=:email ")
        exist = connection.execute(query, {'email': email}).fetchone()[0]
        return exist > 0
    
def not_user_exist(email):
    query = text("select count(*) from users where email=:email ")
    exist = connection.execute(query, {
        'email': email
    }).fetchone()[0]
    if exist==0:
        return True
    else:
        return False
    

# def get_patient_id_from_email(email):
#     query=text("SELECT patient_id from patient WHERE email=:email")
#     result = connection.execute(query, {'email':email}).fetchone()

#     if result:
#         patient_id = result[0]
#         return patient_id
#     else:
#         return False;



def get_patient_id_from_email(email):
    query = text("SELECT id FROM users WHERE email = :email")
    result = connection.execute(query, {'email': email}).fetchone()

    if result:
        return result[0]  # Return the first column value from the result (assuming it's the patient ID)
    else:
        return None




def check_password(email, password):
    query = text("SELECT password FROM users WHERE email=:email")
    result = connection.execute(query, {'email': email}).fetchone()
    
    if result:
        hashed_password = result[0]
        return bcrypt.check_password_hash(hashed_password, password)
    else:
        return False



def insert_user(name, email, password_hash, age, gender, weight, height, blood_group, user_address, user_contact, relation, s_name, secondary_contact, secondary_address):
        query = text("INSERT INTO users (name, email, password_hash, age, gender, weight, height, blood_group, user_address, user_contact, relation, s_name, secondary_contact, secondary_address) VALUES (:name, :email, :password_hash, :age, :gender, :weight, :height, :blood_group, :user_address, :user_contact, :relation, :s_name, :secondary_contact, :secondary_address)")
        connection.execute(query, {
            'name': name,
            'email': email,
            'password_hash': password_hash,
            'age': age,
            'gender': gender,
            'weight': weight,
            'height': height,
            'blood_group': blood_group,
            'user_address': user_address,
            'user_contact': user_contact,
            'relation': relation,
            's_name': s_name,
            'secondary_contact': secondary_contact,
            'secondary_address': secondary_address,
        })
        connection.commit()

def add_medicine():
    if request.method == 'POST':
     med_gen_name=request.form.get('med_gen_name')
     med_scientific_name=request.form.get('med_scientific_name')
     med_qty=request.form.get('med_qty')
     med_price=request.form.get('med_price')
     with engine.connect() as connection:
            with connection.begin() as transaction:
                query=text("insert into pharmacy (med_gen_name,med_scientific_name,med_qty,med_price) values (:med_gen_name,:med_scientific_name,:med_qty,:med_price);")
                connection.execute(query,{'med_gen_name': med_gen_name,'med_scientific_name':med_scientific_name,'med_qty':med_qty,'med_price':med_price})
                transaction.commit()
                return redirect(url_for('pharmacy'))
                #return redirect(url_for('patient'))

def add_equipment():
    if request.method == 'POST':
     equip_name=request.form.get('equip_name')
     equip_cost=request.form.get('equip_cost')
     equip_qty=request.form.get('equip_qty')
     roomid=request.form.get('roomid')
     with engine.connect() as connection:
            with connection.begin() as transaction:
                query=text("insert into equipment (equip_name,equip_cost,equip_qty,roomid) values (:equip_name,:equip_cost,:equip_qty,:roomid);")
                connection.execute(query,{'equip_name':equip_name,'equip_cost':equip_cost,'equip_qty':equip_qty,'roomid':roomid})
                transaction.commit()
                return redirect(url_for('equipment'))
                #return redirect(url_for('patient'))
