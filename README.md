# 🚀 Laravel Docker Dev

محیط توسعه مدرن، سریع و قابل استفاده مجدد برای پروژه‌های Laravel با Docker.

---

## ✨ ویژگی‌ها

| ویژگی | توضیح |
|-------|-------|
| **Traefik Reverse Proxy** | مسیریابی خودکار برای دامنه‌های محلی با HTTPS |
| **Interactive CLI** | منوی تعاملی برای مدیریت سرویس‌ها |
| **Auto-Provisioning** | ساخت سایت جدید لاراول از روی template |
| **Health Checks** | بررسی سلامت همه سرویس‌ها (MySQL، Traefik، PHP-FPM) |
| **Xdebug Toggle** | فعال/غیرفعال کردن Xdebug با یک دستور |
| **Queue Worker** | Worker صف با تنظیمات قابل تغییر از `.env` |
| **Mailpit** | تست ایمیل محلی بدون ارسال واقعی |
| **Colorized Output** | لاگ‌های رنگی و خوانا در ترمینال |

---

## 📋 پیش‌نیازها

- **Docker Desktop** (v24+)
- **Python 3.10+**

---

## 🛠 نصب و راه‌اندازی

```bash
git clone https://github.com/fallahalireza/laravel-docker-dev.git
cd laravel-docker-dev
```

### ۱. راه‌اندازی زیرساخت (Traefik + MySQL)

```bash
python dev.py up
```

### ۲. ساخت یک پروژه جدید

```bash
python dev.py create myapp.localhost
```

### ۳. اجرای سایت

```bash
cd sites/myapp_localhost
cp .env.example .env     # در صورت نیاز
make setup               # نصب اولیه (composer, migrate, key)
make up                  # اجرای کانتینرها
```

سایت روی `https://myapp.localhost` در دسترس خواهد بود.

---

## 📟 دستورات CLI

```bash
python dev.py                    # منوی تعاملی
python dev.py up                 # راه‌اندازی همه سرویس‌های زیرساخت
python dev.py up traefik         # راه‌اندازی فقط Traefik
python dev.py down               # توقف همه سرویس‌ها
python dev.py restart mysql      # ری‌استارت MySQL
python dev.py create myapp.ir    # ساخت سایت جدید
python dev.py list               # لیست سایت‌های موجود
```

---

## 🧰 دستورات Makefile (داخل پوشه سایت)

```bash
make help          # نمایش همه دستورات
make up            # اجرای کانتینرها
make down          # توقف کانتینرها
make shell         # ورود به shell کانتینر PHP
make artisan CMD="migrate"
make composer CMD="require spatie/laravel-permission"
make npm CMD="run dev"
make xdebug-on     # فعال کردن Xdebug
make xdebug-off    # غیرفعال کردن Xdebug
make setup         # راه‌اندازی اولیه پروژه
make test          # اجرای تست‌ها
```

---

## 📁 ساختار پروژه

```
laravel-docker-dev/
├── development/
│   ├── traefik/          # Traefik reverse proxy
│   └── mysql/            # MySQL سراسری
├── scripts/
│   ├── dev.py            # CLI entry point
│   └── manager.py        # منطق اصلی مدیریت
├── template/
│   └── laravel/          # قالب آماده برای سایت‌های جدید
├── sites/                # سایت‌های ساخته‌شده (auto-generated)
└── dev.py                # نقطه ورود اصلی
```

---

## ⚙️ متغیرهای محیطی مهم (.env سایت)

| متغیر | پیش‌فرض | توضیح |
|-------|---------|-------|
| `PHP_VERSION` | `8.4` | نسخه PHP |
| `XDEBUG_MODE` | `off` | حالت Xdebug |
| `REDIS_PASSWORD` | `secret_redis_password` | رمز Redis |
| `QUEUE_TRIES` | `3` | تعداد تلاش مجدد صف |
| `QUEUE_TIMEOUT` | `90` | timeout صف (ثانیه) |

---

## 📄 License

MIT © [Alireza Fallah](https://github.com/fallahalireza)
