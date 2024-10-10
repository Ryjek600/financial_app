from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask_mail import Message
from extensions import db, mail
from models import User, DataEntry
import xml.etree.ElementTree as ET
from datetime import datetime

main = Blueprint('main', __name__)

@main.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for('main.login'))
    return render_template("index.html")

@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for('main.register'))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists.")
            return redirect(url_for('main.register'))

        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash("Email already registered.")
            return redirect(url_for('main.register'))

        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        try:
            db.session.commit()
            flash("Registration successful. Please log in.")
            return redirect(url_for('main.login'))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {e}")
            return redirect(url_for('main.register'))

    return render_template("register.html")

@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            flash("Login successful.")
            return redirect(url_for('main.index'))
        else:
            flash("Invalid username or password.")
            return redirect(url_for('main.login'))

    return render_template("login.html")

@main.route("/forgot_password", methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            token = generate_reset_token(user.email)
            send_reset_email(user.email, token)
            flash('Wysłano link resetujący hasło na adres e-mail.')
        else:
            flash('Nie znaleziono użytkownika z podanym e-mailem.')
        return redirect(url_for('main.forgot_password'))
    return render_template('forgot_password.html')

def generate_reset_token(email):
    s = Serializer(current_app.config['SECRET_KEY'], salt='password-reset-salt')
    return s.dumps({'email': email})

def verify_reset_token(token):
    try:
        s = Serializer(current_app.config['SECRET_KEY'])
        data = s.loads(token, salt='password-reset-salt', max_age=3600)  # Token ważny przez godzinę
    except Exception as e:
        print(f"Token verification error: {e}")
        return None
    return data

def send_reset_email(email, token):
    msg = Message('Resetowanie hasła',
                  sender='ryszardpiasecki299@gmail.com',
                  recipients=[email])
    msg.body = f'Kliknij w poniższy link, aby zresetować hasło:\n\n{url_for("main.reset_password", token=token, _external=True)}'
    mail.send(msg)

@main.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token, salt='password-reset-salt')
    except Exception as e:
        flash('Link resetujący hasło jest nieprawidłowy lub wygasł.')
        return redirect(url_for('main.forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password')
        if not password:
            flash('Hasło jest wymagane.')
            return redirect(url_for('main.reset_password', token=token))

        user = User.query.filter_by(email=data['email']).first()
        if user:
            user.password = generate_password_hash(password)
            db.session.commit()
            flash('Twoje hasło zostało zaktualizowane!')
            return redirect(url_for('main.login'))
        else:
            flash('Nie znaleziono użytkownika. Spróbuj ponownie.')
            return redirect(url_for('main.forgot_password'))

    return render_template('reset_password.html')

@main.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    flash("You have been logged out.")
    return redirect(url_for('main.index'))

@main.route("/results")
def results():
    entries = DataEntry.query.filter_by(user_id=session["user_id"]).order_by(DataEntry.submit_date.asc()).all()

    results = []
    for entry in entries:
        osn = (entry.short_term_receivables / entry.net_revenues * 365) if entry.net_revenues != 0 else None
        ouz = (entry.inventory / entry.operating_costs * 365) if entry.operating_costs != 0 else None
        orz = (entry.short_term_liabilities / entry.operating_costs * 365) if entry.operating_costs != 0 else None
        co = osn + ouz if osn is not None and ouz is not None else None
        ckg = co - orz if co is not None and orz is not None else None

        results.append({
            'submit_date': entry.submit_date,
            'date': entry.date,
            'liquidity_current': entry.current_assets / entry.short_term_liabilities if entry.short_term_liabilities != 0 else None,
            'liquidity_quick': (entry.current_assets - entry.inventory) / entry.short_term_liabilities if entry.short_term_liabilities != 0 else None,
            'liquidity_immediate': entry.cash_and_equivalents / entry.short_term_liabilities if entry.short_term_liabilities != 0 else None,
            'coverage_payables': entry.short_term_receivables / entry.trade_payables if entry.trade_payables != 0 else None,
            'osn': osn,
            'ouz': ouz,
            'orz': orz,
            'co': co,
            'ckg': ckg,
            'debt_ratio': (entry.short_term_liabilities + entry.long_term_liabilities) / entry.total_assets if entry.total_assets != 0 else None,
            'debt_equity_ratio': (entry.short_term_liabilities + entry.long_term_liabilities) / entry.equity if entry.equity != 0 else None,
            'long_term_debt_ratio': entry.long_term_liabilities / entry.equity if entry.equity != 0 else None,
            'liability_structure_ratio': entry.equity / (entry.short_term_liabilities + entry.long_term_liabilities) if (entry.short_term_liabilities + entry.long_term_liabilities) != 0 else None,
            'fixed_assets_debt_ratio': entry.fixed_assets / entry.long_term_liabilities if entry.long_term_liabilities != 0 else None,
            'source': entry.source
        })

    return render_template('results.html', results=results, entries=entries)

@main.route("/delete_entry/<int:entry_id>", methods=["POST"])
def delete_entry(entry_id):
    entry = DataEntry.query.get(entry_id)
    if entry and entry.user_id == session["user_id"]:
        db.session.delete(entry)
        db.session.commit()
        flash("Wpis został usunięty.")
    else:
        flash("Nie znaleziono wpisu lub brak uprawnień.")
    return redirect(url_for('main.results'))

@main.route("/upload")
def upload():
    return render_template("upload.html")

@main.route("/dataput", methods=["GET", "POST"])
def dataput():
    if request.method == "POST":
        date_str = request.form.get("date")
        total_assets = request.form.get("total_assets")
        fixed_assets = request.form.get("fixed_assets")
        current_assets = request.form.get("current_assets")
        short_term_receivables = request.form.get("short_term_receivables")
        cash_and_equivalents = request.form.get("cash_and_equivalents")
        inventory = request.form.get("inventory")
        short_term_liabilities = request.form.get("short_term_liabilities")
        long_term_liabilities = request.form.get("long_term_liabilities")
        trade_payables = request.form.get("trade_payables")
        equity = request.form.get("equity")
        net_revenues = request.form.get("net_revenues")
        operating_costs = request.form.get("operating_costs")

        if not all([date_str, total_assets, fixed_assets, current_assets,
                    short_term_receivables, cash_and_equivalents, inventory,
                    short_term_liabilities, long_term_liabilities,
                    trade_payables, equity, net_revenues, operating_costs]):
            flash("Wszystkie pola są wymagane.")
            return redirect(url_for('main.dataput'))

        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            total_assets = float(total_assets)
            fixed_assets = float(fixed_assets)
            current_assets = float(current_assets)
            short_term_receivables = float(short_term_receivables)
            cash_and_equivalents = float(cash_and_equivalents)
            inventory = float(inventory)
            short_term_liabilities = float(short_term_liabilities)
            long_term_liabilities = float(long_term_liabilities)
            trade_payables = float(trade_payables)
            equity = float(equity)
            net_revenues = float(net_revenues)
            operating_costs = float(operating_costs)

            data_entry = DataEntry(
                user_id=session["user_id"],
                date=date,
                total_assets=total_assets,
                fixed_assets=fixed_assets,
                current_assets=current_assets,
                short_term_receivables=short_term_receivables,
                cash_and_equivalents=cash_and_equivalents,
                inventory=inventory,
                short_term_liabilities=short_term_liabilities,
                long_term_liabilities=long_term_liabilities,
                trade_payables=trade_payables,
                equity=equity,
                net_revenues=net_revenues,
                operating_costs=operating_costs,
                submit_date=datetime.utcnow(),
                source='dataput'
            )
            db.session.add(data_entry)
            db.session.commit()
            flash("Dane zostały pomyślnie dodane.")
        except ValueError as ve:
            db.session.rollback()
            flash(f"Wystąpił błąd przy konwersji danych: {ve}")
        except Exception as e:
            db.session.rollback()
            flash(f"Wystąpił błąd: {e}")

        return redirect(url_for('main.results'))

    return render_template("dataput.html")

from flask import current_app  # Add this import

@main.route('/insertxml', methods=['POST'])
def insertxml():
    print("insertxml function called")
    current_app.logger.debug("Request Method: %s", request.method)
    current_app.logger.debug("Request Files: %s", request.files)

    if 'file' not in request.files:
        flash("No file part")
        current_app.logger.warning("No file part in request.")
        return redirect(url_for('main.upload'))

    file = request.files['file']
    date_str = request.form.get('date') 
    if file.filename == '':
        flash("No selected file")
        current_app.logger.warning("No file selected.")
        return redirect(url_for('main.upload'))

    if file and file.filename.endswith('.xml'):
        try:
            tree = ET.parse(file)
            root = tree.getroot()

            # Debugging: Print the XML structure
            current_app.logger.debug("Parsed XML: %s", ET.tostring(root, encoding='unicode'))

            namespaces = {
                'dtsf': 'http://www.mf.gov.pl/schematy/SF/DefinicjeTypySprawozdaniaFinansowe/2018/07/09/DefinicjeTypySprawozdaniaFinansowe/',
                'jin': 'http://www.mf.gov.pl/schematy/SF/DefinicjeTypySprawozdaniaFinansowe/2018/07/09/JednostkaInnaStruktury',
                'tns': 'http://www.mf.gov.pl/schematy/SF/DefinicjeTypySprawozdaniaFinansowe/2018/07/09/JednostkaInnaWZlotych'
            }

            # Helper function to safely extract text from XML
            def safe_find_text(xpath, namespaces):
                element = root.find(xpath, namespaces)
                return float(element.text) if element is not None and element.text is not None else 0.0

            # Extract data from XML with safe method
            total_assets = safe_find_text('.//dtsf:KwotaA', namespaces)
            fixed_assets = safe_find_text('.//jin:Aktywa_A_I//dtsf:KwotaA', namespaces)
            current_assets = safe_find_text('.//jin:Aktywa_A_II//dtsf:KwotaA', namespaces)
            short_term_receivables = safe_find_text('.//jin:Aktywa_A_II_1_B//dtsf:KwotaA', namespaces)
            cash_and_equivalents = safe_find_text('.//jin:Aktywa_B_III_1_C//dtsf:KwotaA', namespaces)
            inventory = safe_find_text('.//jin:Aktywa_B_I//dtsf:KwotaA', namespaces)
            short_term_liabilities = safe_find_text('.//jin:Pasywa_B_III//dtsf:KwotaA', namespaces)
            long_term_liabilities = safe_find_text('.//jin:Pasywa_B_II//dtsf:KwotaA', namespaces)
            trade_payables = safe_find_text('.//jin:Pasywa_B_II_1//dtsf:KwotaA', namespaces)
            equity = safe_find_text('.//jin:Pasywa_A//dtsf:KwotaA', namespaces)
            net_revenues = safe_find_text('.//jin:NettoPrzychody//dtsf:KwotaA', namespaces)
            operating_costs = safe_find_text('.//jin:KosztyOperacyjne//dtsf:KwotaA', namespaces)

            return redirect(url_for('main.preview_data', 
                                    date=date_str, 
                                    total_assets=total_assets, 
                                    fixed_assets=fixed_assets, 
                                    current_assets=current_assets, 
                                    short_term_receivables=short_term_receivables,
                                    cash_and_equivalents=cash_and_equivalents,
                                    inventory=inventory,
                                    short_term_liabilities=short_term_liabilities,
                                    long_term_liabilities=long_term_liabilities,
                                    trade_payables=trade_payables, 
                                    equity=equity,
                                    net_revenues=net_revenues,  
                                    operating_costs=operating_costs))  

        except ET.ParseError as e:
            flash(f"XML parsing error: {e}")
            current_app.logger.error("XML parsing error: %s", e)
            return redirect(url_for('main.upload'))
        except Exception as e:
            flash(f"Wystąpił błąd: {e}")
            current_app.logger.error("An error occurred: %s", e)
            return redirect(url_for('main.upload'))

    else:
        flash("Invalid file format")
        current_app.logger.warning("Invalid file format.")
        return redirect(url_for('main.upload'))

@main.route('/confirm_insert', methods=['POST'])
def confirm_insert():
    print("confirm_insert function called")
    print("Request Method:", request.method) 
    
    date_str = request.form.get('date')
    print(f"Received date: {date_str}")

    if not date_str:
        flash("Date is required.")
        return redirect(url_for('main.preview_data'))

    try:
        total_assets = float(request.form.get('total_assets'))
        fixed_assets = float(request.form.get('fixed_assets'))
        current_assets = float(request.form.get('current_assets'))
        short_term_receivables = float(request.form.get('short_term_receivables'))
        cash_and_equivalents = float(request.form.get('cash_and_equivalents'))
        inventory = float(request.form.get('inventory'))
        short_term_liabilities = float(request.form.get('short_term_liabilities'))
        long_term_liabilities = float(request.form.get('long_term_liabilities'))
        trade_payables = float(request.form.get('trade_payables'))  
        equity = float(request.form.get('equity'))
        net_revenues = float(request.form.get('net_revenues'))  
        operating_costs = float(request.form.get('operating_costs'))  

        print(f"Received data - Date: {date_str}, Total Assets: {total_assets}, Fixed Assets: {fixed_assets}, Current Assets: {current_assets}")

        # Creating a new entry in the database
        try:
            data_entry = DataEntry(
                user_id=session["user_id"],
                date=datetime.strptime(date_str, '%Y-%m-%d'),
                total_assets=total_assets,
                fixed_assets=fixed_assets,
                current_assets=current_assets,
                short_term_receivables=short_term_receivables,
                cash_and_equivalents=cash_and_equivalents,
                inventory=inventory,
                short_term_liabilities=short_term_liabilities,
                long_term_liabilities=long_term_liabilities,
                trade_payables=trade_payables,
                equity=equity,
                net_revenues=net_revenues,
                operating_costs=operating_costs,
                source='insertxml'
            )
            db.session.add(data_entry)
            db.session.commit()
            flash("Dane zostały pomyślnie dodane.")
            return redirect(url_for('main.results'))
        except Exception as e:
            db.session.rollback()
            flash(f"Wystąpił błąd: {e}")
            print(f"Error: {e}")

    except ValueError as e:
        flash(f"Invalid input: {e}")
        return redirect(url_for('main.preview_data'))

@main.route('/preview_data', methods=['GET'])
def preview_data():
    total_assets = request.args.get('total_assets')
    fixed_assets = request.args.get('fixed_assets')
    current_assets = request.args.get('current_assets')
    short_term_receivables = request.args.get('short_term_receivables')
    cash_and_equivalents = request.args.get('cash_and_equivalents')
    inventory = request.args.get('inventory')
    short_term_liabilities = request.args.get('short_term_liabilities')
    long_term_liabilities = request.args.get('long_term_liabilities')
    trade_payables = request.args.get('trade_payables')  
    equity = request.args.get('equity')
    net_revenues = request.args.get('net_revenues')  # Add net_revenues
    operating_costs = request.args.get('operating_costs')  # Add operating_costs

    # Log received data for debugging
    current_app.logger.debug("Preview data received: %s", {
        'total_assets': total_assets,
        'fixed_assets': fixed_assets,
        'current_assets': current_assets,
        'short_term_receivables': short_term_receivables,
        'cash_and_equivalents': cash_and_equivalents,
        'inventory': inventory,
        'short_term_liabilities': short_term_liabilities,
        'long_term_liabilities': long_term_liabilities,
        'trade_payables': trade_payables,
        'equity': equity,
        'net_revenues': net_revenues,  # Log net_revenues
        'operating_costs': operating_costs  # Log operating_costs
    })

    return render_template(
        'preview_data.html',
        total_assets=total_assets,
        fixed_assets=fixed_assets,
        current_assets=current_assets,
        short_term_receivables=short_term_receivables,
        cash_and_equivalents=cash_and_equivalents,
        inventory=inventory,
        short_term_liabilities=short_term_liabilities,
        long_term_liabilities=long_term_liabilities,
        trade_payables=trade_payables,  
        equity=equity,
        net_revenues=net_revenues,  # Pass net_revenues to template
        operating_costs=operating_costs  # Pass operating_costs to template
    )




