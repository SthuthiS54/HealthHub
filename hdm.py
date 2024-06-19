from flask import Flask, abort
from flask import render_template,request,flash,redirect,session,send_file,jsonify
from flask import url_for
from models import get_patient_data,get_pharmacy_data,get_billing_data,get_transaction_details,add_patient,get_doctor_data,get_room_alloted,get_room_occupancy,allot_room,get_research_interns_data,insert_appointment,insert_appointment_patient,appointcheck,user_exist,not_user_exist,insert_user,check_password,add_equipment,add_medicine,get_equip_data, add_doctor, get_patient_id_from_email, add_research, room_patient
from forms import PatientForm,RegistrationForm,LoginForm,RoomAllotForm,AppointmentForm,MedForm,TransForm,MedicineForm,EquipmentForm, DoctorForm, Research
from sqlalchemy import text,create_engine,engine
from sqlalchemy.exc import SQLAlchemyError
import qrcode
import random
from io import BytesIO
from flask_wtf.csrf import CSRFProtect
from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_login import current_user,LoginManager,logout_user
from werkzeug.security import generate_password_hash
from flask_login import login_required
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from werkzeug.security import check_password_hash
from sqlalchemy import Column, Integer, String
from flask import Flask, render_template, request
from werkzeug.exceptions import Unauthorized




Base = declarative_base()
Session = scoped_session(sessionmaker())


app = Flask(__name__)


engine = create_engine("mysql+pymysql://root:mysqlpassword@127.0.0.1:3306/hospital_management")
connection = engine.connect()

Session.configure(bind=engine)

# Set a secret key for the application
app.secret_key = '72c54091f475bc54a71759f5085c405d'



app.config['WTF_CSRF_ENABLED'] = False

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
csrf = CSRFProtect()
csrf.init_app(app)

bcrypt=Bcrypt(app)

from flask_login import UserMixin
class User(UserMixin, Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128))  # Store the hashed password
    name = Column(String(255))
    
    def __init__(self, email, password):
        self.email = email
        self.password_hash = generate_password_hash(password)  # Hash the password during initialization

    def check_password(self, password):
        # Verify the provided password against the stored hash
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)

    @classmethod
    def query(cls):
        return Session.query(cls)




login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    # Load user from the database based on user_id
    return User.query().get(int(user_id))  # Use the query method to retrieve the user by ID


@app.route("/")
def home():
    return render_template("index.html")




@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        
        # Query the database for the user based on the provided email
        user = User.query().filter_by(email=email).first()
        
        if user and user.check_password(password):
            # Log in the user using Flask-Login's login_user function
            login_user(user)
            session['email'] = email

            user_name = User.query().filter_by(email=email).with_entities(User.name).scalar() 
            
            # Store the user's name in the session
            session['name'] = user_name
            
            flash('Logged in successfully!', 'success')
            if email == 'abhinayasrinivas30@gmail.com' and password == 'Abhi':
                return redirect(url_for('admin'))  # Redirect to the admin page
            else:
                return redirect(url_for('home'))  # Redirect to the home page after successful login
        else:
            flash('Invalid email or password', 'danger')
    return render_template('login.html', form=form, title='Login')




@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/patient_doctor_appoint")
@login_required
def patient_doctor_appoint():
    doctors = get_doctor_data()  # Fetch patient data
    return render_template("doctors_appointment.html", doctors=doctors)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(Unauthorized)
def handle_unauthorized_error(e):
    flash("Please log in to access this page.", "info")
    return redirect(url_for("login"))  # Redirect to the login page

@app.route("/appointment/<int:doc_id>")
@login_required  # Ensure the patient is logged in
def appointment(doc_id):
    # Retrieve patient email from session
    patient_email = session.get('email')  # Assuming you store patient email in the session after login
    if not patient_email:
        flash('Please log in to make an appointment.', 'info')
        return redirect(url_for('login'))  # Redirect to login if patient not logged in

    # Retrieve patient ID from database based on email
    patient_id = get_patient_id_from_email(patient_email)
    if not patient_id:
        flash('Account Not Found', "danger")
        return redirect(url_for('login'))  # Redirect to login if patient ID not found

    form = AppointmentForm()
    return render_template("appointment.html", form=form, doc_id=doc_id, patient_id=patient_id)

@app.route('/create_appointment', methods=['POST'])
@login_required
def create_appointment():
    # Retrieve doc_id and patient_id from the request parameters
    doc_id = request.args.get('doc_id')
    patient_id = request.args.get('patient_id')

    # Create an instance of the AppointmentForm
    form = AppointmentForm(request.form)
    
    # Check if the form is submitted and valid
    if form.validate_on_submit():
        # Retrieve other form data
        print("validated")
        appointment_date = form.appointment_date.data
        appointment_time = form.appointment_time.data

        # Check if the appointment slot is available
        
        if appointcheck(doc_id, patient_id, appointment_date, appointment_time):
            # Insert appointment into the database
            appointment_id = insert_appointment(appointment_date, appointment_time)
            insert_appointment_patient(appointment_id, patient_id, doc_id)
            flash(f'Appointment created successfully.', "success")
            return redirect(url_for('home'))
        else:
            flash(f'Appointment already exists for this slot.', "danger")
            return redirect(url_for('home'))
    else:
        # If the form is not valid, render the appointment.html template with the form
        flash(f'Invalid Credentials', 'warning')
        print("not validated ")
        return render_template('appointment.html', form=form, doc_id=doc_id, patient_id=patient_id)




@app.route("/department")
def department():
    return render_template("department.html")

from flask_login import login_user, current_user


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == "POST" and form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        confirm_password = form.confirm_password.data
        name = form.name.data
        age = form.age.data
        gender = form.gender.data
        weight = form.weight.data
        height = form.height.data
        blood_group = form.blood_group.data
        user_address = form.user_address.data
        user_contact = form.user_contact.data
        relation = form.relation.data
        s_name = form.s_name.data
        secondary_contact = form.secondary_contact.data
        secondary_address = form.secondary_address.data
        
        if not user_exist(email) and password == confirm_password:
            hashed_password = generate_password_hash(password)
            insert_user(name, email, hashed_password, age, gender, weight, height, blood_group, user_address, user_contact, relation, s_name, secondary_contact, secondary_address)
            flash('User account created successfully!', 'success')
            
            # Retrieve the newly created user from the database
            user = User.query().filter_by(email=email).first()
            # Log the user in
            login_user(user)
            
            return redirect(url_for('home'))
        else:
            flash('Registration failed. Please check your inputs.', 'danger')
    
    return render_template('register.html', title='Register', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))

@app.route("/myappointments")
@login_required
def myappointments():
    patient_id = current_user.id

    with engine.connect() as conn:
        query = text("""
            SELECT 
                d.doc_name AS doctor_name,
                a.appointment_date,
                a.appointment_time
            FROM 
                doctor d
            INNER JOIN 
                patient_appointment pa ON d.doc_id = pa.doc_id
            INNER JOIN 
                appointment a ON pa.appointment_id = a.appointment_id
            WHERE 
                pa.patient_id = :patient_id
        """)
        appointments = conn.execute(query, {"patient_id": patient_id}).fetchall()

    return render_template("myappointments.html", appointments=appointments)


@app.route("/mytransactions")
@login_required
def mytransactions():
    current_user_id = current_user.id

    with engine.connect() as conn:
        query = text("""
            SELECT 
                bill_no,
                b_amount,
                transaction_id,
                b_medicine,
                b_equipment,
                b_lab
            FROM 
                bill
            WHERE 
                patient_id = :current_user_id
        """)
        bills = conn.execute(query, {"current_user_id": current_user_id}).fetchall()

    return render_template("mytransactions.html", bills=bills)



@app.route("/patients")
def patient():
   patient = get_patient_data()  # Fetch patient data
   return render_template("patients.html", patient=patient)

@app.route("/patient_room")
@login_required
def patient_room():
   if current_user.email == "abhinayasrinivas30@gmail.com":
        patient = room_patient()  # Fetch patient data
        return render_template("room_patient.html", patient=patient)
   else:
        return render_template("404.html"), 404




@app.route("/equipment")
@login_required
def equipment():
    if current_user.email == "abhinayasrinivas30@gmail.com":
        equipment= get_equip_data()  # Fetch patient data
        return render_template("equipment.html", equipment=equipment)
    else:
        return render_template("404.html"), 404

@app.route("/billing")
@login_required
def billing():
    if current_user.email == "abhinayasrinivas30@gmail.com":
        billing = get_billing_data()
        return render_template("bil.html", billing=billing)
    else:
        return render_template("404.html"), 404


@app.route("/doctors")
def doctor():
   doctors = get_doctor_data()  # Fetch patient data
   return render_template("doctors.html", doctors= doctors)

@app.route("/doctor")
def doctors():
   return render_template("doctors.html")

@app.route("/admin")
@login_required
def admin():
    if current_user.email == "abhinayasrinivas30@gmail.com":
        return render_template("admin.html")
    else:
        # Return a custom 404 page with styling
        return render_template("404.html"), 404  # Return 404 error for non-admin users# Redirect to login page for non-admin users

@app.route("/pharmacy")
def pharmacy():
    pharmacy = get_pharmacy_data()  # Fetch pharmacy data
    return render_template("pharmacy.html", pharmacy=pharmacy)


@app.route("/bill")
@login_required
def bill():
    if current_user.email == "abhinayasrinivas30@gmail.com":
        bill = get_billing_data()  # Fetch billing data
        return render_template("bill.html", bill=bill)
    else:
        return render_template("404.html"), 404
    



@app.route("/transaction")
@login_required
def transaction():
    if current_user.email == "abhinayasrinivas30@gmail.com":
        transaction = get_transaction_details()  # Fetch transaction data
        return render_template("transaction.html", transaction=transaction)
    else:
        return render_template("404.html"), 404
    

@app.route("/research")
def research():
    research = get_research_interns_data()  # Fetch patient data
    return render_template("research.html", research=research)

@app.route("/equipments")
@login_required
def equip():
    if current_user.email == "abhinayasrinivas30@gmail.com":
        total_equip_price = session.get('total_price',0)
        return render_template("equipments.html",total_equip_price=total_equip_price)
    else:
        return render_template("404.html"), 404
    

@app.route("/equipbill")
@login_required
def show_equip_bill():
    if current_user.email == "abhinayasrinivas30@gmail.com":
        total_equip_price = session.get('total_equip_price',0)
        return render_template('equipbill.html', total_equip_price=total_equip_price)
    else:
        return render_template("404.html"), 404
    

@app.route("/buyequipment", methods=['POST'])
@login_required
def buy_equipment():
    if current_user.email == "abhinayasrinivas30@gmail.com":
        total_equip_price=session.get('total_equip_price')
        return render_template("pat_equip.html",total_equip_price=total_equip_price)
    else:
        return render_template("404.html"), 404
    

@app.route("/equip_session", methods=['POST'])
@login_required
def equip_session():
    if current_user.email == "abhinayasrinivas30@gmail.com":
        pid = request.form['patient_id']
        tep = session.get('total_equip_price', 0)
        pit = session.get('pt', random.randint(5000,10000))  # Get the current value of 'rt' from the session
        
        with engine.connect() as connection:
            try:
                with connection.begin() as transaction:
                    query = text("insert into transaction values(:transaction_id,:transaction_amount);")
                    result = connection.execute(query,{"transaction_id":pit,"transaction_amount":tep})
                    query = text("update bill set b_equipment=:b_equip where patient_id=:p_id;")
                    result = connection.execute(query,{"b_equip":tep,"p_id":pid})
                    query = text("update bill set b_amount=b_medicine+b_equipment where patient_id=:p_id;")
                    result = connection.execute(query,{"p_id":pid})
                    transaction.commit()
            except SQLAlchemyError as e:
            # Handle any database-related errors
                print("An error occurred:", str(e))
                return redirect(url_for('transaction_failed'))
        session['total_equip_price'] = 0  # Set total_price to 0
        session.clear()  # Clear all session data
        return render_template('pop.html', total_equip_price=tep,transaction_id=pit)
    else:
        return render_template("404.html"), 404



@app.route("/sell_equipment", methods=['POST'])
@login_required
def sell_equipment():
    if current_user.email == "abhinayasrinivas30@gmail.com":
        session['total_equip_price'] = session.get('total_equip_price',0)
        #session['submit_count'] = 0
        equip_id = request.form['equipment_id']
        equip_qty = int(request.form['equipment_qty'])
        total_equip_price = session.get('total_equip_price', 0)
        with engine.connect() as connection:
            try:
                with connection.begin() as transaction:
                    query = text("SELECT equip_qty, equip_cost FROM equipment WHERE equip_id=:eq_id;")
                    result = connection.execute(query, {"eq_id": equip_id}).fetchone()
                    if result:
                        current_qty = result[0]
                        equip_price = result[1]
                        if current_qty >= (equip_qty):
                            new_qty = current_qty - (equip_qty)
                            price = (equip_qty) * equip_price  # Calculate the price
                            total_equip_price = total_equip_price+price  # Update total price
                            session['total_equip_price'] = total_equip_price
                            #print(f"Updated total_price: {total_price}")
                            # Update pharmacy table with new quantity
                            query = text("UPDATE equipment SET equip_qty=:new WHERE equip_id=:eq_id;")
                            connection.execute(query, {"new": new_qty, "eq_id": equip_id})
                            transaction.commit()
                        else:
                            return redirect(url_for('show_error', error=f'Insufficient quantity for euipment ID {equip_id}'))
                    else:
                        return redirect(url_for('show_error', error=f'Equipment with ID {equip_id} not found'))
            except SQLAlchemyError as e:
                # Handle any database-related errors
                print("An error occurred:", str(e))
                return redirect(url_for('transaction_failed'))
        session['total_equip_price'] = total_equip_price
        redirect_url = url_for('show_equip_bill')

        return redirect(redirect_url)
    else:
        return render_template("404.html"), 404


    
@app.route("/medicine")
@login_required
def med():
    if current_user.email == "abhinayasrinivas30@gmail.com":
        total_price = session.get('total_price',0)
        form = MedForm()
        return render_template("medicine.html",total_price=total_price, form=form)
    else:
        return render_template("404.html"), 404

@app.route("/sell_medicine", methods=['POST'])
@login_required
def sell_medicine():
    if current_user.email == "abhinayasrinivas30@gmail.com":
        session['total_price'] = session.get('total_price',0)
        #session['submit_count'] = 0
        med_id = request.form['medicine_id']
        med_qty = int(request.form['medicine_qty'])
        total_price = session.get('total_price', 0)
        with engine.connect() as connection:
            try:
                with connection.begin() as transaction:
                    query = text("SELECT med_qty, med_price FROM pharmacy WHERE med_no=:med_id;")
                    result = connection.execute(query, {"med_id": med_id}).fetchone()
                    if result:
                        current_qty = result[0]
                        med_price = result[1]
                        if current_qty >= (med_qty):
                            new_qty = current_qty - (med_qty)
                            price = (med_qty) * med_price  # Calculate the price
                            total_price = total_price+price  # Update total price
                            session['total_price'] = total_price
                            print(f"Updated total_price: {total_price}")
                            # Update pharmacy table with new quantity
                            query = text("UPDATE pharmacy SET med_qty=:new WHERE med_no=:med_id;")
                            connection.execute(query, {"new": new_qty, "med_id": med_id})
                            transaction.commit()
                        else:
                            return redirect(url_for('show_error', error=f'Insufficient quantity for medicine ID {med_id}'))
                    else:
                        return redirect(url_for('show_error', error=f'Medicine with ID {med_id} not found'))
            except SQLAlchemyError as e:
                # Handle any database-related errors
                return redirect(url_for('show_error', error=f'An error occurred while updating the pharmacy: {str(e)}'))
        session['total_price'] = total_price
        redirect_url = url_for('show_bill')

        return redirect(redirect_url)
    else:
        return render_template("404.html"), 404

@app.route("/price")
@login_required
def show_bill():
    if current_user.email == "abhinayasrinivas30@gmail.com":
        total_price = session.get('total_price',0)
        return render_template('med_bill.html', total_price=total_price)
    else:
        return render_template("404.html"), 404

@app.route("/show_error/<error>")
def show_error(error):
    # Render the template for showing the error message
    return render_template("medicine.html", error=error)

@app.route("/buymedicine", methods=['POST'])
@login_required
def buy_medicine():
    if current_user.email == "abhinayasrinivas30@gmail.com":
        form=TransForm()
        total_price=session.get('total_price')
        return render_template("pat_med.html",total_price=total_price, form=form)
    else:
        return render_template("404.html"), 404

@app.route("/end_session", methods=['POST'])
@login_required
def end_session():
    if current_user.email == "abhinayasrinivas30@gmail.com":
        pid= request.form['patient_id']
        tp = session.get('total_price', 0)
        rt = session.get('tid', random.randint(1000,5000))  # Get the current value of 'rt' from the session
        bid= session.get('bt',random.randint(1000000,2000000))
        with engine.connect() as connection:
            try:
                with connection.begin() as transaction:
                    query = text("insert into transaction values(:transaction_id,:transaction_amount);")
                    result = connection.execute(query,{"transaction_id":rt,"transaction_amount":tp})
                    query = text("insert into bill values(:bill_id,:patient_id,:b_amount,:transaction_id,:b_medicine,NULL,NULL);")
                    result = connection.execute(query,{"bill_id":bid,"patient_id":pid, "b_amount":tp,"transaction_id":rt,"b_medicine":tp})
                    transaction.commit()
            except SQLAlchemyError as e:
                # Handle any database-related errors
                print("An error occurred:", str(e))
                return redirect(url_for('transaction_failed'))
        session['total_price'] = 0  # Set total_price to 0
        session.clear()  # Clear all session data
        return render_template('popup.html', total_price=tp,transaction_id=rt)
    else:
        return render_template("404.html"), 404

@app.route("/generate_qr")
@login_required
def generate_qr():
    if current_user.email == "abhinayasrinivas30@gmail.com":
    
    # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        # Here you can add the content you want to encode in the QR code
        qr.add_data("https://www.nbcnews.com/id/wbna45729377")
        qr.make(fit=True)

        # Create an in-memory BytesIO object to store the QR code image
        img = qr.make_image(fill_color="black", back_color="white")
        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)

        # Return the image file
        return send_file(img_io, mimetype='image/png')
    else:
        return render_template("404.html"), 404

@app.route("/transaction_failed")
def transaction_failed():
    return render_template("failtransaction.html")



# @app.route("/billing_details/<float:total_price>", methods=['GET'])
# def billing_details(total_price):
#     return render_template('show.html', total_price=total_price)

     
@app.route('/add_patient', methods=['GET', 'POST'])
@login_required
def add_patient_route():
    if current_user.email == "abhinayasrinivas30@gmail.com":
        form = PatientForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                # Process the form data (e.g., adding patient to the database)
                add_patient()
                flash(f'Patient details added successfully', 'success')
                return redirect(url_for('patient'))  # Redirect to the patient page after adding patient
            else:
                flash(f'Form validation failed', 'error')  # Flash an error message if form validation fails
            return render_template('pat_form.html', form=form)  # Pass the form object to the template
        return render_template('pat_form.html', form=form)
    else:
        return render_template("404.html"), 404


@app.route('/add_doctor', methods=['GET', 'POST'])
@login_required
def add_doctor_route():
    if current_user.email == "abhinayasrinivas30@gmail.com":
        form = DoctorForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                # Process the form data (e.g., adding Doctor to the database)
                add_doctor()
                flash(f'Doctor details added successfully', 'success')
                return redirect(url_for('doctor'))  # Redirect to the patient page after adding patient
            else:
                flash(f'Form validation failed', 'error')  # Flash an error message if form validation fails
            return render_template('doc_form.html', form=form)  # Pass the form object to the template
        return render_template('doc_form.html', form=form)
    else:
        return render_template("404.html"), 404


@app.route('/add_research', methods=['GET', 'POST'])
@login_required
def add_research_route():
    if current_user.email == "abhinayasrinivas30@gmail.com":
        form = Research()
        if request.method == 'POST':
            if form.validate_on_submit():
                # Process the form data (e.g., adding Doctor to the database)
                add_research()
                flash(f'Intern details added successfully', 'success')
                return redirect(url_for('research'))  # Redirect to the patient page after adding patient
            else:
                flash(f'Form validation failed', 'error')  # Flash an error message if form validation fails
            return render_template('research_form.html', form=form)  # Pass the form object to the template
        return render_template('research_form.html', form=form)
    else:
        return render_template("404.html"), 404


@app.route('/allot_room', methods=['GET'])
def allotroomform():
    form = RoomAllotForm()
    return render_template('allotment.html', form=form)



@app.route('/allot_room', methods=['POST', 'GET'])
@login_required
def allotroom():
    if current_user.email == "abhinayasrinivas30@gmail.com":

        form = RoomAllotForm(request.form)
        
        if request.method == 'POST' and form.validate_on_submit():
            room_id = form.room_id.data
            patient_id = int(form.patient_id.data)
            in_date = form.in_date.data
            out_date = form.out_date.data
            
            current_date = datetime.now().date()
            alloted = get_room_alloted(room_id)
            occupancy = get_room_occupancy(room_id)
            print("alloted: ", alloted)
            print("occupancy: ", occupancy)

            # Construct SQL query to count existing room allotments with the same details
            query = text("SELECT COUNT(*) "
                        "FROM patient_room "
                        "WHERE patient_id = :patient_id AND room_id = :room_id AND in_date = :in_date AND out_date = :out_date")
            result = connection.execute(query, {"patient_id": patient_id, "room_id": room_id, "in_date": in_date, "out_date": out_date}).fetchone()[0]

            # Check if any existing room allotments were found
            if result > 0:
                flash('Room already allotted.', 'warning')
                return redirect(url_for('patient_room'))
            
            # If no existing allotment found and input dates are valid
            elif in_date >= current_date and out_date >= current_date and in_date <= out_date:
                # Check if room occupancy allows for allotment
                if occupancy > alloted:
                    allot_room(room_id, patient_id, in_date, out_date)
                    flash('Room allotted successfully.', 'success')
                else:
                    flash('Room not allotted. Maximum occupancy reached.', 'danger')
            else:
                flash('Invalid date. Please select future dates.', 'error')
            
            return redirect(url_for('patient_room'))
        
        return render_template('allotment.html', form=form)
    else:
        return render_template("404.html"), 404

@app.route('/add_medicine', methods=['GET', 'POST'])
@login_required
def add_medicine_route():
    if current_user.email == "abhinayasrinivas30@gmail.com":
        form = MedicineForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                # Process the form data (e.g., adding patient to the database)
                add_medicine()
                flash(f'Stock details updated successfully', 'success')
                return redirect(url_for('pharmacy'))  # Redirect to the patient page after adding patient
            else:
                flash(f'Form validation failed', 'error')  # Flash an error message if form validation fails
            return render_template('med_form.html', form=form)  # Pass the form object to the template
        return render_template('med_form.html',form=form)
    else:
        return render_template("404.html"), 404

@app.route('/add_equipment', methods=['GET', 'POST'])
@login_required
def add_equipment_route():
    if current_user.email == "abhinayasrinivas30@gmail.com":
        form = EquipmentForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                # Process the form data (e.g., adding patient to the database)
                add_equipment()
                flash(f'Stock details updated successfully', 'success')
                return redirect(url_for('equipment'))  # Redirect to the patient page after adding patient
            else:
                flash(f'Form validation failed', 'error')  # Flash an error message if form validation fails
            return render_template('equip_form.html', form=form)  # Pass the form object to the template
        return render_template('equip_form.html',form=form)
    else:
        return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(debug=True)
