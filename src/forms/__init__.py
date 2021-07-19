from flask_wtf import FlaskForm
from wtforms import (
    PasswordField,
    StringField,
    SubmitField,
    SelectField,
    IntegerField,
    ValidationError
)
from wtforms.fields.core import BooleanField, DateTimeField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import Email, Length, InputRequired, EqualTo
from wtforms.fields.html5 import DateTimeLocalField
from src.models import User
from flask_wtf.file import FileField, FileRequired
from src.utils import validate_phone, valid_username


# =====================Sign up for a user account.============================
class SignupForm(FlaskForm):
    username = StringField(
        'Username', validators=[InputRequired(
            "Please enter your username."), Length(
                min=2, max=25), valid_username]
        )
    email = StringField(
        "Email",
        [
            Email(message="Not a valid email address."),
            InputRequired("Please enter a valid email address."), Length(
                    min=7, max=35)]
    )
    phone = StringField(
        'Phone', validators=[
            InputRequired(
                "Please enter your phone number in a \
                    valid format"), validate_phone]
        )
    password = PasswordField(
        "Password",
        validators=[Length(
                    min=8, max=50)]
    )
    submit = SubmitField("Sign Up")


# =====================Log into a user account.=========================
class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        [
            Email(message="Not a valid email address."),
            InputRequired("Please enter a valid email address."), Length(
                    min=7, max=35)]
    )
    password = PasswordField(
        "Password",
        [InputRequired("Please enter a password.")],
    )
    remember_me = BooleanField("Remenber Me")
    submit = SubmitField("Log In")


# ===================== Creating an offer for authenticated user ==============
class AddProductForm(FlaskForm):
    """Adds a product."""
    product_name = StringField(
        'Product Name', validators=[InputRequired(
            "Please enter the product name."), Length(
                min=2, max=100)]
        )
    product_location = SelectField("Location", choices=[
        ("Kajiado", "Kajiado"), ("Kiambu", "Kiambu"), ("Mombasa", "Mombasa"),
        ("Nairobi", "Nairobi"),
        ("Nakuru", "Nakuru"), ("Baringo", "Baringo"), ("Bomet", "Bomet"),
        ("Bungoma", "Bungoma"), ("Busia", "Busia"), (
            "Elgeyo-Marakwet", "Elgeyo-Marakwet"),
        ("Embu", "Embu"), ("Garissa", "Garissa"), ("Homa Bay", "Homa Bay"),
        ("Isiolo", "Isiolo"), ("Kakamega", "Kakamega"), ("Kericho", "Kericho"),
        ("Kilifi", "Kilifi"), ("Kirinyaga", "Kirinyaga"), ("Kisii", "Kisii"),
        ("Kisumu", "Kisumu"), ("Kitui", "Kitui"), ("Kwale", "Kwale"),
        ("Laikipia", "Laikipia"), ("Lamu", "Lamu"), ("Machakos", "Machakos"),
        ("Makueni", "Makueni"), ("Mandera", "Mandera"), (
            "Marsabit", "Marsabit"),
        ("Meru", "Meru"), ("Migori", "Migori"), ("Murang", "Murang'a"),
        ("Nandi", "Nandi"), ("Narok", "Narok"), ("Nyamira", "Nyamira"),
        ("Nyandarua", "Nyandarua"), ("Nyeri", "Nyeri"), ("Samburu", "Samburu"),
        ("Siaya", "Siaya"), ("Taita Taveta", "Taita Taveta"), (
            "Tana River", "Tana River"),
        ("Tharaka-Nithi", "Tharaka-Nithi"), (
            "Trans-Nzoia", "Trans-Nzoia"), ("Turkana", "Turkana"),
        ("Uasin Gishu", "Uasin Gishu"), ("Vihiga", "Vihiga"), (
            "Wajir", "Wajir"),
        ("West Pokot", "West Pokot")])

    offer_start_date = DateTimeField('Offer Start Date')
    offer_end_date = DateTimeLocalField(
        'Offer End Date', format='%Y-%m-%dT%H:%M')
    offer_previous_price = IntegerField(
        'Offer Previous Price', validators=[InputRequired(
            "Please enter the product market price.")])
    offer_current_price = IntegerField(
        'Offer Current Price', validators=[InputRequired(
            "Please enter the product selling price.")])
    product_category = SelectField("Product Category", choices=[
        ("Supermarket", "Supermarket"), ("Electronics", "Electronics"), (
            "Mobile Phones & Tablets", "Mobile Phones & Tablets"),
        ("Vehicles", "Vehicles"), (
            "Home, Furniture & Appliances", "Home, Furniture & Appliances"), (
            "Property", "Property"),
        ("Health & Beauty", "Health & Beauty"), ("Services", "Services"),
        ("Agriculture & Food", "Agriculture & Food"), (
            "Restaurants & Bars", "Restaurants & Bars"), (
            "Farm Produce", "Farm Produce"),
        ("Fashion", "Fashion"), (
            "Sports, Leisure & Travel", "Sports, Leisure & Travel"), (
            "Alcohol", "Alcohol"),
        ("Commercial Tools & Equipment", "Commercial Tools & Equipment"), (
            "Hardware & Construction", "Hardware & Construction"),
        ("Animals & Pets", "Animals & Pets"), (
            "Baby, Kids & Toys", "Baby, Kids & Toys"), (
            "Household Supplies", "Household Supplies"),
        ("Food Cupboard", "Food Cupboard"), ("Drinks", "Drinks")], coerce=str)
    product_subcategory = SelectField(
        "Product Subcategory", choices=[], coerce=str,
        validate_choice=False, validators=[
            InputRequired('value required')])
    stock_available = IntegerField(
        'Available Stock', validators=[InputRequired(
            "Enter the available stock.")])
    product_image_one = FileField(validators=[FileRequired("You must provide at least \
        2 files for your product")])
    product_image_two = FileField(validators=[FileRequired("You must provide at least \
        2 files for your product")])
    product_description = TextAreaField(
        "Product Description", validators=[InputRequired(
            "Provide a short description of your offer")])
    terms_checkbox = BooleanField(
        'I agree to terms and conditions', validators=[
            InputRequired("You must agree to the terms and conditions"), ])
    offer_checkbox = BooleanField(
        'I guarantee that this offer is genuine', validators=[
            InputRequired("You must confirm genuinity of the offer"), ])
    genuine_checkbox = BooleanField(
        'I guarantee that this product is genuine', validators=[
            InputRequired("You must confirm genuinity of the product"), ])
    submit = SubmitField("Submit Offer")


class SearchForm(FlaskForm):
    """Search a product."""
    search_query = StringField(
        'q', validators=[InputRequired(
            "Please enter the search term."), Length(
                min=2, max=25)]
        )
    product_location = SelectField("Location", choices=[
        ("All in Kenya", "All in Kenya"),
        ("Kajiado", "Kajiado"), ("Kiambu", "Kiambu"), ("Mombasa", "Mombasa"),
        ("Nairobi", "Nairobi"),
        ("Nakuru", "Nakuru"), ("Baringo", "Baringo"), ("Bomet", "Bomet"),
        ("Bungoma", "Bungoma"), ("Busia", "Busia"), (
            "Elgeyo-Marakwet", "Elgeyo-Marakwet"),
        ("Embu", "Embu"), ("Garissa", "Garissa"), ("Homa Bay", "Homa Bay"),
        ("Isiolo", "Isiolo"), ("Kakamega", "Kakamega"), ("Kericho", "Kericho"),
        ("Kilifi", "Kilifi"), ("Kirinyaga", "Kirinyaga"), ("Kisii", "Kisii"),
        ("Kisumu", "Kisumu"), ("Kitui", "Kitui"), ("Kwale", "Kwale"),
        ("Laikipia", "Laikipia"), ("Lamu", "Lamu"), ("Machakos", "Machakos"),
        ("Makueni", "Makueni"), ("Mandera", "Mandera"), (
            "Marsabit", "Marsabit"),
        ("Meru", "Meru"), ("Migori", "Migori"), ("Murang", "Murang'a"),
        ("Nandi", "Nandi"), ("Narok", "Narok"), ("Nyamira", "Nyamira"),
        ("Nyandarua", "Nyandarua"), ("Nyeri", "Nyeri"), ("Samburu", "Samburu"),
        ("Siaya", "Siaya"), ("Taita Taveta", "Taita Taveta"), (
            "Tana River", "Tana River"),
        ("Tharaka-Nithi", "Tharaka-Nithi"), (
            "Trans-Nzoia", "Trans-Nzoia"), ("Turkana", "Turkana"),
        ("Uasin Gishu", "Uasin Gishu"), ("Vihiga", "Vihiga"), (
            "Wajir", "Wajir"),
        ("West Pokot", "West Pokot")])
    product_category = SelectField("Product Category", choices=[
        ("Categories", "Categories"),
        ("Supermarket", "Supermarket"), ("Electronics", "Electronics"), (
            "Mobile Phones & Tablets", "Mobile Phones & Tablets"),
        ("Vehicles", "Vehicles"), (
            "Home, Furniture & Appliances", "Home, Furniture & Appliances"), (
            "Property", "Property"),
        ("Health & Beauty", "Health & Beauty"), ("Services", "Services"),
        ("Agriculture & Food", "Agriculture & Food"), (
            "Restaurants & Bars", "Restaurants & Bars"), (
            "Farm Produce", "Farm Produce"),
        ("Fashion", "Fashion"), (
            "Sports, Leisure & Travel", "Sports, Leisure & Travel"), (
            "Alcohol", "Alcohol"),
        ("Commercial Tools & Equipment", "Commercial Tools & Equipment"), (
            "Hardware & Construction", "Hardware & Construction"),
        ("Animals & Pets", "Animals & Pets"), (
            "Baby, Kids & Toys", "Baby, Kids & Toys"), (
            "Household Supplies", "Household Supplies"),
        ("Food Cupboard", "Food Cupboard"), ("Drinks", "Drinks")])
    submit = SubmitField("Search")


class RequestPasswordReset(FlaskForm):
    email = StringField(
        "Email", [Email(
            message="Not a valid email address."), InputRequired(
                "Please enter a valid email address."), Length(
                    min=7, max=35)]
    )
    submit = SubmitField("Request Password Reset")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError("That email does not exist, plase sign up")


class PasswordResetForm(FlaskForm):
    password = PasswordField(
        "Password", [InputRequired("Please enter a password.")])
    confirm_password = PasswordField(
        "Confirm Password", [InputRequired(
            "Please enter a password."), EqualTo('password')])
    submit = SubmitField("Reset Password")
