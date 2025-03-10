import re
from datetime import datetime, timedelta

import pymysql as pymysql
from flask import Flask, render_template, request, session, redirect, flash

conn = pymysql.connect(host="online-car-sale.cx6w0yceyyfr.us-east-1.rds.amazonaws.com", user="admin", password="onlinecarsale", db="online_car_sale")
cursor = conn.cursor()



import os
import boto3 as boto3
Online_Car_Sale_Access_Key = "AKIAQ4NXPXFZS5UB7IHG"
Online_Car_Sale_Secret_Access_Key = "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"
Online_Car_Sale_bucket = "online-car-sale"
Online_Car_Sale_Email_Source = 'komalkumarpenti23@gmail.com'
Online_Car_Sale_System_s3_client = boto3.client('s3', aws_access_key_id=Online_Car_Sale_Access_Key, aws_secret_access_key=Online_Car_Sale_Secret_Access_Key)
Online_Car_Sale_System_ses_client = boto3.client('ses', aws_access_key_id=Online_Car_Sale_Access_Key, aws_secret_access_key=Online_Car_Sale_Secret_Access_Key, region_name='us-east-1')

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_ROOT = APP_ROOT + "/static/picture"

app = Flask(__name__)
app.secret_key = "online_car_sale"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/admin_login")
def admin_login():
    return render_template("/admin_login.html")


@app.route("/admin_login_action", methods=['post'])
def admin_login_action():
    username = request.form.get("username")
    password = request.form.get("password")
    if username=='admin' and password=='admin':
        session['role'] = "admin"
        return redirect("/admin_home")
    else:
        return render_template("msg.html", msg="Invalid Login")


@app.route("/admin_home")
def admin_home():
    return render_template("admin_home.html")


@app.route("/logout")
def logout():
    session.clear()
    return render_template("index.html")


@app.route("/owner_registration")
def owner_registration():
    return render_template("owner_registration.html")


@app.route("/owner_registration_action", methods=["post"])
def owner_registration_action():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    phone = request.form.get("phone")
    email = request.form.get("email")
    state = request.form.get("state")
    city = request.form.get("city")
    zipcode = request.form.get("zipcode")
    date_of_birth = request.form.get("date_of_birth")
    password = request.form.get("password")
    conform_password = request.form.get("conform_password")
    address = request.form.get("address")
    if password != conform_password:
        return render_template("msg.html", msg="Password Not Matched !!!")
    count = cursor.execute("select * from owners where email='"+str(email)+"' or phone='"+str(phone)+"'")
    if count == 0:
        cursor.execute("insert into owners(first_name,last_name,phone,email,state,city,zipcode,password,date_of_birth,address,status) "
                       "values('"+str(first_name)+"','"+str(last_name)+"','"+str(phone)+"','"+str(email)+"','"+str(state)+"','"+str(city)+"','"+str(zipcode)+"','"+str(password)+"','"+str(date_of_birth)+"','"+str(address)+"','De-Activated')")

        conn.commit()
        Online_Car_Sale_System_ses_client.verify_email_address(
            EmailAddress=email
        )
        return render_template("msg.html", msg="Owner Registered Successfully")
    else:
        return render_template("msg.html", msg="Duplicate Entry")


@app.route("/owner_login")
def owner_login():
    return render_template("owner_login.html")


@app.route("/owner_login_action", methods=['post'])
def owner_login_action():
    email = request.form.get("email")
    password = request.form.get("password")
    count = cursor.execute("select * from owners where email='"+str(email)+"' and password='"+str(password)+"'")
    if count > 0:
        owner = cursor.fetchone()
        if owner[6] == "De-Activated":
            return render_template("msg.html", msg="Owner Is Not Activated")
        else:
            owner_first_name = owner[1]
            owner_last_name = owner[2]
            email = owner[3]
            emails = Online_Car_Sale_System_ses_client.list_identities(
                IdentityType='EmailAddress'
            )
            if email in emails['Identities']:
                email_msg = 'Hello ' + owner_first_name + ' '+ owner_last_name +' '+'You Have Successfully Logged into Online Car Sales System Website'
                Online_Car_Sale_System_ses_client.send_email(Source=Online_Car_Sale_Email_Source,
                                                                Destination={'ToAddresses': [email]},
                                                                Message={
                                                                    'Subject': {'Data': email_msg, 'Charset': 'utf-8'},
                                                                    'Body': {'Html': {'Data': email_msg,
                                                                                      'Charset': 'utf-8'}}})

            session['owner_id'] = owner[0]
            session['role'] = "owner"
            return redirect("/owner_home")
    else:
        return render_template("msg.html", msg="Invalid login Details")


@app.route("/owner_home")
def owner_home():
    owner_id = session['owner_id']
    cursor.execute("select * from owners where owner_id='"+str(owner_id)+"'")
    owner = cursor.fetchone()
    return render_template("owner_home.html", owner=owner)


@app.route("/customer_login")
def customer_login():
    return render_template("/customer_login.html")


@app.route("/customer_login_action", methods=['post'])
def customer_login_action():
    email = request.form.get("email")
    password = request.form.get("password")
    count = cursor.execute("select * from customers where email='"+str(email)+"' and password='"+str(password)+"'")
    if count > 0:
        customer = cursor.fetchone()
        customer_first_name = customer[1]
        customer_last_name = customer[2]
        email = customer[3]
        emails = Online_Car_Sale_System_ses_client.list_identities(
            IdentityType='EmailAddress'
        )
        if email in emails['Identities']:
            email_msg = 'Hello ' + customer_first_name + ' ' + customer_last_name + ' ' + 'You Have Successfully Logged into Online Car Sales System Website'
            Online_Car_Sale_System_ses_client.send_email(Source=Online_Car_Sale_Email_Source,
                                                         Destination={'ToAddresses': [email]},
                                                         Message={
                                                             'Subject': {'Data': email_msg, 'Charset': 'utf-8'},
                                                             'Body': {'Html': {'Data': email_msg,
                                                                               'Charset': 'utf-8'}}})
        else:
            return render_template("msg.html",
                                   msg="Verify your email by the link that has sent to registered your email.")
        session['customer_id'] =customer[0]
        session['role'] = "customer"
        return redirect("/customer_home")
    else:
        return render_template("msg.html", msg="Invalid Login")


@app.route("/customer_registration")
def customer_registration():
    return render_template("customer_registration.html")


@app.route("/customer_registration_action", methods=["post"])
def customer_registration_action():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    phone = request.form.get("phone")
    email = request.form.get("email")
    state = request.form.get("state")
    city = request.form.get("city")
    zipcode = request.form.get("zipcode")
    date_of_birth = request.form.get("date_of_birth")
    password = request.form.get("password")
    conform_password = request.form.get("conform_password")
    address = request.form.get("address")
    if password != conform_password:
        return render_template("msg.html", msg="Password Not Matched !!!")
    count = cursor.execute("select * from customers where email='"+str(email)+"' or phone='"+str(phone)+"'")
    if count == 0:
        cursor.execute("insert into customers (first_name,last_name,phone,email,state,city,zipcode,password,date_of_birth,address) values('"+str(first_name)+"','"+str(last_name)+"','"+str(phone)+"','"+str(email)+"','"+str(state)+"','"+str(city)+"','"+str(zipcode)+"','"+str(password)+"','"+str(date_of_birth)+"','"+str(address)+"')")
        conn.commit()
        Online_Car_Sale_System_ses_client.verify_email_address(
            EmailAddress=email
        )
        return render_template("msg.html", msg="Customer Registered Successful")
    else:
        return render_template("msg.html", msg="Duplicate Entry")


@app.route("/customer_home")
def customer_home():
    customer_id = session['customer_id']
    cursor.execute("select * from customers where customer_id='"+str(customer_id)+"'")
    customer = cursor.fetchone()
    return render_template("customer_home.html", customer=customer)


@app.route("/add_location")
def add_location():
    cursor.execute("select * from locations")
    locations = cursor.fetchall()
    return render_template("add_location.html", locations=locations)


@app.route("/add_location_action", methods=['post'])
def add_location_action():
    location_name = request.form.get("location_name")
    count= cursor.execute("select * from locations where location_name='"+str(location_name)+"'")
    if count == 0:
        cursor.execute("insert into locations(location_name) values('"+str(location_name)+"')")
        conn.commit()
        return redirect("/add_location")
    else:
        return render_template('msg2.html', msg='Location Already Exist', color='text-success')

@app.route("/view_owner")
def view_owner():
    cursor.execute("select * from owners")
    owners = cursor.fetchall()
    return render_template("view_owner.html", owners=owners)



@app.route("/activate1")
def activate1():
    owner_id = request.args.get("owner_id")
    cursor.execute("update owners set status='Activated' where owner_id='"+str(owner_id)+"'")
    conn.commit()
    return redirect("/view_owner")


@app.route("/activate2")
def activate2():
    owner_id = request.args.get("owner_id")
    cursor.execute("update owners set status='De-Activated' where owner_id='" + str(owner_id) + "'")
    conn.commit()
    return redirect("/view_owner")


@app.route("/add_car")
def add_car():
    msg = request.args.get("msg")
    customer = request.args.get("customer")
    location_id = request.args.get("location_id")
    keyword = request.args.get("keyword")
    if keyword == None:
        keyword = ""
    query = ""
    if session['role'] == 'owner':
        owner_id = session['owner_id']
        if location_id == None:
            location_id = ""
        if location_id == "":
            query = "select * from cars where owner_id='"+str(owner_id)+"' and (make LIKE '%"+str(keyword)+"%' or model LIKE '%"+str(keyword)+"%')"
        else:
            query = "select * from cars where owner_id='"+str(owner_id)+"' and location_id='"+str(location_id)+"' and (make LIKE '%"+str(keyword)+"%' or model LIKE '%"+str(keyword)+"%')"
    elif session['role'] == 'customer':
        if location_id == None:
            location_id = ""
        if location_id == "":
            query = "select * from cars where status='Available' and (make LIKE '%"+str(keyword)+"%' or model LIKE '%"+str(keyword)+"%')"
        else:
            query = "select * from cars where status='Available' and location_id='"+str(location_id)+"' and (make LIKE '%"+str(keyword)+"%' or model LIKE '%"+str(keyword)+"%')"
    elif session['role'] == 'admin':
        if location_id == None:
            location_id = ""
        if location_id == "":
            query = "select * from cars where (make LIKE '%" + str(
                keyword) + "%' or model LIKE '%" + str(keyword) + "%')"

        else:

            query = "select * from cars where location_id='" + str(location_id) + "' and (make LIKE '%" + str(keyword) + "%' or model LIKE '%" + str(keyword) + "%')"

    cursor.execute(query)
    cars = cursor.fetchall()
    cars = list(cars)
    cars.reverse()
    cursor.execute("select * from locations")
    locations = cursor.fetchall()
    locations = list(locations)
    return render_template("add_car.html", locations=locations,int=int, cars=cars, customer=customer, msg=msg, str=str, location_id=location_id, keyword=keyword, is_customer_is_requested_for_car=is_customer_is_requested_for_car, get_location_by_location_id=get_location_by_location_id)

@app.route("/add_car_action", methods=['post'])
def add_car_action():
    location_id = request.form.get("location_id")
    owner_id = session['owner_id']
    make = request.form.get("make")
    model = request.form.get("model")
    miles_travelled = request.form.get("miles_travelled")
    manufacturing_year = request.form.get("manufacturing_year")
    price = request.form.get("price")
    description = request.form.get("description")
    vin_number = request.form.get("vin_number")
    license_plate = request.form.get("license_plate")
    milage = request.form.get("milage")
    tax_amount = request.form.get("tax_amount")
    car_image = request.files.get("car_image")
    path = APP_ROOT + "/" + car_image.filename
    car_image.save(path)
    Online_Car_Sale_System_s3_client.upload_file(path, Online_Car_Sale_bucket, car_image.filename)
    licence = request.files.get("licence")
    path = APP_ROOT + "/" + licence.filename
    licence.save(path)
    Online_Car_Sale_System_s3_client.upload_file(path, Online_Car_Sale_bucket, licence.filename)
    count = cursor.execute("select * from cars where vin_number='"+str(vin_number)+"' or license_plate='"+str(license_plate)+"'")
    if count > 0:
        return render_template('msg2.html', msg='This car by this owner is already exist', color='text-success')
    else:
        cursor.execute("insert into cars (location_id,owner_id,make,model,manufacturing_year,miles_travelled,price,description,vin_number,license_plate,milage,tax_amount,car_image,licence,status)"
                       " values('"+str(location_id)+"','"+str(owner_id)+"','"+str(make)+"','"+str(model)+"','"+str(manufacturing_year)+"','"+str(miles_travelled)+"','"+str(price)+"','"+str(description)+"','"+str(vin_number)+"','"+str(license_plate)+"','"+str(milage)+"','"+str(tax_amount)+"','"+str(car_image.filename)+"','"+str(licence.filename)+"','Not Verified')")
        conn.commit()
        return redirect("/add_car")




# @app.route("/view_cars")
# def view_cars():
#     query = {}
#     cars = car_collection.find(query)
#     cars = list(cars)
#     cars.reverse()
#     locations = location_collection.find({})
#     locations = list(locations)
#     return render_template("view_cars.html",str=str, cars=cars,locations=locations,is_customer_is_requested_for_car=is_customer_is_requested_for_car,get_location_by_location_id=get_location_by_location_id)



def is_customer_is_requested_for_car(car_id):
    customer_id = session['customer_id']
    count = cursor.execute("select * from carrequests where customer_id='"+str(customer_id)+"' and car_id='"+str(car_id)+"' and status!='cancelled'")
    if count > 0:
        return True
    else:
        return False


@app.route("/cancel")
def cancel():
    car_order_id = request.args.get("car_order_id")
    cursor.execute("update carrequests set status='cancelled' where carrequest_id='"+str(car_order_id)+"'")
    conn.commit()
    return redirect("/view_car_order")


def get_location_by_location_id(location_id):
    cursor.execute("select * from locations where location_id='"+str(location_id)+"'")
    locations = cursor.fetchone()
    return locations


# @app.route("/edit_details")
# def edit_details():
#     car_id = request.args.get("car_id")
#     car = car_collection.find_one({"_id": ObjectId(car_id)})
#     return render_template("edit_car.html", car=car, car_id=car_id)

@app.route("/verify_car")
def verify_car():
    car_id = request.args.get("car_id")
    cursor.execute("update cars set status='Available' where car_id='"+str(car_id)+"'")
    conn.commit()
    return redirect("/add_car")

# @app.route("/edit_car_action")
# def edit_car_action():
#     car_id = request.args.get("car_id")
#     make = request.args.get("make")
#     model = request.args.get("model")
#     miles_travelled = request.args.get("miles_travelled")
#     price = request.args.get("price")
#     vin_number = request.args.get("vin_number")
#     license_plate = request.args.get("license_plate")
#     milage = request.args.get("milage")
#     tax_amount = request.args.get("tax_amount")
#     query1 = {"_id": ObjectId(car_id)}
#     query2 = {"$set": {"make": make, "model": model, "miles_travelled": miles_travelled,"license_plate":license_plate, "price":price, "vin_number": vin_number, "milage": milage, "tax_amount": tax_amount}}
#     car_collection.update_many(query1, query2)
#     return render_template("msg.html", msg="Details are Updated")


@app.route("/send_request")
def send_request():
    car_id = request.args.get("car_id")
    customer_id = session['customer_id']
    total_price = request.args.get("total_price")
    date = datetime.now()
    cursor.execute("insert into carrequests(customer_id,total_price,car_id,date,status) values('"+str(customer_id)+"','"+str(total_price)+"','"+str(car_id)+"','"+str(date)+"','requested')")
    conn.commit()
    return render_template("msg2.html", msg="Your Proposal Request is send to Owner")



@app.route("/view_car_order")
def view_car_order():
    query = ""
    if session['role'] == "owner":
        car_id = request.args.get("car_id")
        query = "select * from carrequests where car_id='"+str(car_id)+"'"
    elif session['role'] == "customer":
        customer_id = session["customer_id"]
        car_id = request.args.get("car_id")
        if car_id == None:
            query = "select * from carrequests where customer_id='" + str(customer_id) + "'"
        else:
            query = "select * from carrequests where customer_id='" + str(customer_id) + "' and car_id='"+str(car_id)+"'"
    cursor.execute(query)
    car_orders = cursor.fetchall()
    car_orders = list(car_orders)
    return render_template("view_car_order.html",car_orders=car_orders, get_customer_by_customer_id=get_customer_by_customer_id, get_car_by_car_id=get_car_by_car_id, get_owner_by_owner_id=get_owner_by_owner_id,int=int)


def get_customer_by_customer_id(customer_id):
    cursor.execute("select * from customers where customer_id='"+str(customer_id)+"'")
    customer = cursor.fetchone()
    return customer


def get_car_by_car_id(car_id):
    cursor.execute("select * from cars where car_id='"+str(car_id)+"'")
    car = cursor.fetchone()
    return car


def get_owner_by_owner_id(owner_id):
    cursor.execute("select * from owners where owner_id='"+str(owner_id)+"'")
    owner = cursor.fetchone()
    return owner

@app.route("/accept_order")
def accept_order():
    car_order_id = request.args.get("car_order_id")
    cursor.execute("update carrequests set status='Accepted' where carrequest_id='"+str(car_order_id)+"'")
    conn.commit()
    cursor.execute("select * from  carrequests where carrequest_id='" + str(car_order_id) + "'")
    carrequest = cursor.fetchone()
    car_id = carrequest[4]
    cursor.execute("update cars set status='Request Accepted' where car_id='"+str(car_id)+"'")
    conn.commit()
    return render_template("msg2.html", msg="Car Request Accepted Successful")

@app.route("/reject_order")
def reject_order():
    car_order_id = request.args.get("car_order_id")
    cursor.execute("update carrequests set status='Rejected' where carrequest_id='"+str(car_order_id)+"'")
    conn.commit()
    return render_template("msg2.html", msg="Car Request Rejected")

@app.route("/dispatch")
def dispatch():
    car_order_id = request.args.get("car_order_id")
    cursor.execute("update carrequests set status='Dispatched' where carrequest_id='"+str(car_order_id)+"'")
    conn.commit()
    return render_template("msg2.html", msg="Car Dispatched")

@app.route("/mark_as_delivered")
def mark_as_delivered():
    car_order_id = request.args.get("car_order_id")
    cursor.execute("update carrequests set status='Delivered' where carrequest_id='"+str(car_order_id)+"'")
    conn.commit()
    return render_template("msg2.html", msg=" Mark as delivered")


@app.route("/payment")
def payment():
    car_order_id = request.args.get("car_order_id")
    cursor.execute("select * from  carrequests  where carrequest_id='" + str(car_order_id) + "'")
    car_order = cursor.fetchone()
    return render_template("payment.html", car_order_id=car_order_id, car_order=car_order, int=int)


@app.route("/payment_action", methods=['post'])
def payment_action():
    car_order_id = request.form.get("car_order_id")
    cursor.execute("select * from  carrequests  where carrequest_id='" + str(car_order_id) + "'")
    car_order = cursor.fetchone()
    customer_id = session['customer_id']
    total_price = request.form.get("total_price")
    admin_amount = float(car_order[1])*10 / 100
    owner_amount = float(car_order[1])*90 / 100

    card_number = request.form.get("card_number")
    card_holder_name = request.form.get("card_holder_name")
    expired_date = request.form.get("expired_date")
    cvv = request.form.get("cvv")
    date = datetime.now()
    cursor.execute("insert into payments (carrequest_id,customer_id,total_price,card_number,card_holder_name,expired_date,cvv,date,status,admin_amount,owner_amount)"
                   " values('"+str(car_order_id)+"','"+str(customer_id)+"','"+str(total_price)+"','"+str(card_number)+"','"+str(card_holder_name)+"','"+str(expired_date)+"','"+str(cvv)+"','"+str(date)+"','Paid','"+str(admin_amount)+"','"+str(owner_amount)+"')")
    conn.commit()
    cursor.execute("update carrequests set status='Paid' where carrequest_id='"+str(car_order_id)+"'")
    conn.commit()
    car_id = car_order[4]
    cursor.execute("update cars set status='Sold' where car_id='"+str(car_id)+"'")
    conn.commit()
    return render_template("msg2.html", msg="Payment Successful")


@app.route("/view_payment")
def view_payment():
    car_order_id = request.args.get("car_order_id")
    cursor.execute("select * from payments where carrequest_id='"+str(car_order_id)+"'")
    payment = cursor.fetchone()
    return render_template("view_payment.html", payment=payment, int=int,float=float)




app.run(debug=True,port=80,host="0.0.0.0")
