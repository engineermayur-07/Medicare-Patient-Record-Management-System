import re
from datetime import datetime
from decimal import Decimal, InvalidOperation


MAX_MEDICAL_FEE = Decimal('500000')


def validate_password_strength(password):
    """Return an error message for weak passwords, or None when valid."""
    if len(password) < 8:
        return 'Password must be at least 8 characters.'
    if not re.search(r'[A-Z]', password):
        return 'Password must contain at least one uppercase letter.'
    if not re.search(r'[a-z]', password):
        return 'Password must contain at least one lowercase letter.'
    if not re.search(r'\d', password):
        return 'Password must contain at least one number.'
    if not re.search(r'[^A-Za-z0-9]', password):
        return 'Password must contain at least one special character.'
    return None


def parse_medical_fee(raw_amount):
    """Parse and validate a medical fee before it reaches the database."""
    try:
        amount = Decimal(raw_amount)
    except (InvalidOperation, TypeError):
        return None, 'Enter a valid amount.'

    if not amount.is_finite():
        return None, 'Enter a valid amount.'
    if amount <= 0:
        return None, 'Amount must be greater than zero.'
    if amount >= MAX_MEDICAL_FEE:
        return None, 'Amount must be below ₹500,000.'
    if amount.as_tuple().exponent < -2:
        return None, 'Amount can have at most two decimal places.'

    return amount.quantize(Decimal('0.01')), None


def validate_payment_details(method, details):
    """Validate checkout details without persisting sensitive payment data."""
    details = details if isinstance(details, dict) else {}

    if method == 'card':
        card_number = re.sub(r'\s+', '', str(details.get('card_number', '')))
        expiry = str(details.get('expiry', '')).strip()
        cvv = str(details.get('cvv', '')).strip()
        if not re.fullmatch(r'\d{12,19}', card_number):
            return 'Enter a valid card number.'
        if not re.fullmatch(r'(0[1-9]|1[0-2])/\d{2}', expiry):
            return 'Enter a valid expiry date in MM/YY format.'
        month, year = expiry.split('/')
        expiry_date = datetime(2000 + int(year), int(month), 1)
        current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if expiry_date < current_month:
            return 'The card expiry date has passed.'
        if not re.fullmatch(r'\d{3,4}', cvv):
            return 'Enter a valid CVV.'
    elif method == 'upi':
        upi_id = str(details.get('upi_id', '')).strip()
        if not re.fullmatch(r'[A-Za-z0-9._-]{2,}@[A-Za-z0-9.-]{2,}', upi_id):
            return 'Enter a valid UPI ID.'
    elif method == 'qr':
        if details.get('confirmed') is not True:
            return 'Confirm that you completed the QR payment.'
    elif method == 'netbanking':
        if not str(details.get('bank', '')).strip():
            return 'Select your bank.'
    else:
        return 'Select a valid payment method.'

    return None
