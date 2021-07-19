from flask import url_for, current_app, abort
from flask_login import current_user
from flask_mail import Message
from src import mail
from itsdangerous import URLSafeTimedSerializer
from src.models import User
from functools import wraps
import os
import secrets
import phonenumbers
from wtforms import (
    ValidationError
)


cat = {
    "Supermarket":
        ["Naivas", "Quickmart", "Carrefour", "Cleanshelf", "Quickmart"],
        "Electronics": [
            "Laptops & Computers", "Televisions", "TV Accessories",
            "Computer Accessories", "Home Theatres", "Speakers & Audio",
            "Printers & Scanners", "Security & Surveillance",
            "Video Games & Accessories", "Software"],
    "Mobile Phones & Tablets":
        ["Smartphones", "Tablets", "Smart Watches", "Mobile Accessories"],
    "Vehicles":
        [
            "Cars", "Motorcycles & Scooters", "Buses & Microbuses",
            "Trucks & Trailers", "Heavy Equipment", "Vehicle Accessories"],
    "Home, Furniture & Appliances":
        [
            "Furniture", "Home Accessories", "Kitchen Appliances",
            "Home Appliances", "Kitchen & Dining", "Garden"],
    "Property":
        [
            "Land & Plots for Sale", "Land & Plots for Rent",
            "Houses & Apartments for Sale", "Houses & Apartments for Sale",
            "Commercial Property for Sale", "Commercial Property for Rent",
            "Short Stay", "Events & Workstations"],
    "Health & Beauty":
        [
            "Bath & Body", "Dental Care", "Makeup & Cosmetics",
            "Manicure & Pedicure", "Vitamins & Supplements", "Sexual Wellness",
            "Vision & Eye care", "Skin Care", "Health Care", "Hair Beauty",
            "Tools & Accessories"],
    "Services":
        [
            "Computer & IT Services", "Cleaning Services",
            "Automotive Services", "Health & Beauty services",
            "Daycare Services", "Legal Services", "Tour & Travel Services",
            "Entertainment Services", "Printing Services",
            "Veterinary Services", "Fitness & Personal Training Services",
            "Chauffer & Transport", "Moving & Relocation Services"],
    "Agriculture & Food":
        [
            "Farm Machinery & Equipment", "Feeds Supplements & Seeds",
            "Meals & Drinks"],
    "Restaurants & Bars":
        ["Restaurants", "Bars"],
    "Farm Produce":
        ["Cereals", "Fruits", "Vegetables", "Livestock", "Poultry", "Fish"],
    "Fashion":
        [
            "Shoes", "Clothing", "Jewelry", "Bags", "Watches",
            "Wedding Wear & Accessories", "Sunglasses & Eye Wear",
            "Clothing Accessories"],
    "Sports, Leisure & Travel":
        [
            "Sports & Gym Equipment", "Bicycles & Biking Accessories",
            "Camping & Hiking", "Arts & Crafts", "Books & Games",
            "Musical Instruments & Gear"],
    "Alcohol":
        [
            "Beer", "Whiskey", "Mixers", "Gin", "Tequila", "Cognac", "Rum",
            "Liqueur", "Champagne", "Wine", "Vodka"],
    "Commercial Tools & Equipment":
        [
            "Industrial Ovens", "Manufacturing Equipment & Materials",
            "Medical Supplies & Equipment", "Printing Equipment",
            "Restaurant & Catering Equipment", "Salon Equipment", "Stationery",
            "Safety Wear & Equipment", "Store Equipment"],
    "Hardware & Construction":
        [
            "Building Materials", "Electrical Equipment",
            "Plumbing & Borehole", "Windows & Doors", "Hand tools",
            "Solar Energy", "Flooring", "Outdoor Power Equipment",
            "Measuring & Layout Tools", "Others"],
    "Animals & Pets":
        [
            "Dogs & Puppies", "Cats & Kittens", "Pets Accessories", "Others"],
    "Baby, Kids & Toys":
        [
            "Toys", "Baby Care", "Babies & Kids Accessories",
            "Children’s Clothing", "Children’s Furniture", "Children’s Shoes",
            "Children’s Gear & Safety", "Maternity & Pregnancy",
            "Car Seats & Accessories", "Prams & Strollers"],
    "Household Supplies":
        [
            "Air Fresheners", "Papers & Rolls", "Bathroom Cleaners",
            "Bulb & Batteries", "Floor Cleaners",
            "Household Cleaners & Sundries", "Kitchen Cleaner", "Laundry"],
    "Food Cupboard":
        [
            "Cooking Ingredients", "Snacks Crisps & Nuts", "Grains & Rice",
            "Sugar & Flour", "Breakfast Cereals", "Candy & Chocolate",
            "Margarine & Jams", "Honey & Spreads"],
    "Drinks":
        [
            "Carbonated Drinks", "Coffee Tea & Cocoa", "Water",
            "Syrups & Cordials", "Dairy", "Juices & Non-Carbonated Drinks"]
}

loc = [
    "Kajiado", "Kiambu", "Mombasa", "Nairobi", "Nakuru", "Baringo", "Bomet",
    "Bungoma", "Busia", "Elgeyo-Marakwet", "Embu", "Garissa", "Homa Bay",
    "Isiolo", "Kakamega", "Kericho", "Kilifi", "Kirinyaga", "Kisii", "Kisumu",
    "Kitui", "Kwale", "Laikipia", "Lamu", "Machakos", "Makueni", "Mandera",
    "Marsabit", "Meru", "Migori", "Murang'a", "Nandi", "Narok", "Nyamira",
    "Nyandarua", "Nyeri", "Samburu", "Siaya", "Taita Taveta", "Tana River",
    "Tharaka-Nithi", "Trans-Nzoia", "Turkana", "Uasin Gishu", "Vihiga",
    "Wajir", "West Pokot"
]


def validate_image(image):
    _, ext = os.path.splitext(image.filename)
    pname = secrets.token_hex(20) + ext
    image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], pname))
    return pname


def validate_profile_image(image):
    _, ext = os.path.splitext(image.filename)
    pname = secrets.token_hex(20) + ext
    image.save(os.path.join(current_app.config['PROFILE_PICS_FOLDER'], pname))
    return pname


def send_mail(subject, recepient, sender, html_body):
    mesage = Message(subject=subject, recipients=recepient, sender=sender)
    mesage.html = html_body
    mail.send(mesage)


def send_mail_reset_email(user):
    token = user.get_reset_password_token(user)
    msg = Message(
        "Password reset request", sender="vicjuma945@gmail.com", recipients=[
            user.email])
    msg.body = f'''To reset your password, follow this \
        link {url_for(
            'src.views.users.reset_token', token=token, _external=True)}'''
    mail.send(msg)


def adminsonly():
    def restrict(f):
        @wraps(f)
        def wrapperfunc(*args, **kwargs):
            if (
                current_user.is_authenticated is True) and (
                    current_user.is_admin is False):
                abort(403)
            return f(*args, **kwargs)
        return wrapperfunc
    return restrict


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(current_app.secret_key)
    return serializer.dumps(email, salt=current_app.secret_key)


def confirm_confirmation_token(token, expiration=None):
    serializer = URLSafeTimedSerializer(current_app.secret_key)
    try:
        email = serializer.loads(
            token,
            salt=current_app.secret_key,
            max_age=expiration
        )
    except User.DoesNotExist:
        return False
    return email


def validate_phone(self, phone):
    try:
        p = phonenumbers.parse(phone.data)
        if not phonenumbers.is_valid_number(p):
            raise ValueError()
    except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
        raise ValidationError('Invalid phone number, please insert your pgone in the \
            format +254712345678')


def valid_username(self, username):
    try:
        if not username.data.replace(" ", "").isalpha():
            raise ValueError()
    except (ValueError):
        raise ValidationError("Username can only contain letters, \
            kindly remove any numeric characters")
