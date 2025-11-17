.PHONY: help spec validate-spec docs backend-lint frontend-lint test-backend test-frontend docker-up docker-down

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# OpenAPI Specification targets
spec: ## Generate OpenAPI specification
	cd b2b-doc-management/backend && python generate_openapi.py

validate-spec: spec ## Validate OpenAPI specification
	npx @apidevtools/swagger-cli validate openapi.json

docs: ## Open API documentation in browser (requires running server)
	@echo "Opening API documentation..."
	@echo "Swagger UI: http://localhost:8000/api/docs"
	@echo "ReDoc: http://localhost:8000/api/redoc"
	@which xdg-open > /dev/null && xdg-open http://localhost:8000/api/docs || \
	 which open > /dev/null && open http://localhost:8000/api/docs || \
	 echo "Please open http://localhost:8000/api/docs in your browser"

# Backend targets
backend-install: ## Install backend dependencies
	cd b2b-doc-management/backend && pip install -r requirements.txt

backend-lint: ## Lint backend code
	cd b2b-doc-management/backend && \
		flake8 app --count --select=E9,F63,F7,F82 --show-source --statistics && \
		flake8 app --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

backend-format: ## Format backend code with black
	cd b2b-doc-management/backend && black app

backend-format-check: ## Check backend code formatting
	cd b2b-doc-management/backend && black --check app

test-backend: ## Run backend tests
	cd b2b-doc-management/backend && \
		if [ -d "tests" ]; then \
			pytest tests/ -v --cov=app --cov-report=html; \
		else \
			echo "No tests directory found"; \
		fi

# Frontend targets
frontend-install: ## Install frontend dependencies
	cd b2b-doc-management/frontend/b2c-doc-management && npm install

frontend-lint: ## Lint frontend code
	cd b2b-doc-management/frontend/b2c-doc-management && npm run ng lint

frontend-format: ## Format frontend code with prettier
	cd b2b-doc-management/frontend/b2c-doc-management && \
		npx prettier --write "src/**/*.{ts,html,css,scss}"

frontend-format-check: ## Check frontend code formatting
	cd b2b-doc-management/frontend/b2c-doc-management && \
		npx prettier --check "src/**/*.{ts,html,css,scss}"

frontend-build: ## Build frontend application
	cd b2b-doc-management/frontend/b2c-doc-management && npm run build

test-frontend: ## Run frontend tests
	cd b2b-doc-management/frontend/b2c-doc-management && npm run test -- --watch=false

# Docker targets
docker-up: ## Start all services with Docker Compose
	cd b2b-doc-management && docker-compose up --build

docker-down: ## Stop all Docker services
	cd b2b-doc-management && docker-compose down

docker-logs: ## Show Docker logs
	cd b2b-doc-management && docker-compose logs -f

# CI targets
ci-backend: backend-lint backend-format-check test-backend ## Run backend CI checks

ci-frontend: frontend-lint frontend-format-check test-frontend ## Run frontend CI checks

ci-all: ci-backend ci-frontend validate-spec ## Run all CI checks

# Development targets
dev: ## Start development environment
	@echo "Starting development environment..."
	@echo "This will start the backend and frontend in Docker"
	make docker-up

clean: ## Clean build artifacts and cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name ".DS_Store" -delete 2>/dev/null || true
	rm -rf b2b-doc-management/frontend/b2c-doc-management/dist 2>/dev/null || true
	rm -rf b2b-doc-management/frontend/b2c-doc-management/coverage 2>/dev/null || true
	@echo "Cleaned build artifacts and cache"
