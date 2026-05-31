# 🚀 Laravel Docker Dev

یک محیط توسعه مدرن، سریع و قابل استفاده مجدد برای پروژه‌های Laravel با Docker.

> A modern, fast and reusable development environment for Laravel projects using Docker.

---

## 📦 سرویس‌ها / Services

| سرویس | تصویر | توضیح |
|-------|-------|--------|
| **nginx** | `nginx:1.27-alpine` | وب‌سرور با gzip و security headers |
| **php-fpm** | `php:8.4-fpm-alpine` | PHP با Xdebug، Redis، OPcache |
| **redis** | `redis:7-alpine` | کش و صف با رمز عبور |
| **queue-worker** | (built) | پردازش صف Laravel |
| **scheduler** | (built) | زمان‌بند وظایف Laravel |
| **mailpit** | `axllent/mailpit` | تست ایمیل محلی |

---

## 🛠️ پیش‌نیازها / Requirements

- Docker Engine 24+
- Docker Compose v2+
- `make` (اختیاری ولی توصیه می‌شود)
- Traefik در حال اجرا با شبکه `traefik-network`
- یک شبکه خارجی `mysql-network` برای دسترسی به دیتابیس

---

## ⚡ شروع سریع / Quick Start

```bash
# ۱. کپی فایل تنظیمات
cp .env.example .env

# ۲. ویرایش تنظیمات (نام کانتینر، دامنه، PHP version و ...)
nano .env

# ۳. ساخت و راه‌اندازی
make build
make up

# ۴. راه‌اندازی اولیه پروژه
make setup
```

---

## 📂 ساختار پروژه / Project Structure

```
laravel-docker-dev/
├── docker/
│   ├── nginx/
│   │   └── nginx.conf.template    # تنظیمات Nginx (با متغیرها)
│   ├── php-fpm/
│   │   └── Dockerfile             # PHP-FPM با همه اکستنشن‌ها
│   └── redis/
│       └── redis.conf             # تنظیمات Redis
├── src/                           # کد لاراول شما اینجا قرار می‌گیرد
├── .env.example                   # نمونه متغیرهای محیطی
├── compose.dev.yaml               # Docker Compose برای توسعه
├── Makefile                       # دستورات سریع
└── README.md
```

---

## 🔧 دستورات Makefile

```bash
make help           # نمایش همه دستورات

# ── مدیریت Docker ──────────────────────────
make up             # راه‌اندازی تمام کانتینرها
make down           # خاموش کردن کانتینرها
make build          # ساخت ایمیج‌ها
make rebuild        # ساخت مجدد بدون cache
make restart        # ریستارت همه کانتینرها
make ps             # وضعیت کانتینرها
make health         # وضعیت سلامت کانتینرها

# ── Shell ───────────────────────────────────
make shell          # ورود به shell کانتینر PHP
make shell-root     # ورود به shell به عنوان root
make shell-nginx    # ورود به shell Nginx

# ── لاگ‌ها ─────────────────────────────────
make logs           # لاگ همه کانتینرها
make logs-nginx     # لاگ Nginx
make logs-php       # لاگ PHP-FPM
make logs-queue     # لاگ Queue Worker

# ── Laravel ────────────────────────────────
make artisan CMD="migrate"       # اجرای artisan
make migrate                     # اجرای migration
make fresh                       # migrate:fresh --seed
make seed                        # اجرای seeders
make tinker                      # Laravel Tinker
make cache-clear                 # پاک کردن همه cache‌ها
make config-cache                # cache کردن config/route/view
make queue-restart               # ریستارت queue workers

# ── Composer ───────────────────────────────
make install                     # composer install
make composer CMD="require x/y"  # اجرای composer

# ── NPM / Vite ─────────────────────────────
make npm-install                 # نصب پکیج‌های npm
make npm-dev                     # اجرای Vite در حالت dev
make npm-build                   # build assets

# ── تست ────────────────────────────────────
make test                        # اجرای تست‌ها
make test-coverage               # تست با coverage

# ── Xdebug ─────────────────────────────────
make xdebug-on                   # فعال‌سازی Xdebug
make xdebug-off                  # غیرفعال‌سازی Xdebug
```

---

## 🐛 Xdebug

برای فعال‌سازی Xdebug:

```bash
# روش اول: از طریق Makefile
make xdebug-on

# روش دوم: دستی در .env
XDEBUG_MODE=debug,develop
# سپس:
make restart
```

### تنظیمات VS Code (`launch.json`):
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Listen for Xdebug",
      "type": "php",
      "request": "launch",
      "port": 9003,
      "pathMappings": {
        "/var/www": "${workspaceFolder}/src"
      }
    }
  ]
}
```

### تنظیمات PhpStorm:
- **Debug port:** 9003
- **Path mapping:** `/var/www` → `./src`
- **IDE Key:** `DOCKER`

---

## 📧 Mailpit (تست ایمیل)

Mailpit برای تست ایمیل در محیط توسعه است. تنظیمات در `src/.env` لاراول:

```dotenv
MAIL_MAILER=smtp
MAIL_HOST=mailpit
MAIL_PORT=1025
MAIL_FROM_ADDRESS=noreply@localhost
```

رابط وب Mailpit: `http://localhost:8025`

---

## 🔒 متغیرهای محیطی مهم / Key ENV Variables

| متغیر | پیش‌فرض | توضیح |
|-------|---------|--------|
| `CONTAINER_NAME` | `my_laravel_app` | پیشوند نام کانتینرها |
| `DOMAIN_DEV` | `my-app.localhost` | دامنه Traefik |
| `PHP_VERSION` | `8.4` | نسخه PHP |
| `XDEBUG_MODE` | `off` | حالت Xdebug |
| `REDIS_PASSWORD` | `secret_redis_password` | رمز Redis |
| `UID` / `GID` | `1000` | شناسه کاربری هاست |

---

## 💡 نکات مفید / Tips

**مشکل permission در فایل‌ها:**
```bash
# UID و GID را با مقدار هاست تنظیم کنید
UID=$(id -u) GID=$(id -g) make up
```

**پاک کردن کامل و شروع مجدد:**
```bash
make down
docker volume rm $(docker volume ls -q | grep CONTAINER_NAME)
make rebuild
make up
```

**بررسی سلامت سرویس‌ها:**
```bash
make health
make ps
```

---

## 📄 License

MIT © [Alireza Fallah](https://github.com/fallahalireza)
