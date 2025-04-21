# Master List Application

A full-stack application with an Angular frontend and Python backend, designed to manage and display lists.

## Project Structure

This is a mono-repo with the following structure:

```
master-list/
├── packages/
│   ├── master-list-ui/    # Angular frontend
│   └── master-list-api/   # Python backend
│       └── docker/        # Docker setup for database
```

## Technologies Used

### Frontend
- Angular v19.0.0
- Azure B2C Authentication (with Google/Facebook IDP support)

### Backend
- Python 3.11.12
- PostgreSQL Database (containerized)

## Prerequisites

- Node.js and npm
- Python 3.11.12
- Docker and Docker Compose

## Getting Started

### Setting Up the Database

1. Navigate to the Docker folder within the API directory:
   ```bash
   cd packages/master-list-api/docker
   ```

2. Initialize the database:
   ```bash
   docker-compose --env-file ../.env --profile init build --no-cache
   ```

3. Start the database container:
   ```bash
   docker-compose --env-file ../.env --profile init up
   ```

Note: The database schema is located in the `db_init` folder along with the startup script `pg_db_init.py`.

### Setting Up the Backend

1. Navigate to the backend directory:
   ```bash
   cd packages/master-list-api
   ```

2. Verify Python version:
   ```bash
   python --version  # Should be Python 3.11.x
   ```

3. If you don't have Python 3.11 installed, follow the instructions at [python.org](https://www.python.org/downloads/) to install it.

4. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

5. Activate the virtual environment:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

6. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

7. Create a `.env` file in the `master-list-api` directory with the following structure:
   ```
   POSTGRES_USER=notes_user
   POSTGRES_PASSWORD=notes_password
   POSTGRES_DB=notes_db
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   TENANT_ID="<azure info>"
   AUDIENCE="<azure info>"
   JWKS_URL="<azure info>"
   AZURE_AD_CLIENT_ID="<azure info>"
   AZURE_AD_CLIENT_SECRET="<azure info>"
   ```
   Contact the repository owners for the specific Azure values.

8. Run the backend application:
   ```bash
   python api.py
   ```

### Setting Up the Frontend

1. Navigate to the frontend directory:
   ```bash
   cd packages/master-list-ui
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```
   This runs `ng serve --ssl` as defined in the package.json.

## Configuration

- Frontend configuration is managed in the `environment.ts` file.
- Backend configuration is managed through the `.env` file.

## Database Management

If you need to modify the database schema:

1. Make your changes to the schema files in the `db_init` folder.
2. Remove existing Docker containers.
3. Delete the files inside the `docker/postgres/data` folder (where DB files are persisted).
4. Run the Docker Compose build command again:
   ```bash
   docker-compose --env-file ../.env --profile init build --no-cache
   ```

## Authentication

This application uses Azure B2C for authentication with the following features:
- Sign-up/Sign-in policies
- Google/Facebook identity providers
- Password reset functionality

## Contributing

Please contact repository owners for contribution guidelines.

## License

[Your License Here]