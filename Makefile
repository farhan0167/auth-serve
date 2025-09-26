.PHONY: db-start, db-stop, generate-secret, server, lint, lint-fix, format

# Start and stop the databases
db-start:
	docker compose up -d
db-stop:
	docker compose down

# Create a secret key
generate-secret:
	cd auth-serve && [ -f secret.txt ] || openssl rand -hex 32 > secret.txt

# Start database and server
server: db-start generate-secret
	cd auth-serve && uv run uvicorn main:app --reload

# Linting
lint:
	cd auth-serve && uv run ruff check .

lint-fix:
	cd auth-serve && uv run ruff check . --fix

# Formatting
format:
	cd auth-serve && uv run ruff format .
