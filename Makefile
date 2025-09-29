.PHONY: db-start, db-stop, generate-secret, setup, server, lint, lint-fix, format, keys-init

# Start and stop the databases
db-start:
	docker compose up -d
db-stop:
	docker compose down

keys-init:
	@if [ ! -d "auth-serve/.keys" ]; then \
		echo "Creating auth-serve/.keys directory structure..."; \
		mkdir -p auth-serve/.keys/private auth-serve/.keys/public; \
		touch auth-serve/.keys/current_kid.txt; \
	fi; \
	# Check if there is any private key with a matching public key
	if [ -z "$$(ls -1 auth-serve/.keys/private/*.pem 2>/dev/null)" ] || [ -z "$$(ls -1 auth-serve/.keys/public/*.pem 2>/dev/null)" ]; then \
		echo "No keypair found, generating a new one..."; \
		KID=$$(uuidgen | tr '[:upper:]' '[:lower:]' | tr -d '-') ; \
		openssl genrsa -out auth-serve/.keys/private/$$KID.pem 2048; \
		openssl rsa -in auth-serve/.keys/private/$$KID.pem -pubout -out auth-serve/.keys/public/$$KID.pem; \
		echo $$KID > auth-serve/.keys/current_kid.txt; \
	else \
		echo "Keypair already exists"; \
	fi

# Install dependencies using uv
setup:
	cd auth-serve && uv sync

# Start database and server
server: db-start keys-init setup
	cd auth-serve && uv run uvicorn main:app --reload

# Linting
lint:
	cd auth-serve && uv run ruff check .

lint-fix:
	cd auth-serve && uv run ruff check . --fix

# Formatting
format:
	cd auth-serve && uv run ruff format .
