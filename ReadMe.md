

# EduHive Backend (Flask API)

EduHive is a **crowdsourced, gamified learning platform** that allows learners to explore curated paths, contributors to create educational content, and admins to manage the system through a robust backend. This repository contains the **Flask API** powering EduHive.

---
> **Note:** The free Render hosting tier does **not support WebSockets**, which may result in connection failures for real-time features. To ensure compatibility, consider using long polling as a fallback on the frontend, or upgrade to a hosting provider that supports WebSockets natively
## Features

* JWT-based authentication with role management (`Admin`, `Contributor`, `Learner`)
* Google OAuth integration
* CRUD for Learning Paths, Modules, Quizzes, and Resources
* Gamification: XP system, badges, and leaderboards
* Real-time Community Discussions (Socket.IO)
* Commenting, likes, and discussion forums
* Admin tools for approval and moderation
* Subscriptions, testimonials, newsletters

---

## Tech Stack

* Python 3.11+
* Flask, Flask-RESTful
* Flask-JWT-Extended
* Flask-SocketIO
* SQLAlchemy and Flask-Migrate
* PostgreSQL (via Supabase)
* Marshmallow or SerializerMixin for serialization
* Deployed on Render

---

## Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/Mitche-44/EduHive-Backend.git

cd EduHive-Backend
```

### 2. Activate Environment and Install Dependencies

```bash
pipenv install
pipenv shell
```

### 3. Set Up Environment Variables

Create a `.env` file in the root folder:

```env
FLASK_ENV=development

SECRET_KEY=your_secret_key

JWT_SECRET_KEY=your_jwt_secret

DATABASE_URL=your_database_url
```

### 4. Initialize the Database

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 5. Run the Development Server

```bash
flask run or python app.py
```

The server runs at `http://127.0.0.1:5000/`

---

## Folder Structure

```
EduHive-Backend/
├── models/             # SQLAlchemy models
├── resources/          # API route classes
├── utils/              # Helpers, decorators, validators
├── config.py           # App configuration
├── app.py              # Main app entry
├── migrations/         # Flask-Migrate DB files
├── requirements.txt
└── .env
```

---

## Roles & Permissions

* **Admin**: Manage users, approve paths/posts, control platform settings
* **Contributor**: Create paths, modules, and quizzes
* **Learner**: Consume content, engage in discussions, earn badges

---

## Sample API Endpoints

| Method | Endpoint              | Description                        |
| ------ | --------------------- | ---------------------------------- |
| POST   | `/auth/register`      | Register a new user                |
| POST   | `/auth/login`         | Authenticate user via JWT          |
| POST   | `/auth/google-login`  | Login via Google OAuth             |
| GET    | `/paths`              | Get all learning paths             |
| POST   | `/paths`              | Create a new path (Contributor)    |
| GET    | `/leaderboard`        | View global leaderboard            |
| PATCH  | `/admin/approve/<id>` | Admin approval for user            |
| POST   | `/community/post`     | Create a community discussion post |

---

## Related Links

* **Frontend Repository:** [EduHive Frontend](https://github.com/Mitche-44/EduHive-Frontend)

* **Frontend App:** [https://edu-hive-frontend.vercel.app](https://edu-hive-frontend.vercel.app)

* **Supabase Project:** [View on Supabase](https://supabase.com/dashboard/project/srsiutpdrjvvafvjyhzu)

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes
4. Push to your fork
5. Open a pull request

---

## License

MIT License © 2025 EduHive Team

---


