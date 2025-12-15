# E-Sports Tournament Manager

A comprehensive web application for organizing and managing esports tournaments, teams, and players. Built with Flask, SQLAlchemy, and Tailwind CSS.

## Project Status ✅

The application is **fully developed and running** with all core features implemented and tested.

## Key Features

### 1. **User Management**
- Role-based access control (Player, Team Leader, Organizer)
- User authentication & session management
- User profiles with stats and activity tracking
- Profile editing with avatar upload capability

### 2. **Tournament Management**
- Create and manage tournaments
- Multiple game support (VALORANT, DOTA 2, Free Fire, PUBG Mobile, etc.)
- Tournament status tracking (Upcoming, Ongoing, Completed)
- Prize pool management
- Bracket generation (Single Elimination)
- Tournament registration with approval system
- Match management and result reporting

### 3. **Team Management**
- Create and manage teams
- Team member management (Add/Remove players)
- Team verification system
- Team logos and customization
- Multiple teams per game

### 4. **Communication & Announcements**
- System announcements with priority levels
- Tournament updates
- Promotional announcements
- Expiring announcements

### 5. **Admin Dashboard**
- User management (Activate/Deactivate)
- Team verification
- Tournament registration approvals
- Announcement management
- Dashboard statistics
- System administration

### 6. **User Dashboards**
- **Player Dashboard**: Tournament registrations, team memberships
- **Team Leader Dashboard**: Team management, tournament registrations
- **Organizer Dashboard**: Tournament creation, quick actions, approvals

## Technology Stack

- **Backend**: Flask 2.3.3
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML5, Jinja2 Templates
- **Styling**: Tailwind CSS 3 (CDN-based)
- **Icons**: Font Awesome 6.4.0
- **Authentication**: JWT + Session-based
- **Python**: 3.13.9

## Database Models

1. **User** - User accounts with roles (player, team_leader, organizer)
2. **Team** - Teams with members and verification status
3. **TeamMember** - Team membership tracking
4. **Tournament** - Tournament details and configuration
5. **TournamentRegistration** - Team registrations for tournaments
6. **Match** - Match details and matchups
7. **MatchResult** - Match results and scores
8. **Announcement** - System announcements

## Project Structure

```
esports-tournament/
├── app.py                          # Main Flask application (986 lines)
├── config.py                       # Configuration settings
├── seed.py                         # Database seeding script
├── requirements.txt                # Python dependencies
├── setup.py                        # Setup script
├── instance/
│   └── tournament.db              # SQLite database
├── static/
│   ├── css/style.css             # Custom styles
│   ├── js/main.js                # JavaScript utilities
│   └── uploads/                  # User uploads
├── templates/
│   ├── base.html                 # Base template with navigation
│   ├── index.html                # Home page
│   ├── auth/
│   │   ├── login.html            # Login form
│   │   └── register.html         # Registration form
│   ├── tournament/
│   │   ├── list.html             # Tournament listing
│   │   ├── detail.html           # Tournament details
│   │   ├── create.html           # Create tournament
│   │   └── bracket.html          # Tournament bracket
│   ├── team/
│   │   ├── list.html             # Team listing
│   │   ├── create.html           # Create team
│   │   ├── view.html             # Team details
│   │   └── manage.html           # Team management
│   ├── profile/
│   │   ├── view.html             # User profile
│   │   └── edit.html             # Edit profile
│   ├── dashboard/
│   │   ├── player.html           # Player dashboard
│   │   ├── team_leader.html      # Team leader dashboard
│   │   └── organizer.html        # Organizer dashboard
│   ├── admin/
│   │   ├── panel.html            # Admin dashboard
│   │   ├── users.html            # User management
│   │   ├── teams.html            # Team verification
│   │   ├── registrations.html    # Registration approvals
│   │   └── announcements.html    # Announcement management
│   └── errors/
│       ├── 404.html              # 404 error page
│       └── 500.html              # 500 error page
```

## Getting Started

### Installation

1. **Clone/Navigate to project directory**:
   ```bash
   cd "c:\Users\KARTHIK\OneDrive\Pictures\Documents\SEM 6 Projects\esports-tournament"
   ```

2. **Virtual Environment** (Already set up in `.venv`):
   ```bash
   .\.venv\Scripts\activate
   ```

3. **Install Dependencies** (Already installed):
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. **Start the Flask server**:
   ```bash
   .\.venv\Scripts\python.exe app.py
   ```
   
   The application will start at `http://localhost:5000`

2. **Populate Sample Data** (Optional, already seeded):
   ```bash
   .\.venv\Scripts\python.exe seed.py
   ```

### Sample Credentials

After running the seed script, you can log in with:

| Role | Username | Password |
|------|----------|----------|
| Admin/Organizer | admin | admin123 |
| Organizer | organizer1 | password123 |
| Team Leader | leader1 | password123 |
| Player | player1 | password123 |

## API Routes Implemented

### Authentication
- `GET /` - Home page
- `GET /register` - Registration form
- `POST /register` - Submit registration
- `GET /login` - Login form
- `POST /login` - Submit login
- `GET /logout` - Logout

### Tournaments
- `GET /tournaments` - List all tournaments
- `GET /tournament/<id>` - View tournament details
- `GET /tournament/create` - Create tournament form
- `POST /tournament/create` - Submit tournament
- `GET /tournament/<id>/register` - Register team
- `GET /tournament/<id>/bracket` - View bracket

### Teams
- `GET /teams` - List all teams
- `GET /team/create` - Create team form
- `POST /team/create` - Submit team
- `GET /team/<id>` - View team details
- `GET /team/<id>/manage` - Manage team
- `POST /team/<id>/add_member` - Add team member

### Profile
- `GET /profile` - View profile
- `GET /profile/edit` - Edit profile form
- `POST /profile/edit` - Submit profile edits

### Admin
- `GET /admin` - Admin dashboard
- `GET /admin/users` - Manage users
- `GET /admin/teams` - Verify teams
- `GET /admin/registrations` - Approve registrations
- `GET /admin/announcements` - Manage announcements

### API Endpoints
- `POST /api/generate_bracket/<tournament_id>` - Generate tournament bracket
- `POST /api/update_match/<match_id>` - Update match result

## Features Implemented

### Core Features (100% Complete)
✅ User authentication & role-based access control  
✅ Tournament creation & management  
✅ Team creation & member management  
✅ User profiles with editing  
✅ Tournament registration  
✅ Match bracket generation  
✅ Admin panel with full controls  
✅ Announcements system  
✅ File uploads (logos, avatars)  
✅ Responsive UI with Tailwind CSS  
✅ Flash messages & notifications  

### Database Features
✅ SQLite database with proper relations  
✅ Cascade delete operations  
✅ Data validation  
✅ Unique constraints  
✅ Foreign key relationships  

### UI/UX Features
✅ Gradient navigation bar  
✅ Responsive grid layouts  
✅ Dark theme styling  
✅ Font Awesome icons  
✅ Form validation  
✅ Success/Error messages  
✅ Mobile-friendly design  

## Testing

### Manual Testing Checklist

1. **Authentication** - ✅
   - Register new user
   - Login with existing credentials
   - Logout functionality
   - Role-based redirects

2. **Tournaments** - ✅
   - Browse tournaments
   - View tournament details
   - Create tournament (organizer only)
   - Register team in tournament
   - View brackets

3. **Teams** - ✅
   - Browse teams
   - Create team (team_leader)
   - View team details
   - Manage team members
   - Upload team logo

4. **Profiles** - ✅
   - View profile
   - Edit profile information
   - Upload avatar

5. **Admin** - ✅
   - Access admin dashboard
   - Manage users
   - Verify teams
   - Approve registrations
   - Create announcements
   - View statistics

6. **Error Handling** - ✅
   - 404 error page
   - 500 error page
   - Validation errors
   - Permission denials

## Database Seeding

The database comes pre-populated with:
- **8 Users**: Across all roles (Admin, Organizers, Team Leaders, Players)
- **3 Teams**: Verified and unverified teams
- **4 Tournaments**: Various states (upcoming, ongoing, completed)
- **3 Announcements**: Different priorities and categories

## Configuration

Key settings in `config.py`:
```python
GAMES = ['VALORANT', 'DOTA 2', 'CS:GO', 'Free Fire', 'PUBG Mobile', 'League of Legends', 'Mobile Legends']
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
SECRET_KEY = 'your-secret-key-here'
```

## Deployment Notes

For production deployment:
1. Change `FLASK_ENV` to `production`
2. Set a strong `SECRET_KEY`
3. Use a production WSGI server (Gunicorn, Waitress)
4. Use PostgreSQL instead of SQLite
5. Enable HTTPS
6. Set up proper logging
7. Configure CORS if needed
8. Use environment variables for sensitive data

## Troubleshooting

### Database Reset
If you need to reset the database:
```bash
# Delete the database file
rm instance/tournament.db

# Reinitialize from Flask shell
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# Re-seed with sample data
.\.venv\Scripts\python.exe seed.py
```

### Port Already in Use
If port 5000 is already in use:
```bash
# Edit app.py or use:
.\.venv\Scripts\python.exe -c "from app import app; app.run(port=5001)"
```

### Template Not Found
If a template is missing, check the `templates/` directory structure matches the routes in `app.py`.

## Future Enhancements

The following features are recommended for future versions:
- WebSocket integration for real-time match updates
- Payment gateway integration for entry fees
- Player ranking/rating system
- Email notifications
- Mobile application
- Advanced analytics dashboard
- Live streaming integration
- Chat/Communication features

## Development Workflow

1. **Make changes** to templates or Python files
2. **Flask auto-reloads** on save (debug mode enabled)
3. **Check browser** for changes
4. **Test functionality** with sample data
5. **Commit changes** to version control

## Support & Documentation

For detailed API documentation, see comments in `app.py`.

For frontend changes, refer to template files with detailed HTML comments.

## License

This is a SEM 6 Projects assignment.

## Author

Developed as part of E-Sports Tournament Management System (SEM 6 Project)

---

**Last Updated**: December 14, 2025  
**Application Status**: ✅ **FULLY FUNCTIONAL**  
**All Core Features**: ✅ **IMPLEMENTED & TESTED**
