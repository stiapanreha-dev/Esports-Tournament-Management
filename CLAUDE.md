# Esports Tournament Management (KAI Arena)

## Project
- **Stack:** Flask + SQLAlchemy + MySQL 8.0 (PyMySQL) + Tailwind CSS + Font Awesome 6
- **Repo:** stiapanreha-dev/Esports-Tournament-Management
- **Branch:** main
- **PROD:** 202.49.176.75, path `/root/apps/esports`, `http://202.49.176.75`
- **Containers:** esports-app (port 5050→5000), esports-mysql (3306)
- **SSH:** `ssh SRV010` (ключ `~/.ssh/SRV010`)

## Deploy
```bash
# Local: commit + push
cd /home/lexun/work/KWORK/esports-deploy
git add <files> && git commit -m "..." && git push origin main

# PROD: pull + rebuild
ssh SRV010 "cd /root/apps/esports && git pull && docker compose -f docker-compose.prod.yml down && docker compose -f docker-compose.prod.yml up -d --build"
```

## DB Migrations (MySQL)
`db.create_all()` не добавляет колонки в существующие таблицы.
- Новые колонки: `docker exec esports-mysql mysql -uesports -pesports-db-secret esports -e "ALTER TABLE ... ADD COLUMN ..."`
- MySQL поддерживает `ADD COLUMN ... UNIQUE` напрямую

## Key Files
- `app.py` — routes, models, all logic
- `config.py` — config class (SECRET_KEY, STEAM_API_KEY, FACEIT_API_KEY, GAMES list)
- `docker-compose.prod.yml` — env vars (STEAM_API_KEY, FACEIT_API_KEY)
- `templates/` — Jinja2 templates (Tailwind CSS)

## Auth
- Standard login/password (Werkzeug hashes, prefix `pbkdf2:` or `scrypt:`)
- Steam OpenID 2.0 (`/auth/steam`, `/auth/steam/callback`)
- Steam users: `email={steam_id}@steam.local`, `password='!steam-auth'`
- Login check: `user.password.startswith(('pbkdf2:', 'scrypt:'))` before `check_password_hash`

## External APIs
- **Steam:** OpenID 2.0 + GetPlayerSummaries (key in STEAM_API_KEY)
- **FACEIT:** Data API v4, lookup by `game_player_id` (Steam64), key in FACEIT_API_KEY
  - Endpoint: `GET https://open.faceit.com/data/v4/players?game=csgo&game_player_id={steam_id}`
  - Auth: `Authorization: Bearer {key}`
  - Games in response: `data['games'][game_key]` -> `faceit_elo`, `skill_level`

## Public Routes (no auth required)
- `/player/<username>` — public player profile with FACEIT data
- `/tournaments`, `/tournament/<id>`, `/teams`, `/team/<id>`

## Gotchas
- ProxyFix required for correct `url_for(_external=True)` behind nginx proxy
- FACEIT CDN logo URLs return 403 — use inline SVG instead
- FACEIT level icons from CDN work: `https://cdn-frontend.faceit-cdn.net/web/static/media/assets_images_skill-icons_skill_level_{level}_svg.svg`
- Avatar field can be external URL (Steam) or local filename — template checks `startswith('http')`
