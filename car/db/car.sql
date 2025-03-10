drop database online_car_sale;

create database online_car_sale;
use online_car_sale;

create table owners(
owner_id int auto_increment primary key,
first_name varchar(255) not null,
last_name varchar(255) not null,
email varchar(255) not null,
phone varchar(255) not null,
password varchar(255) not null,
status varchar(255) not null,
address varchar(255) not null,
date_of_birth varchar(255) not null,
zipcode varchar(255) not null,
city varchar(255) not null,
state varchar(255) not null
);


create table customers(
customer_id int auto_increment primary key,
first_name varchar(255) not null,
last_name varchar(255) not null,
email varchar(255) not null,
phone varchar(255) not null,
password varchar(255) not null,
address varchar(255) not null,
date_of_birth varchar(255) not null,
zipcode varchar(255) not null,
city varchar(255) not null,
state varchar(255) not null
);

create table locations(
location_id int auto_increment primary key,
location_name varchar(255) not null
);


create table cars(
car_id int auto_increment primary key,
make varchar(255) not null,
model varchar(255) not null,
manufacturing_year varchar(255) not null,
miles_travelled varchar(255) not null,
price varchar(255) not null,
description varchar(255) not null,
vin_number varchar(255) not null,
license_plate varchar(255) not null,
milage varchar(255) not null,
tax_amount varchar(255) not null,
car_image varchar(255) not null,
status varchar(255) not null,
licence varchar(255) not null,
location_id int,
owner_id int,
foreign key(location_id) references locations(location_id),
foreign key(owner_id) references owners(owner_id)
);

create table carrequests(
carrequest_id int auto_increment primary key,
total_price varchar(255) not null,
status varchar(255),
date datetime not null,
car_id int,
customer_id int,
foreign key(car_id) references cars(car_id),
foreign key(customer_id) references customers(customer_id)
);

create table payments(
payment_id int auto_increment primary key,
total_price varchar(255) not null,
card_number varchar(255),
card_holder_name varchar(255),
expired_date varchar(255),
cvv varchar(255),
date datetime not null,
status varchar(255),
admin_amount varchar(255),
owner_amount varchar(255),
customer_id int,
carrequest_id int,
foreign key(customer_id) references customers(customer_id),
foreign key(carrequest_id) references carrequests(carrequest_id)
);










