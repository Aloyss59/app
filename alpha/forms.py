# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TelField
from wtforms.validators import DataRequired, Length, EqualTo, Email, Regexp

class RegistrationForm(FlaskForm):
    first_name = StringField('Prénom', validators=[DataRequired(), Regexp(r'[A-Za-zÀ-ÖØ-Ýà-öø-ÿ]+')])
    last_name = StringField('Nom', validators=[DataRequired(), Regexp(r'[A-Za-zÀ-ÖØ-Ýà-öø-ÿ]+')])
    phone = TelField('Numéro de téléphone', validators=[Regexp(r'[0-9]+')])
    username = StringField('Nom d’utilisateur', validators=[DataRequired(), Length(min=3), Regexp(r'[A-Za-zÀ-ÖØ-Ýà-öø-ÿ0-9.]+')])
    email = StringField('Adresse Mail', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[
        DataRequired(),
        Length(min=6),
        Regexp(r'(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@#$%^&*!])[A-Za-z\d@#$%^&*!]{8,}')
    ])
    confirm_password = PasswordField('Confirmez le mot de passe', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Créer un compte')

class LoginForm(FlaskForm):
    username = StringField(
        'Nom d\'utilisateur / Adresse mail',
        validators=[
            DataRequired(),
            Length(min=3, max=150),
            Regexp(r'[A-Za-zÀ-ÖØ-Ýà-öø-ÿ0-9.]+')
        ]
    )
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    submit = SubmitField('Se connecter')
