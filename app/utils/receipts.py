import html
import os

from flask import current_app


def create_receipt(payment) -> str:
    receipt_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'receipts')
    os.makedirs(receipt_dir, exist_ok=True)

    filename = f'receipt_{payment.id}.html'
    path = os.path.join(receipt_dir, filename)
    safe = lambda value: html.escape(str(value or ''))

    content = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Payment Receipt #{payment.id}</title>
<style>
body {{ font-family: Arial, sans-serif; color: #1e293b; max-width: 720px;
       margin: 40px auto; padding: 32px; border: 1px solid #cbd5e1; }}
h1 {{ color: #1d4ed8; }} table {{ width: 100%; border-collapse: collapse; }}
td {{ padding: 10px 0; border-bottom: 1px solid #e2e8f0; }}
.amount {{ font-size: 22px; font-weight: bold; }}
</style></head>
<body>
<h1>MediCare Hospital</h1>
<h2>Payment Receipt</h2>
<table>
<tr><td>Receipt number</td><td>MC-{payment.id:06d}</td></tr>
<tr><td>Patient</td><td>{safe(payment.user.name)}</td></tr>
<tr><td>Description</td><td>{safe(payment.description)}</td></tr>
<tr><td>Payment type</td><td>{safe(payment.fee_type.title())}</td></tr>
<tr><td>Razorpay payment ID</td><td>{safe(payment.razorpay_payment_id)}</td></tr>
<tr><td>Paid at</td><td>{safe(payment.paid_at)}</td></tr>
<tr><td class="amount">Amount paid</td>
    <td class="amount">{safe(payment.currency)} {safe(payment.amount)}</td></tr>
</table>
<p>Thank you for choosing MediCare Hospital.</p>
</body></html>"""

    with open(path, 'w', encoding='utf-8') as receipt_file:
        receipt_file.write(content)
    return path
