# Training Log System

A Python application for managing and analyzing personal training logs using a relational SQL database.

The system allows users to create accounts, record exercises and training sessions, and retrieve training history and volume statistics. The application separates business logic from database operations, allowing the same application code to work with different SQL backends.

The workflow of the system is illustrated in:

docs/training-log-management-workflow.pdf

---

## Architecture

The application follows a simple layered design:

- **app.py** – application logic and user interaction
- **database.py** – database queries and data access layer

This separation allows the database backend to be changed without modifying the application logic.

---

## Technologies

- Python
- SQL
- SQLite
- PostgreSQL

---

## Database Schema

The system uses three relational tables.

### users
Stores user accounts.

- id (primary key)
- username

### exercises
Stores exercises associated with each user.

- id (primary key)
- user_id (foreign key → users.id)
- exercise_name
- training_type

### trainings
Stores individual training records.

- id (primary key)
- user_id (foreign key → users.id)
- exercise_id (foreign key → exercises.id)
- date
- sets
- reps
- intensity_kg
- workout_type
- body_weight_kg
- observations

---

## Features

- User account creation and selection
- Exercise management by muscle group
- Training session logging
- Retrieval of training history
- Training volume analysis by muscle group
- Visualization of training statistics

---

## Database Implementations

Two database implementations are provided.

**SQLite**  
Branch: `app_sqlite`  
Uses the Python `sqlite3` library and includes a local database for testing.

**PostgreSQL**  
Branch: `app_postgresql`  
Uses `psycopg2` and requires a configured PostgreSQL database.
