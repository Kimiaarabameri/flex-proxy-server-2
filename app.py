from flask import Flask, jsonify, request
import random
import string
import os
import time
import hashlib

app = Flask(__name__)

# لیست User-Agent های مختلف برای استفاده تصادفی - متفاوت از سرور اول
USER_AGENTS = [
    "Amazon/34567 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.128 Mobile Safari/537.36",
    "Amazon/34568 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.5304.105 Mobile Safari/537.36",
    "Amazon/34569 (iPhone; CPU iPhone OS 16_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Amazon/34570 (iPad; CPU OS 16_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
]

# تابع کمکی برای تولید امضاهای تصادفی با روش متفاوت
def generate_signature_data(marketplace_id):
    # تولید یک امضا با استفاده از هش مارکت آیدی
    timestamp = int(time.time() * 1000)
    random_suffix = random.randint(10000, 99999)
    sig_input = f"@method;@path;@authority;x-amzn-marketplace-id;x-amzn-requestid;x-flex-instance-id;sig={timestamp}={random_suffix}"
    
    # ایجاد امضای متفاوت با استفاده از الگوریتم هش
    sig_base = f"{marketplace_id}:{timestamp}:{random_suffix}"
    sig_hash = hashlib.sha256(sig_base.encode()).hexdigest()
    sig = sig_hash + "".join(random.choices(string.ascii_letters + string.digits + "/+=", k=60))
    
    return {
        "signature_input": sig_input,
        "signature": sig,
        "user_agent": random.choice(USER_AGENTS)
    }

@app.route('/')
def home():
    return jsonify({
        "status": "Server 2 is running",
        "message": "Use /accept/<api_key>/<marketplace_id> or /challenge/<api_key>/<marketplace_id> endpoints"
    })

@app.route('/accept/<api_key>/<marketplace_id>')
def accept_offer(api_key, marketplace_id):
    # بررسی API کلید
    if api_key != os.environ.get('API_KEY', 'default-api-key-server2'):
        return jsonify({"error": "Invalid API key"}), 403
    
    # تولید داده‌های امضا
    signature_data = generate_signature_data(marketplace_id)
    
    # لاگ کردن درخواست
    print(f"[Server 2] Accept request for marketplace_id: {marketplace_id}")
    
    return jsonify(signature_data)

@app.route('/challenge/<api_key>/<marketplace_id>')
def validate_challenge(api_key, marketplace_id):
    # بررسی API کلید
    if api_key != os.environ.get('API_KEY', 'default-api-key-server2'):
        return jsonify({"error": "Invalid API key"}), 403
    
    # تولید داده‌های امضا
    signature_data = generate_signature_data(marketplace_id)
    
    # لاگ کردن درخواست
    print(f"[Server 2] Challenge request for marketplace_id: {marketplace_id}")
    
    return jsonify(signature_data)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port) 