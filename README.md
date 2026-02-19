# E-Sports Tournament Manager

A web application for organizing and managing esports tournaments, teams, and players. Built with Flask, SQLAlchemy, and Tailwind CSS.

## Technology Stack

- **Backend**: Flask 2.3.3
- **Database**: MySQL 8.0 with SQLAlchemy ORM + PyMySQL
- **Frontend**: HTML5, Jinja2 Templates
- **Styling**: Tailwind CSS 3 (CDN)
- **Icons**: Font Awesome 6.4.0
- **Auth**: Session-based + Steam OpenID
- **Deployment**: Docker + Docker Compose

## Features

- Role-based access control (Player, Team Leader, Organizer)
- Steam authentication (OpenID)
- FACEIT profile integration
- Tournament creation & bracket generation (Single Elimination)
- Team management with logos
- Admin dashboard (user management, approvals, announcements)
- File uploads (avatars, team logos)
- Responsive dark UI

## Roles

| Role | Access |
|------|--------|
| `player` | Tournaments, profile, team membership |
| `team_leader` | + Create/manage teams |
| `organizer` | + Admin panel, create tournaments, manage users |

## Production Deployment (Docker)

### Requirements
- Docker + Docker Compose

### Run

```bash
git clone https://github.com/stiapanreha-dev/Esports-Tournament-Management.git
cd Esports-Tournament-Management
docker compose -f docker-compose.prod.yml up -d --build
```

App runs on port `5050`. Configure a reverse proxy (nginx) to forward traffic.

### Environment Variables

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Flask session secret |
| `DATABASE_URL` | MySQL URL: `mysql+pymysql://user:pass@host/db` |
| `STEAM_API_KEY` | Steam Web API key |
| `FACEIT_API_KEY` | FACEIT API key |
| `FLASK_ENV` | `production` |

### Grant Admin Access

After first login, promote a user to organizer via MySQL:

```bash
docker exec esports-mysql mysql -uesports -pesports-db-secret esports -e \
  "UPDATE user SET role='organizer' WHERE username='YOUR_USERNAME';"
```

## API Routes

### Auth
- `GET /login` — Login page
- `POST /login` — Submit login
- `GET /register` — Register
- `GET /logout` — Logout
- `GET /auth/steam` — Steam OpenID login
- `GET /auth/steam/callback` — Steam callback

### Tournaments
- `GET /tournaments` — List
- `GET /tournament/<id>` — Detail
- `POST /tournament/create` — Create (organizer)
- `POST /tournament/<id>/register` — Register
- `GET /tournament/<id>/bracket` — Bracket

### Teams
- `GET /teams` — List
- `POST /team/create` — Create
- `GET /team/<id>` — Detail
- `GET /team/<id>/manage` — Manage
- `POST /team/<id>/add_member` — Add member

### Profile
- `GET /profile` — Own profile
- `GET /player/<username>` — Public profile
- `POST /profile/edit` — Edit profile

### Admin (organizer only)
- `GET /admin` — Dashboard
- `GET /admin/users` — Manage users
- `GET /admin/teams` — Verify teams
- `GET /admin/registrations` — Approve registrations
- `GET /admin/announcements` — Manage announcements

### API
- `POST /api/generate_bracket/<id>` — Generate bracket
- `POST /api/update_match/<id>` — Update match result

## Database Models

- **User** — accounts with roles, Steam ID, FACEIT data
- **Team** — teams with members and verification
- **TeamMember** — membership (captain / member)
- **Tournament** — tournaments with bracket type, prize pool
- **TournamentRegistration** — registrations (pending / approved / rejected)
- **Match** — matches per round
- **MatchResult** — scores and screenshots
- **Announcement** — system announcements with priority

## Project Structure

```
├── app.py                    # Main Flask application
├── config.py                 # Configuration
├── requirements.txt          # Python dependencies
├── Dockerfile
├── docker-compose.prod.yml
├── static/
│   └── uploads/              # User uploads
└── templates/
    ├── base.html
    ├── auth/
    ├── tournament/
    ├── team/
    ├── profile/
    ├── dashboard/
    ├── admin/
    └── errors/
```
