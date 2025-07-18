
#  EduHive Backend (Flask API)

EduHive is a **crowdsourced learning platform** with gamification, designed to help learners create, share, and engage with structured learning paths while earning points, badges, and competing on leaderboards. This repository contains the **Flask API** that powers the EduHive platform.

---

##  Features

*  User authentication (JWT) and role management (Admin, Contributor, Learner)
* CRUD for Learning Paths, Modules, Quizzes, and Resources
*  Gamification support: XP system, badges, achievements
*  Community tools: Ratings, comments, discussions
*  Leaderboards and challenge tracking
* 🔧 Admin tools for moderation

---

##  Tech Stack

* **Python 3.11+**
* **Flask**
* **Flask-SQLAlchemy**
* **Flask-Migrate**
* **Flask-JWT-Extended**
* **SerializerMixin** (for serialization)
* **SQLite / PostgreSQL/PostMan** (switchable)

---

##  Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/yourusername/EduHive-Backend.git

cd EduHive-Backend
```

### 2. Create and Activate a Virtual Environment

```bash

pipenv shell

```
### 3. Install Dependencies

```bash
pipenv install -r requirements.txt
```

### 4. Set Environment Variables

Create a `.env` file:

```env
FLASK_ENV=development

DATABASE_URL=sqlite:///eduhive.db

SECRET_KEY=your_secret_key

JWT_SECRET_KEY=your_jwt_key
```

### 5. Run Migrations

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 6. Start the Server

```bash
flask run
```

The API will be available at: `http://127.0.0.1:5000/`

---

##  Folder Structure

```
EduHive-Backend/
├── app/
│   ├── models/              # SQLAlchemy models
│   ├── routes/              # API route blueprints
│   ├── schemas/             # Marshmallow schemas
│   ├── utils/               # Helper functions
│   └── __init__.py          # App factory
├── migrations/              # Flask-Migrate files
├── requirements.txt
├── .env
└── run.py
```

---

##  Roles & Permissions

* **Admin**: Moderate content, approve paths, manage badges/challenges
* **Contributor**: Create learning paths, modules, and quizzes
* **Learner**: Follow paths, earn XP, unlock badges, comment

---

##  API Endpoints Overview (MVP)

| Method | Endpoint             | Description                          |
| ------ | -------------------- | ------------------------------------ |
| POST   | `/auth/signup`       | User registration                    |
| POST   | `/auth/login`        | User login (JWT token)               |
| GET    | `/paths`             | List all learning paths              |
| POST   | `/paths`             | Create a new learning path (contrib) |
| GET    | `/leaderboard`       | Global leaderboard                   |
| POST   | `/comments`          | Add comment to path/module           |
| GET    | `/profile/<user_id>` | Get user profile & XP stats          |

---

##  MVP Checklist

*  User authentication (JWT)
*  Role-based access control
*  Learning path and module CRUD
*  Points/XP system
*  Badge and achievement unlock
*  Leaderboard and challenge logic
*  Comment and rating system

---

##  Related Repositories

* [EduHive-Frontend](https://github.com/Mitche-44/EduHive-Frontend)

---

##  Contributing

1. Fork the project
2. Create your feature branch (`git checkout -b feature/awesome-feature`)
3. Commit your changes (`git commit -m 'Add awesome feature'`)
4. Push to the branch (`git push origin feature/awesome-feature`)
5. Open a Pull Request

---

## License

MIT License © 2025 EduHive Team

---

