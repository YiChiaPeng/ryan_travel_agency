# Copilot Instructions for B2B Document Upload and Review Management System

## Overview
This repository contains a B2B document upload and review management system. The project is divided into two main components:

1. **Frontend**: Built with Angular, providing user interfaces for B2B clients and admins.
2. **Backend**: Developed using Flask, handling authentication, file uploads, notifications, and database interactions.

The system uses MariaDB for data storage and Docker for containerized deployment.

---

## Architecture

### Backend
- **Entry Point**: `backend/app/main.py` initializes the Flask application.
- **Services**: Located in `backend/app/services/`, these modules encapsulate business logic:
  - `auth.py`: Handles user authentication.
  - `file_upload.py`: Manages file upload and validation.
  - `notification.py`: Sends notifications to users.
- **Utilities**: Found in `backend/app/utils/`, these modules provide helper functions:
  - `db.py`: Database connection and query utilities.
  - `smtp.py`: Email sending functionality.
- **Database**: Schema and initial data are defined in `db/init.sql`.

### Frontend
- **Angular Configuration**: Defined in `frontend/angular.json`.
- **Components and Services**: Located in `frontend/src/app/`.
- **Dependencies**: Managed via `frontend/package.json`.

---

## Developer Workflows

### Building and Running the Application
1. Ensure Docker and Docker Compose are installed.
2. Build and start the application:
   ```bash
   docker-compose up --build
   ```
3. Access the application:
   - Frontend: `http://localhost:4200`
   - Backend API: `http://localhost:5000`

### Database Initialization
- The database schema is automatically initialized using `db/init.sql` when the database container starts.

### Adding Dependencies
- **Backend**: Add Python packages to `backend/requirements.txt`.
- **Frontend**: Add npm packages to `frontend/package.json`.

### Debugging
- **Backend**: Use Flask's debug mode by setting `FLASK_ENV=development`.
- **Frontend**: Use Angular's development server with `ng serve`.

---

## Project-Specific Conventions

### Backend
- Follow Flask's application factory pattern.
- Organize business logic into services and utilities.
- Use `.env` files for sensitive configurations (e.g., database credentials).

### Frontend
- Use Angular's CLI for generating components and services.
- Follow Angular's module-based architecture.

---

## Integration Points

### External Dependencies
- **MariaDB**: Used for data storage. Configuration is in `docker-compose.yml`.
- **SMTP**: Used for sending emails. Configuration is in `backend/app/utils/smtp.py`.

### Cross-Component Communication
- The frontend communicates with the backend via REST APIs. Routes are defined in `backend/app/routes.py`.

---

## Key Files and Directories
- `backend/app/main.py`: Flask application entry point.
- `backend/app/services/`: Contains backend business logic.
- `frontend/src/app/`: Contains Angular components and services.
- `db/init.sql`: Database schema and initial data.
- `docker-compose.yml`: Defines the containerized application setup.

---

## Notes for AI Agents
- Ensure Docker is running before executing build or run commands.
- When modifying backend services, update corresponding routes in `backend/app/routes.py`.
- For frontend changes, ensure consistency with Angular's module-based structure.
- Validate database changes against `db/init.sql` to maintain schema integrity.

---

Feel free to update this document as the project evolves!