from flask import Flask, jsonify, request
import random
import string
import os
import time
import uuid
import hashlib
import json

app = Flask(__name__)

# User-Agent list for iOS 16
ios_user_agents = [
    # iOS User-Agents - updated for version 3.104.1.0
    "Amazon/3.104.1.0 (iPhone; CPU iPhone OS 16_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/20G81",
    "Amazon/3.104.1.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/20G75",
    "Amazon/3.104.1.0 (iPhone; CPU iPhone OS 16_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/20F75",
    "Amazon/3.104.1.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/20F66",
    "Amazon/3.104.1.0 (iPhone; CPU iPhone OS 16_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/20E252",
]

# User-Agent list for Android - updated for version 2.512.0.0
android_user_agents = [
    "Amazon/2.512.0.0 (Linux; Android 13; SM-S918B Build/TP1A.220624.014) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/114.0.5735.196 Mobile Safari/537.36",
    "Amazon/2.512.0.0 (Linux; Android 13; SM-G998U Build/TP1A.220624.014) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/114.0.5735.196 Mobile Safari/537.36",
    "Amazon/2.512.0.0 (Linux; Android 13; Pixel 7 Build/TQ2A.230505.002) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/114.0.5735.196 Mobile Safari/537.36",
    "Amazon/2.512.0.0 (Linux; Android 12; SM-S906N Build/SP1A.210812.016) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/114.0.5735.196 Mobile Safari/537.36",
    "Amazon/2.512.0.0 (Linux; Android 12; Pixel 6 Build/SD1A.210817.023) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/114.0.5735.196 Mobile Safari/537.36",
]

# تابع کمکی برای تولید امضاهای قوی با هش
def generate_signature_data(marketplace_id=None, request_id=None, method=None, path=None, authority=None):
    # ایجاد یک کلید منحصر به فرد برای امضا
    timestamp = int(time.time() * 1000)
    unique_id = str(uuid.uuid4())[:8]
    random_num = random.randint(10000, 99999)
    
    # اگر marketplace_id ارسال شده باشد از آن استفاده می‌کنیم
    seed = f"{marketplace_id or unique_id}:{timestamp}:{random_num}"
    
    # ساخت امضای ورودی با فرمت پیشرفته
    path_component = f";@path" if path else ""
    authority_component = f";@authority" if authority else ""
    method_component = f";@method" if method else ""
    
    sig_input = f"{method_component}{path_component}{authority_component};x-amzn-marketplace-id;x-amzn-requestid;x-flex-instance-id;sig={timestamp}={random_num}"
    
    # ساخت امضا با استفاده از الگوریتم هش
    hash_base = hashlib.sha256(seed.encode()).hexdigest()
    
    # ترکیب بخش‌های مختلف برای ساخت امضای قوی
    sig_parts = [
        hash_base[:40],  # بخش اول هش
        ''.join(random.choices(string.ascii_letters + string.digits, k=30)),  # بخش تصادفی
        '/+=',  # کاراکترهای خاص
        ''.join(random.choices(string.ascii_letters + string.digits, k=30)),  # بخش تصادفی دیگر
        hash_base[40:]  # بخش دوم هش
    ]
    
    # ترکیب بخش‌ها با هم
    sig = "".join(sig_parts)
    
    # انتخاب User-Agent براساس پلتفرم
    # بررسی تنظیمات پلتفرم از فایل
    use_ios = False
    userdata_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core", "AMAZON_FLEX_BOT-main", "userdata", "use_ios")
    if os.path.exists(userdata_path):
        with open(userdata_path, "r") as f:
            use_ios = f.read().strip().lower() == "true"
    
    selected_user_agent = random.choice(ios_user_agents if use_ios else android_user_agents)
    
    return {
        "signature_input": sig_input,
        "signature": sig,
        "user_agent": selected_user_agent
    }

@app.route('/')
def home():
    return jsonify({
        "status": "Signature Proxy Server is running",
        "message": "Use /signature/<api_key>/<marketplace_id> endpoint for generating signatures"
    })

@app.route('/signature/<api_key>/<marketplace_id>', methods=['GET', 'POST'])
def generate_signature(api_key, marketplace_id):
    # بررسی API کلید
    if api_key != os.environ.get('API_KEY', 'default-api-key'):
        return jsonify({"error": "Invalid API key"}), 403
    
    # دریافت پارامترهای اضافی از درخواست
    request_id = request.args.get('request_id')
    method = request.args.get('method')
    path = request.args.get('path')
    authority = request.args.get('authority')
    
    # تولید داده‌های امضا
    signature_data = generate_signature_data(
        marketplace_id=marketplace_id,
        request_id=request_id,
        method=method,
        path=path,
        authority=authority
    )
    
    # لاگ کردن درخواست
    print(f"Signature request for marketplace_id: {marketplace_id}")
    
    return jsonify(signature_data)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port) 