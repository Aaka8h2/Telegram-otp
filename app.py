# app.py
from flask import Flask, render_template, request, jsonify
import requests
import random
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = '70a7f8ea1e4dd4e00b9a6196854b0750e7b32f5b631dc9ed51ea8e2c3f846105'

# Temporary storage for OTP codes (use database in production)
otp_storage = {}

TELEGRAM_BOT_TOKEN = '7158237482:AAEL0v_4VXVJBxhLaOqUhZXwNrpUKRc-wPI'

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/send_otp', methods=['POST'])
def send_otp():
    telegram_id = request.form['telegram_id']
    
    if not telegram_id.startswith('@'):
        return jsonify({'error': 'Invalid Telegram ID format'}), 400
    
    # Generate 4-digit OTP
    otp = str(random.randint(1000, 9999))
    expiration = datetime.now() + timedelta(minutes=2)
    
    # Store OTP
    otp_storage[telegram_id] = {
        'otp': otp,
        'expires': expiration.timestamp()
    }
    
    # Send via Telegram Bot
    try:
        response = requests.post(
            f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage',
            json={
                'chat_id': telegram_id,
                'text': f'Your OTP code is: {otp}\nExpires in 2 minutes'
            }
        )
        response.raise_for_status()
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    telegram_id = data['telegram_id']
    user_otp = data['otp']
    
    stored_data = otp_storage.get(telegram_id)
    
    if not stored_data:
        return jsonify({'error': 'OTP not found or expired'}), 400
    
    if datetime.now().timestamp() > stored_data['expires']:
        del otp_storage[telegram_id]
        return jsonify({'error': 'OTP expired'}), 400
    
    if user_otp == stored_data['otp']:
        del otp_storage[telegram_id]
        return jsonify({'success': True})
    
    return jsonify({'error': 'Invalid OTP'}), 400

if __name__ == '__main__':
    app.run(debug=True)
