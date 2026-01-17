# Spy Cat Agency – Backend

Backend API for the Spy Cat Agency test assignment.

The application provides RESTful endpoints to manage:
- Spy Cats
- Missions
- Targets

Built with Django and Django REST Framework.

---

## 🚀 Tech Stack

- Python 3.10+
- Django
- Django REST Framework
- SQLite (default, can be replaced)
- TheCatAPI (breed validation)

---

## ⚙️ Setup & Run

### 1. Clone repository
```bash

git clone https://github.com/<your-username>/spy-cat-agency-backend.git
cd spy-cat-agency-backend


### 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux / macOS
venv\Scripts\activate     # Windows

### 3. Install dependencies
pip install -r requirements.txt

### 4. Run migrations
python manage.py migrate

### 5. Start server
python manage.py runserver

Backend will be available at:
http://127.0.0.1:8000/
