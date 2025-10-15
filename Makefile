.PHONY: help dev-frontend dev-backend dev prod

help:
	@echo "Available commands:"
	@echo "  make dev-frontend    - Starts the frontend development server (Vite)"
	@echo "  make dev-backend     - Starts the backend development server (Uvicorn with reload)"
	@echo "  make dev             - Starts both frontend and backend development servers"

dev-frontend:
	@echo "Starting frontend development server..."
	@cd frontend && npm run dev
# 	@cd frontend && http-server dist

dev-backend:
	@echo "Starting backend development server..."
	@cd backend && uvx --refresh --from "langgraph-cli[inmem]" --with-editable . --python 3.11 langgraph dev --allow-blocking

prod-frontend:
	@echo "Building frontend for production..."
	@cd frontend && npm install && npm run build


# Run frontend and backend concurrently
dev:
	@echo "Starting both frontend and backend development servers..."
	@make dev-frontend & make dev-backend 

prod:
	@echo "Building frontend for production..."
	@make prod-frontend
# for now the backend is the same in prod and dev
	@cd backend && uvx --from "langgraph-cli[inmem]" --with-editable . --python 3.11 langgraph dev --allow-blocking