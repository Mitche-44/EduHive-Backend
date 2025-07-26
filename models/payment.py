from extensions import db
from datetime import datetime

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    checkout_request_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    merchant_request_id = db.Column(db.String(100), nullable=True, index=True)
    phone_number = db.Column(db.String(15), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    account_reference = db.Column(db.String(100), nullable=True)
    transaction_desc = db.Column(db.String(200), nullable=True)
    
    # M-Pesa response fields
    mpesa_receipt_number = db.Column(db.String(50), nullable=True)
    transaction_date = db.Column(db.DateTime, nullable=True)
    
    # Status tracking - Updated statuses
    status = db.Column(db.String(20), default='pending')  
    # Possible statuses: pending, sent_to_phone, completed, failed, cancelled, timeout
    
    result_code = db.Column(db.Integer, nullable=True)
    result_desc = db.Column(db.String(200), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Payment {self.checkout_request_id}: {self.status}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'checkout_request_id': self.checkout_request_id,
            'merchant_request_id': self.merchant_request_id,
            'phone_number': self.phone_number,
            'amount': self.amount,
            'account_reference': self.account_reference,
            'transaction_desc': self.transaction_desc,
            'mpesa_receipt_number': self.mpesa_receipt_number,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'status': self.status,
            'result_code': self.result_code,
            'result_desc': self.result_desc,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }