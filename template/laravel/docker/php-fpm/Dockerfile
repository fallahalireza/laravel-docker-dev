ARG PHP_VERSION=8.4
FROM php:${PHP_VERSION}-fpm-alpine AS base

# ── Build Arguments ───────────────────────────────────────────────
ARG UID=1000
ARG GID=1000
ARG PHP_MEMORY_LIMIT=512M
ARG PHP_POST_MAX_SIZE=128M
ARG PHP_MAX_EXECUTION_TIME=300
ARG PHP_UPLOAD_MAX_FILESIZE=100M
ARG PHP_MAX_INPUT_TIME=300
ARG PHP_MAX_INPUT_VARS=3000
ARG XDEBUG_HOST=host.docker.internal
ARG XDEBUG_IDE_KEY=DOCKER
ARG XDEBUG_PORT=9003

# ── Install System Dependencies ───────────────────────────────────
RUN apk add --no-cache \
    bash \
    curl \
    git \
    zip \
    unzip \
    libzip-dev \
    libpng-dev \
    libjpeg-turbo-dev \
    libwebp-dev \
    freetype-dev \
    icu-dev \
    oniguruma-dev \
    linux-headers \
    fcgi \
    nodejs \
    npm \
    && rm -rf /var/cache/apk/*

# ── Install PHP Extensions ────────────────────────────────────────
RUN docker-php-ext-configure gd \
        --with-freetype \
        --with-jpeg \
        --with-webp \
    && docker-php-ext-install -j$(nproc) \
        pdo_mysql \
        mbstring \
        exif \
        pcntl \
        bcmath \
        gd \
        zip \
        intl \
        opcache

# ── Install Redis + Xdebug در یک مرحله (کاهش لایه‌های image) ────
RUN apk add --no-cache --virtual .phpize-deps $PHPIZE_DEPS \
    && pecl install redis xdebug \
    && docker-php-ext-enable redis xdebug \
    && apk del .phpize-deps \
    && rm -rf /tmp/pear

# ── Configure PHP ─────────────────────────────────────────────────
RUN { \
    echo "memory_limit=${PHP_MEMORY_LIMIT}"; \
    echo "post_max_size=${PHP_POST_MAX_SIZE}"; \
    echo "max_execution_time=${PHP_MAX_EXECUTION_TIME}"; \
    echo "upload_max_filesize=${PHP_UPLOAD_MAX_FILESIZE}"; \
    echo "max_input_time=${PHP_MAX_INPUT_TIME}"; \
    echo "max_input_vars=${PHP_MAX_INPUT_VARS}"; \
    echo "date.timezone=Asia/Tehran"; \
    echo "expose_php=Off"; \
    echo "error_reporting=E_ALL"; \
    echo "display_errors=On"; \
    echo "log_errors=On"; \
    echo "error_log=/var/log/php/error.log"; \
    echo "realpath_cache_size=4096K"; \
    echo "realpath_cache_ttl=600"; \
} > /usr/local/etc/php/conf.d/99-custom.ini

# ── Configure OPcache (dev-friendly) ─────────────────────────────
RUN { \
    echo "opcache.enable=1"; \
    echo "opcache.enable_cli=1"; \
    echo "opcache.memory_consumption=128"; \
    echo "opcache.interned_strings_buffer=8"; \
    echo "opcache.max_accelerated_files=10000"; \
    echo "opcache.validate_timestamps=1"; \
    echo "opcache.revalidate_freq=0"; \
    echo "opcache.fast_shutdown=1"; \
} > /usr/local/etc/php/conf.d/opcache.ini

# ── Configure Xdebug ─────────────────────────────────────────────
RUN { \
    echo "xdebug.mode=\${XDEBUG_MODE}"; \
    echo "xdebug.client_host=${XDEBUG_HOST}"; \
    echo "xdebug.client_port=${XDEBUG_PORT}"; \
    echo "xdebug.idekey=${XDEBUG_IDE_KEY}"; \
    echo "xdebug.start_with_request=yes"; \
    echo "xdebug.discover_client_host=0"; \
    echo "xdebug.log_level=0"; \
    echo "xdebug.max_nesting_level=512"; \
} > /usr/local/etc/php/conf.d/xdebug.ini

# ── Configure PHP-FPM ─────────────────────────────────────────────
RUN { \
    echo "[global]"; \
    echo "error_log=/var/log/php/fpm-error.log"; \
    echo "[www]"; \
    echo "listen=0.0.0.0:9000"; \
    echo "clear_env=no"; \
    echo "catch_workers_output=yes"; \
    echo "php_flag[display_errors]=on"; \
    echo "ping.path=/ping"; \
    echo "ping.response=pong"; \
    echo "pm=dynamic"; \
    echo "pm.max_children=20"; \
    echo "pm.start_servers=4"; \
    echo "pm.min_spare_servers=2"; \
    echo "pm.max_spare_servers=6"; \
    echo "pm.process_idle_timeout=10s"; \
    echo "pm.max_requests=500"; \
} > /usr/local/etc/php-fpm.d/www.conf

# ── Install php-fpm-healthcheck ───────────────────────────────────
RUN curl -fsSL -o /usr/local/bin/php-fpm-healthcheck \
    https://raw.githubusercontent.com/renatomefi/php-fpm-healthcheck/master/php-fpm-healthcheck \
    && chmod +x /usr/local/bin/php-fpm-healthcheck

# ── Install Composer ─────────────────────────────────────────────
COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

# ── Create Application User ───────────────────────────────────────
RUN addgroup -g ${GID} -S appgroup 2>/dev/null || true \
    && adduser -u ${UID} -S appuser -G appgroup 2>/dev/null || true

# ── Create Necessary Directories ─────────────────────────────────
RUN mkdir -p /var/www /var/log/php \
    && chown -R appuser:appgroup /var/www /var/log/php

WORKDIR /var/www

USER appuser

EXPOSE 9000
