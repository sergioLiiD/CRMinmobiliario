# CRM Inmobiliario

A modular CRM system for real estate companies.

## Project Structure

The project is organized into independent modules:
- Authentication Module: Handles user authentication and authorization
- Clients Module: Core module for managing client information
- Properties Module: Manages real estate properties

## Setup Instructions

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

4. Run the development server:
```bash
flask run
```

## Module Structure

Each module follows the same structure:
- `routes.py`: HTTP endpoints
- `models.py`: Database models
- `services.py`: Business logic

## Adding New Modules

To add a new module:
1. Create a new directory under `app/`
2. Add `__init__.py`, `routes.py`, `models.py`, and `services.py`
3. Register the blueprint in `app/__init__.py`
