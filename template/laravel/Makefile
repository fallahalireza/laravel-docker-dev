# ═══════════════════════════════════════════════════════════════
#  Laravel Docker Dev - Makefile
#  Usage: make <command>
# ═══════════════════════════════════════════════════════════════

COMPOSE = docker compose -f docker-compose.yml
PHP_FPM = $(COMPOSE) exec php-fpm
PHP_USER = $(COMPOSE) exec -u $(shell id -u):$(shell id -g) php-fpm

.PHONY: help up down build rebuild start stop restart shell logs \
        artisan composer npm tinker test migrate fresh seed \
        cache-clear config-cache route-cache queue-restart \
        xdebug-on xdebug-off ps health

# ── Default target ────────────────────────────────────────────
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""

# ── Docker Lifecycle ──────────────────────────────────────────
up: ## Start all containers (detached)
	$(COMPOSE) up -d

down: ## Stop and remove containers
	$(COMPOSE) down

build: ## Build images
	$(COMPOSE) build

rebuild: ## Rebuild images without cache
	$(COMPOSE) build --no-cache

start: ## Start stopped containers
	$(COMPOSE) start

stop: ## Stop running containers
	$(COMPOSE) stop

restart: ## Restart all containers
	$(COMPOSE) restart

ps: ## List containers and their status
	$(COMPOSE) ps

health: ## Show container health status
	@docker inspect --format='{{.Name}}: {{.State.Health.Status}}' \
		$(shell $(COMPOSE) ps -q) 2>/dev/null || echo "No health info available"

# ── Logs ──────────────────────────────────────────────────────
logs: ## Tail logs for all containers
	$(COMPOSE) logs -f

logs-nginx: ## Tail Nginx logs
	$(COMPOSE) logs -f nginx

logs-php: ## Tail PHP-FPM logs
	$(COMPOSE) logs -f php-fpm

logs-queue: ## Tail queue worker logs
	$(COMPOSE) logs -f queue-worker

# ── Shells ────────────────────────────────────────────────────
shell: ## Enter PHP-FPM container shell
	$(PHP_FPM) bash

shell-root: ## Enter PHP-FPM container as root
	$(COMPOSE) exec -u root php-fpm bash

shell-nginx: ## Enter Nginx container shell
	$(COMPOSE) exec nginx sh

# ── Laravel Artisan ───────────────────────────────────────────
artisan: ## Run artisan command: make artisan CMD="migrate"
	$(PHP_USER) php artisan $(CMD)

tinker: ## Open Laravel Tinker REPL
	$(PHP_FPM) php artisan tinker

migrate: ## Run database migrations
	$(PHP_USER) php artisan migrate

fresh: ## Drop all tables and re-run migrations
	$(PHP_USER) php artisan migrate:fresh --seed

seed: ## Run database seeders
	$(PHP_USER) php artisan db:seed

cache-clear: ## Clear all Laravel caches
	$(PHP_USER) php artisan optimize:clear

config-cache: ## Cache config, routes, views
	$(PHP_USER) php artisan optimize

route-cache: ## Cache routes only
	$(PHP_USER) php artisan route:cache

queue-restart: ## Restart queue workers
	$(PHP_USER) php artisan queue:restart

# ── Composer ──────────────────────────────────────────────────
composer: ## Run composer command: make composer CMD="require package/name"
	$(PHP_USER) composer $(CMD)

install: ## Install composer dependencies
	$(PHP_USER) composer install

update: ## Update composer dependencies
	$(PHP_USER) composer update

# ── NPM ───────────────────────────────────────────────────────
npm: ## Run npm command: make npm CMD="install"
	$(PHP_USER) npm $(CMD)

npm-install: ## Install npm dependencies
	$(PHP_USER) npm install

npm-dev: ## Run Vite in development mode
	$(PHP_USER) npm run dev

npm-build: ## Build assets for production
	$(PHP_USER) npm run build

# ── Testing ───────────────────────────────────────────────────
test: ## Run PHPUnit tests
	$(PHP_USER) php artisan test

test-coverage: ## Run tests with coverage (requires xdebug coverage mode)
	$(PHP_USER) php artisan test --coverage

# ── Xdebug Toggle ─────────────────────────────────────────────
xdebug-on: ## Enable Xdebug (debug mode)
	@sed -i 's/^XDEBUG_MODE=.*/XDEBUG_MODE=debug,develop/' .env
	$(COMPOSE) restart php-fpm
	@echo "✅ Xdebug enabled (debug,develop)"

xdebug-off: ## Disable Xdebug
	@sed -i 's/^XDEBUG_MODE=.*/XDEBUG_MODE=off/' .env
	$(COMPOSE) restart php-fpm
	@echo "✅ Xdebug disabled"

# ── Initial Setup ─────────────────────────────────────────────
setup: ## First-time project setup
	@echo "📦 Setting up Laravel project..."
	@[ -f src/.env ] || cp src/.env.example src/.env && echo "  ✅ .env created"
	$(PHP_USER) composer install
	$(PHP_USER) php artisan key:generate
	$(PHP_USER) php artisan migrate
	$(PHP_USER) php artisan storage:link
	@echo "🎉 Setup complete! Visit https://$(shell grep DOMAIN_DEV .env | cut -d= -f2)"
