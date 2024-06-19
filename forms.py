from sqlalchemy import create_engine,text
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,BooleanField,IntegerField,FieldList,FormField,DateField,TimeField,ValidationError,SelectField
from wtforms.validators import DataRequired,Length,Email,EqualTo
from models import not_user_exist, user_exist
from datetime import datetime


engine = create_engine("mysql+pymysql://root:mysqlpassword@127.0.0.1:3306/hospital_management")
connection = engine.connect() 

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    name = StringField('Name', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    weight = IntegerField('Weight', validators=[DataRequired()])
    height = IntegerField('Height', validators=[DataRequired()])
    blood_group = SelectField('Blood Group', choices=[('A+', 'A+'), ('B+', 'B+'), ('AB+', 'AB+'), ('O+', 'O+'), ('A-', 'A-'), ('B-', 'B-'), ('AB-', 'AB-'), ('O-', 'O-')])
    user_address = StringField('Address', validators=[DataRequired()])
    user_contact = StringField('Contact', validators=[DataRequired()])
    relation = SelectField('Relation', choices=[('father', 'Father'), ('mother', 'Mother'), ('spouse', 'Spouse'), ('daughter', 'Daughter'), ('son', 'Son'), ('guardian', 'Guardian'), ('other', 'Other')])
    s_name = StringField('Secondary Name')
    secondary_contact = StringField('Secondary Contact')
    secondary_address = StringField('Secondary Address')
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        if user_exist(email.data):
            raise ValidationError('Email already exists!')


class LoginForm(FlaskForm):
  email =StringField('Email',validators=[DataRequired(),Email()])
  password =PasswordField('Password',validators=[DataRequired()])
  remember= BooleanField('Remember Me')
  submit = SubmitField('Login')

class singleForm(FlaskForm):
  med_no = IntegerField('ID',validators=[DataRequired()])
  med_qty = IntegerField('Quantity',validators=[DataRequired()])

class BillingForm(FlaskForm):
    medicines = FieldList(FormField(singleForm), validators=[DataRequired()],min_entries=1)
    submit = SubmitField('Submit')

class PatientForm(FlaskForm):
  p_name =StringField('Name',validators=[DataRequired()])
  address=StringField('Address',validators=[DataRequired()])
  p_gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
  p_age = IntegerField('Age',validators=[DataRequired()])
  submit = SubmitField('Submit')


class DoctorForm(FlaskForm):
  doc_name =StringField('Name',validators=[DataRequired()])
  doc_address=StringField('Address',validators=[DataRequired()])
  doc_remuneration = IntegerField('Remuneration',validators=[DataRequired()])
  doc_specialisation =StringField('Specialisation',validators=[DataRequired()])
  doc_cabin_no = IntegerField('Cabin No',validators=[DataRequired()])
  doc_floor_no = IntegerField('Floor',validators=[DataRequired()])
  doc_gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
  doc_age = IntegerField('Age',validators=[DataRequired()])
  submit = SubmitField('Submit')

class Research(FlaskForm):
  r_name =StringField('Name',validators=[DataRequired()])
  r_age = IntegerField('Age',validators=[DataRequired()])
  r_address=StringField('Address',validators=[DataRequired()])
  r_joining = DateField('Date of Joining',validators=[DataRequired()])
  r_stiphend = IntegerField('Stiphend',validators=[DataRequired()])
  r_field =StringField('Research Area',validators=[DataRequired()])
  r_gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
  submit = SubmitField('Submit')

class RoomAllotForm(FlaskForm):
    room_id = StringField('Room Id', render_kw={'required': True})
    patient_id = patient_id = IntegerField('Patient ID', render_kw={'required': True})
    in_date = DateField('In Date', format='%Y-%m-%d', render_kw={'required': True})
    out_date = DateField('Out Date', format='%Y-%m-%d', render_kw={'required': False})
    submit = SubmitField('Allot')



class AppointmentForm(FlaskForm):
    appointment_date = DateField('Appointment Date', format='%Y-%m-%d', render_kw={'required': True})
    appointment_time = TimeField('Appointment Time', format='%H:%M', render_kw={'required': True})
    submit = SubmitField('Book Now ')
    def validate_appointment_date(self, field):
        appointment_datetime = datetime.combine(field.data, self.appointment_time.data)
        if appointment_datetime <= datetime.now():
            raise ValidationError('Appointment date and time must be in the future')




class MedForm(FlaskForm):
   medicine_id = IntegerField('ID',validators=[DataRequired()])
   medicine_qty = IntegerField('Qty',validators=[DataRequired()])
   submit = SubmitField('Submit ')

class TransForm(FlaskForm):
   patient_id = IntegerField('ID',validators=[DataRequired()])
   submit = SubmitField('Submit ')

class MedicineForm(FlaskForm):
  med_gen_name = StringField('General Name',validators=[DataRequired()])
  med_scientific_name =StringField('Scientific Name',validators=[DataRequired()])
  med_qty = IntegerField('Quantity',validators=[DataRequired()])
  med_price = IntegerField('Cost per unit',validators=[DataRequired()])
  submit = SubmitField('Submit')

class EquipmentForm(FlaskForm):
  equip_name = StringField('General Name',validators=[DataRequired()])
  equip_cost = IntegerField('Cost per unit',validators=[DataRequired()])
  equip_qty = IntegerField('Quantity',validators=[DataRequired()])
  roomid = StringField('Room Id', render_kw={'required': True})
  submit = SubmitField('Submit')
