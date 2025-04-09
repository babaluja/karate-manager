from flask import render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
import calendar
from sqlalchemy import extract, func
import json
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from flask_login import login_user, logout_user, login_required, current_user

from app import app, db
from models import Athlete, Payment, Exam, BELT_COLORS, User

# Add 'now' variable to all templates
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# Custom filter for belt colors
@app.template_filter('belt_color')
def belt_color_filter(belt_index):
    colors = [
        '#f8f9fa',  # Bianca
        '#fff59d',  # Bianca-Gialla
        '#ffeb3b',  # Gialla
        '#ffd54f',  # Gialla-Arancione
        '#ffa726',  # Arancione
        '#aed581',  # Arancione-Verde
        '#4caf50',  # Verde
        '#26a69a',  # Verde-Blu
        '#2196f3',  # Blu
        '#795548',  # Blu-Marrone
        '#5d4037',  # Marrone
        '#212529',  # Nera 1° Dan
        '#212529',  # Nera 2° Dan
        '#212529',  # Nera 3° Dan
        '#212529',  # Nera 4° Dan
        '#212529'   # Nera 5° Dan
    ]
    return colors[belt_index]

@app.route('/')
def index():
    """Homepage with dashboard"""
    # Get counts for dashboard
    athletes_count = Athlete.query.filter_by(active=True).count()
    
    # Get current month's payments total
    current_month = datetime.now().month
    current_year = datetime.now().year
    monthly_payments = Payment.query.filter(
        Payment.month == current_month,
        Payment.year == current_year
    ).with_entities(func.sum(Payment.amount)).scalar() or 0
    
    # Get yearly payments total
    yearly_payments = Payment.query.filter(
        Payment.year == current_year
    ).with_entities(func.sum(Payment.amount)).scalar() or 0
    
    # Get belt distribution
    belt_counts = db.session.query(
        Athlete.belt_color, func.count(Athlete.id)
    ).filter_by(active=True).group_by(Athlete.belt_color).all()
    
    belt_distribution = {belt: 0 for belt in BELT_COLORS}
    for belt, count in belt_counts:
        belt_distribution[belt] = count
    
    # Get monthly payments by month
    monthly_payment_data = db.session.query(
        Payment.month, func.sum(Payment.amount)
    ).filter(
        Payment.year == current_year
    ).group_by(Payment.month).all()
    
    monthly_data = [0] * 12
    for month, amount in monthly_payment_data:
        monthly_data[month-1] = float(amount)
    
    return render_template(
        'index.html', 
        athletes_count=athletes_count,
        monthly_payments=monthly_payments,
        yearly_payments=yearly_payments,
        belt_distribution=json.dumps(belt_distribution),
        monthly_data=json.dumps(monthly_data)
    )

# Athletes Routes
@app.route('/athletes')
@login_required
def athletes_list():
    """List all athletes"""
    athletes = Athlete.query.order_by(Athlete.last_name).all()
    return render_template('athletes.html', athletes=athletes, belt_colors=BELT_COLORS)

@app.route('/athletes/new', methods=['GET', 'POST'])
@login_required
def add_athlete():
    """Add a new athlete"""
    if request.method == 'POST':
        try:
            birth_date = datetime.strptime(request.form['birth_date'], '%Y-%m-%d').date()
            enrollment_date = datetime.strptime(request.form['enrollment_date'], '%Y-%m-%d').date() if request.form['enrollment_date'] else datetime.now().date()
            
            monthly_fee = max(5.0, float(request.form['monthly_fee']) if request.form['monthly_fee'] else 5.0)
            
            athlete = Athlete(
                first_name=request.form['first_name'],
                last_name=request.form['last_name'],
                birth_date=birth_date,
                address=request.form['address'],
                phone=request.form['phone'],
                email=request.form['email'],
                belt_color=request.form['belt_color'],
                enrollment_date=enrollment_date,
                monthly_fee=monthly_fee,
                notes=request.form['notes'],
                active=('active' in request.form)
            )
            
            db.session.add(athlete)
            db.session.commit()
            flash('Atleta aggiunto con successo!', 'success')
            return redirect(url_for('athletes_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Errore: {str(e)}', 'danger')
    
    return render_template('athlete_form.html', athlete=None, belt_colors=BELT_COLORS)

@app.route('/athletes/<int:athlete_id>')
@login_required
def athlete_detail(athlete_id):
    """Show athlete details"""
    athlete = Athlete.query.get_or_404(athlete_id)
    payments = Payment.query.filter_by(athlete_id=athlete_id).order_by(Payment.payment_date.desc()).all()
    exams = Exam.query.filter_by(athlete_id=athlete_id).order_by(Exam.exam_date.desc()).all()
    
    return render_template('athlete_detail.html', athlete=athlete, payments=payments, exams=exams, belt_colors=BELT_COLORS)

@app.route('/athletes/<int:athlete_id>/edit', methods=['GET', 'POST'])
def edit_athlete(athlete_id):
    """Edit athlete"""
    athlete = Athlete.query.get_or_404(athlete_id)
    
    if request.method == 'POST':
        try:
            athlete.first_name = request.form['first_name']
            athlete.last_name = request.form['last_name']
            athlete.birth_date = datetime.strptime(request.form['birth_date'], '%Y-%m-%d').date()
            athlete.address = request.form['address']
            athlete.phone = request.form['phone']
            athlete.email = request.form['email']
            athlete.belt_color = request.form['belt_color']
            athlete.enrollment_date = datetime.strptime(request.form['enrollment_date'], '%Y-%m-%d').date()
            athlete.monthly_fee = max(5.0, float(request.form['monthly_fee']) if request.form['monthly_fee'] else 5.0)
            athlete.notes = request.form['notes']
            athlete.active = ('active' in request.form)
            
            db.session.commit()
            flash('Atleta aggiornato con successo!', 'success')
            return redirect(url_for('athlete_detail', athlete_id=athlete.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Errore: {str(e)}', 'danger')
    
    return render_template('athlete_form.html', athlete=athlete, belt_colors=BELT_COLORS)

@app.route('/athletes/<int:athlete_id>/delete', methods=['POST'])
def delete_athlete(athlete_id):
    """Delete athlete"""
    athlete = Athlete.query.get_or_404(athlete_id)
    
    try:
        db.session.delete(athlete)
        db.session.commit()
        flash('Atleta eliminato con successo!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore: {str(e)}', 'danger')
    
    return redirect(url_for('athletes_list'))

# Payment Routes
@app.route('/payments', methods=['GET'])
def payments_list():
    """List payments with filters"""
    # Get filter parameters
    month = request.args.get('month', default=datetime.now().month, type=int)
    year = request.args.get('year', default=datetime.now().year, type=int)
    athlete_id = request.args.get('athlete_id', default=None, type=int)
    
    query = Payment.query
    
    # Apply filters
    if month:
        query = query.filter(Payment.month == month)
    if year:
        query = query.filter(Payment.year == year)
    if athlete_id:
        query = query.filter(Payment.athlete_id == athlete_id)
    
    payments = query.order_by(Payment.payment_date.desc()).all()
    
    # Get total
    total = sum(payment.amount for payment in payments)
    
    # Get all athletes for filter dropdown
    athletes = Athlete.query.order_by(Athlete.last_name).all()
    
    # Prepare month names for select
    months = [(i, calendar.month_name[i]) for i in range(1, 13)]
    
    # Get year range
    current_year = datetime.now().year
    years = list(range(current_year - 5, current_year + 2))
    
    return render_template(
        'payments.html', 
        payments=payments, 
        total=total,
        athletes=athletes,
        months=months,
        years=years,
        selected_month=month,
        selected_year=year,
        selected_athlete_id=athlete_id
    )

@app.route('/athletes/<int:athlete_id>/payments/add', methods=['POST'])
def add_payment(athlete_id):
    """Add payment for an athlete"""
    athlete = Athlete.query.get_or_404(athlete_id)
    
    try:
        payment_date = datetime.strptime(request.form['payment_date'], '%Y-%m-%d').date()
        amount = float(request.form['amount'])
        month = int(request.form['month'])
        year = int(request.form['year'])
        
        payment = Payment(
            athlete_id=athlete.id,
            amount=amount,
            payment_date=payment_date,
            month=month,
            year=year,
            payment_method=request.form['payment_method'],
            notes=request.form['notes']
        )
        
        db.session.add(payment)
        db.session.commit()
        flash('Pagamento registrato con successo!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore: {str(e)}', 'danger')
    
    return redirect(url_for('athlete_detail', athlete_id=athlete.id))

@app.route('/payments/<int:payment_id>/delete', methods=['POST'])
def delete_payment(payment_id):
    """Delete payment"""
    payment = Payment.query.get_or_404(payment_id)
    athlete_id = payment.athlete_id
    
    try:
        db.session.delete(payment)
        db.session.commit()
        flash('Pagamento eliminato con successo!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore: {str(e)}', 'danger')
    
    return redirect(url_for('athlete_detail', athlete_id=athlete_id))

# Exam Routes
@app.route('/athletes/<int:athlete_id>/exams/add', methods=['POST'])
def add_exam(athlete_id):
    """Add exam for an athlete"""
    athlete = Athlete.query.get_or_404(athlete_id)
    
    try:
        exam_date = datetime.strptime(request.form['exam_date'], '%Y-%m-%d').date()
        fee = float(request.form['fee'])
        
        exam = Exam(
            athlete_id=athlete.id,
            exam_date=exam_date,
            previous_belt=athlete.belt_color,
            new_belt=request.form['new_belt'],
            result=request.form['result'],
            fee=fee,
            paid=('paid' in request.form),
            notes=request.form['notes']
        )
        
        # Update athlete belt if exam is passed
        if exam.result == 'Passed':
            athlete.belt_color = exam.new_belt
        
        db.session.add(exam)
        db.session.commit()
        flash('Esame registrato con successo!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore: {str(e)}', 'danger')
    
    return redirect(url_for('athlete_detail', athlete_id=athlete.id))

@app.route('/exams/<int:exam_id>/delete', methods=['POST'])
def delete_exam(exam_id):
    """Delete exam"""
    exam = Exam.query.get_or_404(exam_id)
    athlete_id = exam.athlete_id
    
    try:
        db.session.delete(exam)
        db.session.commit()
        flash('Esame eliminato con successo!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore: {str(e)}', 'danger')
    
    return redirect(url_for('athlete_detail', athlete_id=athlete_id))

# Reports Route
@app.route('/reports')
def reports():
    """Financial and statistics reports"""
    # Get year for reporting
    year = request.args.get('year', default=datetime.now().year, type=int)
    
    # Monthly payment totals for the year
    monthly_totals = db.session.query(
        Payment.month,
        func.sum(Payment.amount).label('total')
    ).filter(
        Payment.year == year
    ).group_by(Payment.month).all()
    
    # Create a list with all months (even those with 0)
    monthly_data = [0] * 12
    for month, total in monthly_totals:
        monthly_data[month-1] = float(total)
    
    # Belt distribution
    belt_distribution = db.session.query(
        Athlete.belt_color, 
        func.count(Athlete.id)
    ).filter_by(active=True).group_by(Athlete.belt_color).all()
    
    belt_data = {belt: 0 for belt in BELT_COLORS}
    for belt, count in belt_distribution:
        belt_data[belt] = count
    
    # Payment methods distribution
    payment_methods = db.session.query(
        Payment.payment_method,
        func.sum(Payment.amount).label('total')
    ).filter(
        Payment.year == year
    ).group_by(Payment.payment_method).all()
    
    # Total income for year
    yearly_total = sum(monthly_data)
    
    # Years for dropdown
    current_year = datetime.now().year
    years = list(range(current_year - 5, current_year + 2))
    
    return render_template(
        'reports.html',
        year=year,
        years=years,
        monthly_data=monthly_data,
        monthly_data_json=json.dumps(monthly_data),
        belt_data=json.dumps(belt_data),
        payment_methods=payment_methods,
        yearly_total=yearly_total
    )

# API endpoints for AJAX calls
@app.route('/api/athletes/search')
def search_athletes():
    """Search athletes by name"""
    query = request.args.get('q', '')
    athletes = Athlete.query.filter(
        (Athlete.first_name.ilike(f'%{query}%')) | 
        (Athlete.last_name.ilike(f'%{query}%'))
    ).all()
    
    results = [{'id': a.id, 'name': a.full_name, 'belt': a.belt_color} for a in athletes]
    return jsonify(results)

@app.route('/api/monthly-data')
def get_monthly_data():
    """Get monthly payment data for the year"""
    year = request.args.get('year', default=datetime.now().year, type=int)
    
    monthly_totals = db.session.query(
        Payment.month,
        func.sum(Payment.amount).label('total')
    ).filter(
        Payment.year == year
    ).group_by(Payment.month).all()
    
    # Create a list with all months (even those with 0)
    monthly_data = [0] * 12
    for month, total in monthly_totals:
        monthly_data[month-1] = float(total)
    
    return jsonify(monthly_data)

@app.route('/api/belt-distribution')
def get_belt_distribution():
    """Get belt distribution data"""
    belt_distribution = db.session.query(
        Athlete.belt_color, 
        func.count(Athlete.id)
    ).filter_by(active=True).group_by(Athlete.belt_color).all()
    
    belt_data = {belt: 0 for belt in BELT_COLORS}
    for belt, count in belt_distribution:
        belt_data[belt] = count
    
    return jsonify(belt_data)


# Forms per autenticazione
class LoginForm(FlaskForm):
    """Form per il login"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    pin = PasswordField('PIN (opzionale)', validators=[Length(min=4, max=6)])
    remember_me = BooleanField('Ricordami')
    submit = SubmitField('Accedi')


class RegistrationForm(FlaskForm):
    """Form per la registrazione"""
    username = StringField('Nome utente', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Conferma Password', validators=[DataRequired(), EqualTo('password')])
    pin = PasswordField('PIN numerico (4-6 cifre)', validators=[DataRequired(), Length(min=4, max=6)])
    submit = SubmitField('Registrati')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Questo nome utente è già in uso. Scegline un altro.')
            
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Questa email è già registrata. Utilizza un\'altra email.')
            
    def validate_pin(self, pin):
        if not pin.data.isdigit():
            raise ValidationError('Il PIN deve contenere solo numeri.')


# Rotte per autenticazione
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login utente"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        # Controlla se l'utente esiste e verifica la password o il PIN
        if user and (user.check_password(form.password.data) or 
                    (form.pin.data and user.check_pin(form.pin.data))):
            login_user(user, remember=form.remember_me.data)
            user.last_login = datetime.now()
            db.session.commit()
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            flash('Login fallito. Controlla email e password/PIN.', 'danger')
            
    return render_template('login.html', title='Accedi', form=form)


@app.route('/logout')
def logout():
    """Logout utente"""
    logout_user()
    flash('Sei stato disconnesso.', 'info')
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registrazione nuovo utente"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        user.set_pin(form.pin.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Account creato con successo! Ora puoi accedere.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html', title='Registrazione', form=form)


@app.route('/pin-login', methods=['GET', 'POST'])
def pin_login():
    """Login rapido con PIN"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        pin = request.form.get('pin')
        email = request.form.get('email')
        
        if pin and email:
            user = User.query.filter_by(email=email).first()
            if user and user.check_pin(pin):
                login_user(user, remember=True)
                user.last_login = datetime.now()
                db.session.commit()
                return redirect(url_for('index'))
        
        flash('PIN non valido. Riprova.', 'danger')
    
    return render_template('pin_login.html', title='Accesso PIN')
