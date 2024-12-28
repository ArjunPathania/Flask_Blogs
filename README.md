# Blog Project

This project is a simple blog application built using Flask, with features like posting articles, user registration, commenting, and more. It is structured to be easy to extend with additional functionality.

## Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Setup](#setup)
- [Directory Structure](#directory-structure)
- [Testing](#testing)
- [Docker Setup](#docker-setup)
- [CI/CD](#cicd)
- [License](#license)

## Features
- User registration and login
- Create, edit, and delete blog posts
- Post comments on blog posts
- Responsive design using custom CSS
- Integrated with a database using SQLAlchemy
- RESTful API for blog posts and comments (optional)

## Tech Stack
- **Backend**: Flask, SQLAlchemy
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite (default) or PostgreSQL
- **Forms**: WTForms
- **Authentication**: Flask-Login
- **Testing**: pytest
- **CI/CD**: GitHub Actions
- **Containerization**: Docker, Docker Compose

## Setup

### Prerequisites
- Python 3.7+
- Virtualenv (or equivalent)

### Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/yourusername/blog-project.git
    cd blog-project
    ```

2. Create a virtual environment and activate it:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Configure your database in `config.py` (default is SQLite, but you can switch to PostgreSQL).

5. Run migrations to set up the database:
    ```bash
    flask db upgrade
    ```

6. Start the development server:
    ```bash
    flask run
    ```

    The app should now be running at `http://localhost:5000`.

## Directory Structure

```plaintext
blog-project/
│                     # Core application folder
├── static/              # Static files (CSS, JS, images)
├── templates/           # HTML templates
├── forms.py             # WTForms classes
├── main.py            # Backend Server 
│
├── .gitignore               # Git ignore file
├── README.md                # Project documentation
├── requirements.txt         # Python dependencies
└── LICENSE                  # Project license

