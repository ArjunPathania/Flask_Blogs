from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp,URL
from flask_ckeditor import CKEditorField


# WTForm for creating a blog post
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


#Create a RegisterForm to register new users
class RegisterForm(FlaskForm):
    name = StringField(
        "Enter Your Name",
        validators=[
            DataRequired(),
            Length(min=2, max=50, message="Name must be between 2 and 50 characters."),
            Regexp(r'^[a-zA-Z\s]+$', message="Name can only contain letters and spaces.")
        ]
    )

    email = StringField(
        "Email Address",
        validators=[
            DataRequired(),
            Email(message="Invalid email address."),
            Length(max=100, message="Email address must not exceed 100 characters.")
        ]
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=8, max=128, message="Password must be between 8 and 128 characters."),
            Regexp(
                r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*]).{8,128}$',
                message=(
                    "Password must contain at least one uppercase letter, one lowercase letter, "
                    "one digit, and one special character (!@#$%^&*)."
                )
            )
        ]
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo('password', message="Passwords must match.")
        ]
    )

    submit = SubmitField("Start Blogging")


# Create a LoginForm to login existing users
class LoginForm(FlaskForm):
    email = StringField(
        "Email Address",
        validators=[
            DataRequired(),
            Email(message="Invalid email address."),
        ]
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
        ]
    )
    submit = SubmitField("Login")

# Create a CommentForm so users can leave comments below posts
class CommentForm(FlaskForm):
    comment = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit Comment")


# Form class using Flask-WTF
class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=50)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone = StringField("Phone Number", validators=[DataRequired(), Length(max=15)])
    message = TextAreaField("Message", validators=[DataRequired(), Length(max=500)])
    submit = SubmitField("Send")
