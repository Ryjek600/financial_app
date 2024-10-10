from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

class DataEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Dodane pole
    date = db.Column(db.Date, nullable=False)
    total_assets = db.Column(db.Float, nullable=False)
    fixed_assets = db.Column(db.Float, nullable=False)
    current_assets = db.Column(db.Float, nullable=False)
    short_term_receivables = db.Column(db.Float, nullable=False)
    cash_and_equivalents = db.Column(db.Float, nullable=False)
    inventory = db.Column(db.Float, nullable=False)
    short_term_liabilities = db.Column(db.Float, nullable=False)
    long_term_liabilities = db.Column(db.Float, nullable=False)
    trade_payables = db.Column(db.Float, nullable=False)
    equity = db.Column(db.Float, nullable=False)
    net_revenues = db.Column(db.Float, nullable=False)  # Dodane pole
    operating_costs = db.Column(db.Float, nullable=False)  # Dodane pole
    submit_date = db.Column(db.DateTime, default=datetime.utcnow)  # Dodana kolumna
    source = db.Column(db.String(20), nullable=False)  # Dodane pole

    def __repr__(self):
        return f'<DataEntry {self.date}>'

    # Property methods for calculations
    @property
    def osn(self):
        return (self.short_term_receivables / self.net_revenues * 365) if self.net_revenues != 0 else None

    @property
    def ouz(self):
        return (self.inventory / self.operating_costs * 365) if self.operating_costs != 0 else None

    @property
    def orz(self):
        return (self.short_term_liabilities / self.operating_costs * 365) if self.operating_costs != 0 else None

    @property
    def co(self):
        osn = self.osn
        ouz = self.ouz
        return osn + ouz if osn is not None and ouz is not None else None

    @property
    def ckg(self):
        co = self.co
        orz = self.orz
        return co - orz if co is not None and orz is not None else None







