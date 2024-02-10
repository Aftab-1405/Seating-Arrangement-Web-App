"""
Step-by-Step Documentation:

    1. Import necessary modules and classes for the Flask application, PDF generation, SQLAlchemy database, and user authentication.
    2. Initialize the Flask application, configure it, and set up the database.
    3. Define the User class for database model and user authentication.
    4. Create FlaskForm classes for user registration and login.
    5. Define routes for home, login, index, logout, and register pages.
    6. Implement custom PDF class (SeatingArrangementPDF) for seating arrangement.
    7. Define header and footer methods in SeatingArrangementPDF for customization.
    8. Define a route for generating PDF based on form submission.
    9. Extract form data, create a SeatingArrangementPDF object, and generate tables.
    10. Output the PDF and serve it for download.
    11. Run the application if executed as the main script.

"""

from flask import Flask, render_template, request, send_file, url_for, redirect
from fpdf import FPDF
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from flask import flash 

# Initialize Flask application
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'AFTAB@1405'
db = SQLAlchemy()
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    
# VERY IMPORTANT
with app.app_context():
    db.create_all()
    
class RegisterForm(FlaskForm):
    # Registration form with validators and placeholders
    username = StringField(validators=[InputRequired(), Length(min=4, max=50)],
                        render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)],
                            render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError('That username already exists. Please choose a different one.')

class LoginForm(FlaskForm):
    # Login form with validators and placeholders
    username = StringField(validators=[InputRequired(), Length(min=8, max=50)],
                        render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)],
                            render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')

@app.route('/')
def home():
    # Render the home page
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Handle login page with validation and redirection
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Successfully logged in')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    return render_template('login.html', form=form)

@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    # Render the index page, accessible only to logged-in users
    return render_template('index.html')

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    # Handle logout and redirect to the login page
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Handle user registration and redirection
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

class SeatingArrangementPDF(FPDF):
    # Custom PDF class for seating arrangement

    def __init__(self, *args, **kwargs):
        # Initialize the PDF object with additional attributes
        super().__init__(*args, **kwargs)
        self.date, self.day, self.start_time, self.end_time = None, None, None, None
        self.branch, self.subject, self.room_no = None, None, None

    def header(self):
        # Add custom header to each page
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, "DEPARTMENT OF TECHNOLOGY, SUK", ln=True, align='C')
        self.cell(0, 10, "Seating Arrangement SEE", ln=True, align='C')

        # Add additional details if available
        if all([self.date, self.day, self.start_time, self.end_time, self.branch, self.subject, self.room_no]):
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, f"Date: {self.date}   Day: {self.day}   Time: {self.start_time} - {self.end_time}", ln=True, align='C')
            self.cell(0, 10, f"Branch: {self.branch}   Subject: {self.subject}", ln=True, align='C')
            self.cell(0, 10, f"Room No: {self.room_no}", ln=True, align='C')
            self.ln(10)

    def footer(self):
        # Add custom footer to each page
        self.set_y(-15)
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')
        self.set_text_color(255, 0, 0)
        self.cell(0, 14, 'Developed by AFTAB-1405', 0, 0, 'R')
        self.set_text_color(0)

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    # Route for generating PDF based on form submission

    # Extract form data
    date, day, start_time, end_time = request.form.get('date'), request.form.get('day'), request.form.get('startTime'), request.form.get('endTime')
    room_no, branch, subject = request.form.get('roomNo'), request.form.get('branch'), request.form.get('subject')
    seat_numbers, bench_numbers = request.form.getlist('seatNo[]'), request.form.getlist('benchNo[]')

    # Create SeatingArrangementPDF object
    pdf = SeatingArrangementPDF('L', 'mm', 'A4')
    pdf.date, pdf.day, pdf.start_time, pdf.end_time = date, day, start_time, end_time
    pdf.branch, pdf.subject, pdf.room_no = branch, subject, room_no

    pdf.set_auto_page_break(auto=False)
    pdf.add_page()

    col_width, row_height, y_position = 30, 10, 70

    # Generate tables for seat and bench numbers
    for i in range(0, len(seat_numbers), 10):
        if i % 40 == 0 and i != 0:
            pdf.add_page()
            y_position = 70

        x_position = 10 + ((i // 10) % 4) * (col_width * 2 + 10)

        # Add header with light blue background color
        pdf.set_xy(x_position, y_position)
        pdf.set_fill_color(173, 216, 230)  # Light blue background color
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(col_width, row_height, 'Bench No', 1, 0, 'C', 1)
        pdf.cell(col_width, row_height, 'Seat No', 1, 1, 'C', 1)

        # Reset background color to white for table content
        pdf.set_fill_color(255, 255, 255)
        pdf.set_font('Arial', '', 10)

        # Populate table with seat and bench numbers
        for j in range(10):
            index = i + j
            if index >= len(seat_numbers):
                break
            pdf.set_x(x_position)
            pdf.cell(col_width, row_height, bench_numbers[index], 1, 0, 'C')
            pdf.cell(col_width, row_height, seat_numbers[index], 1, 1, 'C')

        # Adjust position for a new set of tables
        if (i // 10) % 4 == 3:
            y_position += 40

    # Output the PDF and serve it for download
    pdf_file_path = 'exam_sitting_arrangement.pdf'
    pdf.output(pdf_file_path)
    return send_file(pdf_file_path, as_attachment=True)

# Run the application if executed as the main script
if __name__ == '__main__':
    app.run(debug=True)