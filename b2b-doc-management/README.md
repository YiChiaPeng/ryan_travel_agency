# B2B Document Upload and Review Management System

## Overview
This project is a B2B document upload and review management system designed to facilitate the submission and processing of customer documents. It consists of a frontend built with Angular and a backend developed in Python using Flask, with a MariaDB database for data storage.

## Features
- **B2B Client Portal:**
  - User authentication with company-based login.
  - Multi-file upload for customer documents.
  - Submission of application forms with various fields.
  - View submission history and notifications for rejected documents.
  - Ability to upload supplementary documents for rejected applications.

- **Admin Portal:**
  - Admin login to access the management dashboard.
  - View and filter submissions by date, company, and urgency.
  - Export submission records to Excel files, organized by company.
  - Mark submissions with rejection reasons and manage resubmissions.

## Project Structure
```
b2b-doc-management
├── backend
│   ├── app
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── routes.py
│   │   ├── services
│   │   │   ├── auth.py
│   │   │   ├── file_upload.py
│   │   │   └── notification.py
│   │   └── utils
│   │       ├── db.py
│   │       └── smtp.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend
│   ├── src
│   │   ├── app
│   │   │   ├── components
│   │   │   ├── services
│   │   │   └── app.module.ts
│   │   └── assets
│   ├── angular.json
│   ├── package.json
│   └── Dockerfile
├── db
│   └── init.sql
├── docker-compose.yml
└── README.md
```

## Setup Instructions

### Prerequisites
- Docker and Docker Compose installed on your machine.
- Python 3.x for backend development (if running locally).

### Running the Application
1. Clone the repository:
   ```
   git clone <repository-url>
   cd b2b-doc-management
   ```

2. Build and run the application using Docker Compose:
   ```
   docker-compose up --build
   ```

3. Access the frontend application at `http://localhost:4200` and the backend API at `http://localhost:5000`.

### Database Initialization
The database schema and initial data can be set up by executing the SQL commands in `db/init.sql`. This can be done automatically when the database container starts.

## Usage
- For B2B clients, log in using your company credentials to access the document submission portal.
- Admins can log in to manage submissions and handle document reviews.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.