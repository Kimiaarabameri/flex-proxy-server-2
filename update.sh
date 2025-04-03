#!/bin/bash

# ایجاد مخزن Git اگر وجود ندارد
if [ ! -d ".git" ]; then
  git init
  git remote add origin https://github.com/Kimiaarabameri/flex-proxy-server-2.git
fi

# اضافه کردن فایل‌ها
git add requirements.txt pyproject.toml app.py Procfile

# کامیت کردن تغییرات
git commit -m "Update dependencies and configuration"

# ارسال به GitHub
git push -u origin main 