import os
import re
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_from_directory, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
from urllib.parse import urlencode
import requests as http_requests
import jwt
from functools import wraps
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password = db.Column(db.String(200), nullable=True)
    steam_id = db.Column(db.String(20), unique=True, nullable=True)
    ign = db.Column(db.String(80))  # In-Game Name
    full_name = db.Column(db.String(100))
    bio = db.Column(db.Text)
    avatar = db.Column(db.String(200))
    role = db.Column(db.String(20), default='player')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    team_memberships = db.relationship('TeamMember', backref='user', lazy=True, cascade='all, delete-orphan')
    created_teams = db.relationship('Team', backref='creator', lazy=True)
    organized_tournaments = db.relationship('Tournament', backref='organizer', lazy=True)
    match_results = db.relationship('MatchResult', backref='reporter', lazy=True, foreign_keys='MatchResult.reported_by')
    
    def get_stats(self):
        """Calculate player statistics"""
        stats = {
            'tournaments_played': 0,
            'tournaments_won': 0,
            'matches_played': 0,
            'matches_won': 0,
            'win_rate': 0
        }
        return stats

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    tag = db.Column(db.String(10), unique=True)
    logo = db.Column(db.String(200))
    game = db.Column(db.String(50))
    description = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    members = db.relationship('TeamMember', backref='team', lazy=True, cascade='all, delete-orphan')
    tournament_registrations = db.relationship('TournamentRegistration', backref='team_reg', lazy=True)
    matches_as_team1 = db.relationship('Match', foreign_keys='Match.team1_id', backref='team1_rel', lazy=True)
    matches_as_team2 = db.relationship('Match', foreign_keys='Match.team2_id', backref='team2_rel', lazy=True)

class TeamMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role = db.Column(db.String(20), default='member')
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('team_id', 'user_id', name='unique_team_member'),)

class Tournament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    game = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    rules = db.Column(db.Text)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    max_teams = db.Column(db.Integer, default=16)
    max_players = db.Column(db.Integer, default=1)
    entry_fee = db.Column(db.Float, default=0.0)
    prize_pool = db.Column(db.Float, default=0.0)
    registration_deadline = db.Column(db.DateTime)
    bracket_type = db.Column(db.String(20), default='single_elimination')
    status = db.Column(db.String(20), default='upcoming')
    thumbnail = db.Column(db.String(200))
    organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    registrations = db.relationship('TournamentRegistration', backref='tournament_reg', lazy=True, cascade='all, delete-orphan')
    matches = db.relationship('Match', backref='tournament_rel', lazy=True, cascade='all, delete-orphan')
    
    def get_registered_count(self):
        return TournamentRegistration.query.filter_by(
            tournament_id=self.id,
            status='approved'
        ).count()
    
    def is_registration_open(self):
        return (self.registration_deadline is None or 
                self.registration_deadline > datetime.utcnow()) and \
               self.status == 'upcoming'

class TournamentRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    player_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')
    
    # Relationships
    team = db.relationship('Team')
    player = db.relationship('User')
    
    __table_args__ = (
        db.UniqueConstraint('tournament_id', 'team_id', name='unique_team_registration'),
        db.UniqueConstraint('tournament_id', 'player_id', name='unique_player_registration'),
    )

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=False)
    round = db.Column(db.Integer, nullable=False)
    match_number = db.Column(db.Integer, nullable=False)
    team1_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    team2_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    player1_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    player2_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    scheduled_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='scheduled')
    winner_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    winner_player_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    stream_url = db.Column(db.String(500))
    
    # Relationships
    team1 = db.relationship('Team', foreign_keys=[team1_id])
    team2 = db.relationship('Team', foreign_keys=[team2_id])
    player1 = db.relationship('User', foreign_keys=[player1_id])
    player2 = db.relationship('User', foreign_keys=[player2_id])
    winner_team = db.relationship('Team', foreign_keys=[winner_id])
    winner_user = db.relationship('User', foreign_keys=[winner_player_id])
    result = db.relationship('MatchResult', backref='match_rel', uselist=False, cascade='all, delete-orphan')

class MatchResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    team1_score = db.Column(db.Integer, default=0)
    team2_score = db.Column(db.Integer, default=0)
    player1_score = db.Column(db.Integer, default=0)
    player2_score = db.Column(db.Integer, default=0)
    screenshots = db.Column(db.Text)
    details = db.Column(db.Text)
    reported_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    verified_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    match = db.relationship('Match', backref='match_result')

class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='general')
    priority = db.Column(db.Integer, default=1)  # 1=normal, 2=important, 3=critical
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    creator = db.relationship('User', backref='announcements_created')

# Helper Functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def role_required(roles):
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated(*args, **kwargs):
            user = User.query.get(session['user_id'])
            if user.role not in roles:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated
    return decorator

def generate_bracket(tournament_id):
    """Generate bracket matches for a tournament"""
    tournament = Tournament.query.get(tournament_id)
    if not tournament:
        return False
    
    # Clear existing matches
    Match.query.filter_by(tournament_id=tournament_id).delete()
    
    # Get approved registrations
    registrations = TournamentRegistration.query.filter_by(
        tournament_id=tournament_id,
        status='approved'
    ).all()
    
    if len(registrations) < 2:
        return False
    
    participants = []
    for reg in registrations:
        if tournament.max_players == 1:
            participants.append({'type': 'player', 'id': reg.player_id, 'registration_id': reg.id})
        else:
            participants.append({'type': 'team', 'id': reg.team_id, 'registration_id': reg.id})
    
    # For single elimination, we need power of 2
    import math
    num_participants = len(participants)
    bracket_size = 2 ** math.ceil(math.log2(num_participants))
    
    # Create matches for first round
    matches = []
    match_time = tournament.start_date
    
    for i in range(0, bracket_size, 2):
        match = Match(
            tournament_id=tournament_id,
            round=1,
            match_number=len(matches) + 1,
            scheduled_time=match_time
        )
        
        # Assign participants
        if i < num_participants:
            if participants[i]['type'] == 'player':
                match.player1_id = participants[i]['id']
            else:
                match.team1_id = participants[i]['id']
        
        if i + 1 < num_participants:
            if participants[i + 1]['type'] == 'player':
                match.player2_id = participants[i + 1]['id']
            else:
                match.team2_id = participants[i + 1]['id']
        
        matches.append(match)
        match_time = match_time + timedelta(minutes=30)  # 30 minutes between matches
    
    db.session.add_all(matches)
    
    # Create subsequent rounds
    total_rounds = int(math.log2(bracket_size))
    for round_num in range(2, total_rounds + 1):
        matches_in_round = bracket_size // (2 ** round_num)
        for match_num in range(1, matches_in_round + 1):
            match = Match(
                tournament_id=tournament_id,
                round=round_num,
                match_number=match_num,
                scheduled_time=match_time
            )
            matches.append(match)
            match_time = match_time + timedelta(minutes=30)
    
    db.session.add_all(matches[matches_in_round:])
    db.session.commit()
    
    tournament.status = 'ongoing'
    db.session.commit()
    
    return True

# Routes
@app.route('/')
def index():
    tournaments = Tournament.query.filter(Tournament.status.in_(['upcoming', 'ongoing']))\
        .order_by(Tournament.start_date).limit(6).all()
    
    announcements = Announcement.query.filter(
        (Announcement.expires_at.is_(None)) | (Announcement.expires_at > datetime.utcnow())
    ).order_by(Announcement.priority.desc(), Announcement.created_at.desc()).limit(5).all()
    
    stats = {
        'total_tournaments': Tournament.query.count(),
        'active_tournaments': Tournament.query.filter_by(status='ongoing').count(),
        'total_teams': Team.query.count(),
        'total_players': User.query.count()
    }
    
    return render_template('index.html', 
                         tournaments=tournaments, 
                         announcements=announcements,
                         stats=stats)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        ign = request.form['ign']
        role = request.form.get('role', 'player')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        user = User(
            username=username,
            email=email,
            password=hashed_password,
            ign=ign,
            role=role,
            is_active=True
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.password and check_password_hash(user.password, password):
            if not user.is_active:
                flash('Account is deactivated. Please contact admin.', 'danger')
                return redirect(url_for('login'))
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Set session
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            session['ign'] = user.ign
            
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('auth/login.html')

# Steam OpenID helpers
STEAM_OPENID_URL = 'https://steamcommunity.com/openid/login'

def get_steam_login_url(return_to):
    params = {
        'openid.ns': 'http://specs.openid.net/auth/2.0',
        'openid.mode': 'checkid_setup',
        'openid.return_to': return_to,
        'openid.realm': return_to.rsplit('/', 1)[0] + '/',
        'openid.identity': 'http://specs.openid.net/auth/2.0/identifier_select',
        'openid.claimed_id': 'http://specs.openid.net/auth/2.0/identifier_select',
    }
    return STEAM_OPENID_URL + '?' + urlencode(params)

def get_steam_profile(steam_id):
    api_key = app.config.get('STEAM_API_KEY', '')
    if not api_key:
        return None
    resp = http_requests.get(
        'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/',
        params={'key': api_key, 'steamids': steam_id},
        timeout=10,
    )
    data = resp.json()
    players = data.get('response', {}).get('players', [])
    return players[0] if players else None

@app.route('/auth/steam')
def steam_login():
    return_to = url_for('steam_callback', _external=True)
    return redirect(get_steam_login_url(return_to))

@app.route('/auth/steam/callback')
def steam_callback():
    # Verify the OpenID response
    params = {
        'openid.assoc_handle': request.args.get('openid.assoc_handle', ''),
        'openid.signed': request.args.get('openid.signed', ''),
        'openid.sig': request.args.get('openid.sig', ''),
        'openid.ns': request.args.get('openid.ns', ''),
        'openid.mode': 'check_authentication',
    }
    signed_fields = request.args.get('openid.signed', '').split(',')
    for field in signed_fields:
        key = 'openid.' + field
        params[key] = request.args.get(key, '')

    resp = http_requests.post(STEAM_OPENID_URL, data=params, timeout=10)
    if 'is_valid:true' not in resp.text:
        flash('Steam authentication failed.', 'danger')
        return redirect(url_for('login'))

    # Extract Steam ID from claimed_id
    claimed_id = request.args.get('openid.claimed_id', '')
    m = re.search(r'/id/(\d+)$', claimed_id) or re.search(r'/openid/id/(\d+)$', claimed_id)
    if not m:
        flash('Could not determine Steam ID.', 'danger')
        return redirect(url_for('login'))

    steam_id = m.group(1)

    # Find or create user
    user = User.query.filter_by(steam_id=steam_id).first()
    if not user:
        profile = get_steam_profile(steam_id)
        persona = profile.get('personaname', f'steam_{steam_id}') if profile else f'steam_{steam_id}'
        avatar_url = profile.get('avatarfull', '') if profile else ''

        # Ensure unique username
        base_name = persona
        counter = 1
        while User.query.filter_by(username=persona).first():
            persona = f'{base_name}_{counter}'
            counter += 1

        user = User(
            username=persona,
            steam_id=steam_id,
            ign=base_name,
            avatar=avatar_url or None,
            role='player',
            is_active=True,
        )
        db.session.add(user)
        db.session.commit()
    else:
        # Refresh avatar on each login
        profile = get_steam_profile(steam_id)
        if profile:
            avatar_url = profile.get('avatarfull', '')
            if avatar_url:
                user.avatar = avatar_url

    user.last_login = datetime.utcnow()
    db.session.commit()

    session['user_id'] = user.id
    session['username'] = user.username
    session['role'] = user.role
    session['ign'] = user.ign

    flash('Logged in via Steam!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@token_required
def dashboard():
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    if user.role == 'organizer':
        tournaments = Tournament.query.filter_by(organizer_id=user_id).all()
        pending_registrations = TournamentRegistration.query.filter(
            TournamentRegistration.tournament_id.in_([t.id for t in tournaments]),
            TournamentRegistration.status == 'pending'
        ).count()
        
        return render_template('dashboard/organizer.html', 
                             user=user, 
                             tournaments=tournaments,
                             pending_registrations=pending_registrations)
    
    elif user.role == 'team_leader':
        teams = Team.query.filter_by(created_by=user_id).all()
        team_ids = [team.id for team in teams]
        
        tournaments = TournamentRegistration.query.filter(
            TournamentRegistration.team_id.in_(team_ids),
            TournamentRegistration.status == 'approved'
        ).all()
        
        return render_template('dashboard/team_leader.html', 
                             user=user, 
                             teams=teams,
                             tournaments=tournaments)
    
    else:  # player
        registrations = TournamentRegistration.query.filter_by(player_id=user_id).all()
        team_memberships = TeamMember.query.filter_by(user_id=user_id).all()
        
        return render_template('dashboard/player.html', 
                             user=user, 
                             registrations=registrations,
                             team_memberships=team_memberships)

# Tournament Routes
@app.route('/tournaments')
def tournaments():
    game = request.args.get('game')
    status = request.args.get('status')
    type_filter = request.args.get('type')
    
    query = Tournament.query
    
    if game and game != 'all':
        query = query.filter_by(game=game)
    if status and status != 'all':
        query = query.filter_by(status=status)
    if type_filter:
        if type_filter == 'solo':
            query = query.filter_by(max_players=1)
        elif type_filter == 'team':
            query = query.filter(Tournament.max_players > 1)
    
    tournaments = query.order_by(Tournament.start_date).all()
    return render_template('tournament/list.html', 
                         tournaments=tournaments,
                         games=app.config['GAMES'])

@app.route('/tournament/<int:tournament_id>')
def tournament_detail(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    registrations = TournamentRegistration.query.filter_by(
        tournament_id=tournament_id
    ).all()
    
    matches = Match.query.filter_by(tournament_id=tournament_id)\
        .order_by(Match.round, Match.match_number).all()
    
    is_registered = False
    if 'user_id' in session:
        user_id = session['user_id']
        if tournament.max_players == 1:
            is_registered = TournamentRegistration.query.filter_by(
                tournament_id=tournament_id,
                player_id=user_id
            ).first() is not None
        else:
            # Check if any of user's teams are registered
            user_teams = [tm.team_id for tm in TeamMember.query.filter_by(user_id=user_id).all()]
            is_registered = TournamentRegistration.query.filter(
                TournamentRegistration.tournament_id == tournament_id,
                TournamentRegistration.team_id.in_(user_teams)
            ).first() is not None
    
    return render_template('tournament/detail.html',
                         tournament=tournament,
                         registrations=registrations,
                         matches=matches,
                         is_registered=is_registered)

@app.route('/tournament/create', methods=['GET', 'POST'])
@role_required(['organizer'])
def create_tournament():
    if request.method == 'POST':
        name = request.form['name']
        game = request.form['game']
        description = request.form['description']
        rules = request.form['rules']
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%dT%H:%M')
        max_teams = int(request.form['max_teams'])
        max_players = int(request.form['max_players'])
        entry_fee = float(request.form['entry_fee'])
        prize_pool = float(request.form['prize_pool'])
        registration_deadline = datetime.strptime(request.form['registration_deadline'], '%Y-%m-%dT%H:%M')
        bracket_type = request.form['bracket_type']
        
        tournament = Tournament(
            name=name,
            game=game,
            description=description,
            rules=rules,
            start_date=start_date,
            max_teams=max_teams,
            max_players=max_players,
            entry_fee=entry_fee,
            prize_pool=prize_pool,
            registration_deadline=registration_deadline,
            bracket_type=bracket_type,
            organizer_id=session['user_id'],
            status='upcoming'
        )
        
        db.session.add(tournament)
        db.session.commit()
        
        flash('Tournament created successfully!', 'success')
        return redirect(url_for('tournament_detail', tournament_id=tournament.id))
    
    return render_template('tournament/create.html', games=app.config['GAMES'])

@app.route('/tournament/<int:tournament_id>/register', methods=['POST'])
@token_required
def register_tournament(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    user_id = session['user_id']
    
    if not tournament.is_registration_open():
        flash('Registration is closed for this tournament', 'danger')
        return redirect(url_for('tournament_detail', tournament_id=tournament_id))
    
    # Check if tournament is full
    registered_count = tournament.get_registered_count()
    if registered_count >= tournament.max_teams:
        flash('Tournament is full', 'danger')
        return redirect(url_for('tournament_detail', tournament_id=tournament_id))
    
    if tournament.max_players == 1:
        # Solo registration
        existing_reg = TournamentRegistration.query.filter_by(
            tournament_id=tournament_id,
            player_id=user_id
        ).first()
        
        if existing_reg:
            flash('You are already registered for this tournament', 'warning')
            return redirect(url_for('tournament_detail', tournament_id=tournament_id))
        
        registration = TournamentRegistration(
            tournament_id=tournament_id,
            player_id=user_id,
            status='approved' if tournament.organizer_id == user_id else 'pending'
        )
        
        db.session.add(registration)
        flash('Registration submitted successfully!', 'success')
    
    else:
        # Team registration
        team_id = request.form.get('team_id')
        if not team_id:
            flash('Please select a team', 'danger')
            return redirect(url_for('tournament_detail', tournament_id=tournament_id))
        
        team = Team.query.get_or_404(team_id)
        
        # Check if user is team captain
        team_member = TeamMember.query.filter_by(
            team_id=team_id,
            user_id=user_id,
            role='captain'
        ).first()
        
        if not team_member:
            flash('Only team captain can register for tournaments', 'danger')
            return redirect(url_for('tournament_detail', tournament_id=tournament_id))
        
        existing_reg = TournamentRegistration.query.filter_by(
            tournament_id=tournament_id,
            team_id=team_id
        ).first()
        
        if existing_reg:
            flash('This team is already registered for this tournament', 'warning')
            return redirect(url_for('tournament_detail', tournament_id=tournament_id))
        
        registration = TournamentRegistration(
            tournament_id=tournament_id,
            team_id=team_id,
            status='approved' if tournament.organizer_id == user_id else 'pending'
        )
        
        db.session.add(registration)
        flash('Team registration submitted successfully!', 'success')
    
    db.session.commit()
    return redirect(url_for('tournament_detail', tournament_id=tournament_id))

@app.route('/tournament/<int:tournament_id>/bracket')
def tournament_bracket(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    matches = Match.query.filter_by(tournament_id=tournament_id)\
        .order_by(Match.round, Match.match_number).all()
    
    # Organize matches by round
    rounds = {}
    for match in matches:
        if match.round not in rounds:
            rounds[match.round] = []
        rounds[match.round].append(match)
    
    return render_template('tournament/bracket.html',
                         tournament=tournament,
                         rounds=rounds)

# Team Routes
@app.route('/teams')
def teams():
    game = request.args.get('game')
    
    query = Team.query.filter_by(is_active=True)
    if game and game != 'all':
        query = query.filter_by(game=game)
    
    teams = query.order_by(Team.created_at.desc()).all()
    return render_template('team/list.html', teams=teams, games=app.config['GAMES'])

@app.route('/team/create', methods=['GET', 'POST'])
@token_required
def create_team():
    if request.method == 'POST':
        name = request.form['name']
        tag = request.form['tag']
        game = request.form['game']
        description = request.form.get('description', '')
        
        if Team.query.filter_by(name=name).first():
            flash('Team name already exists', 'danger')
            return redirect(url_for('create_team'))
        
        if Team.query.filter_by(tag=tag).first():
            flash('Team tag already exists', 'danger')
            return redirect(url_for('create_team'))
        
        logo = None
        if 'logo' in request.files:
            file = request.files['logo']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(f"{name}_{datetime.now().timestamp()}.{file.filename.rsplit('.', 1)[1].lower()}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                logo = filename
        
        team = Team(
            name=name,
            tag=tag,
            game=game,
            description=description,
            logo=logo,
            created_by=session['user_id'],
            is_verified=False,
            is_active=True
        )
        
        db.session.add(team)
        db.session.commit()
        
        # Add creator as captain
        team_member = TeamMember(
            team_id=team.id,
            user_id=session['user_id'],
            role='captain'
        )
        db.session.add(team_member)
        db.session.commit()
        
        # Update user role if needed
        user = User.query.get(session['user_id'])
        if user.role == 'player':
            user.role = 'team_leader'
            db.session.commit()
        
        flash('Team created successfully!', 'success')
        return redirect(url_for('team_manage', team_id=team.id))
    
    return render_template('team/create.html', games=app.config['GAMES'])

@app.route('/team/<int:team_id>')
def team_view(team_id):
    team = Team.query.get_or_404(team_id)
    members = TeamMember.query.filter_by(team_id=team_id).all()
    registrations = TournamentRegistration.query.filter_by(team_id=team_id).all()
    
    return render_template('team/view.html',
                         team=team,
                         members=members,
                         registrations=registrations)

@app.route('/team/<int:team_id>/manage')
@token_required
def team_manage(team_id):
    team = Team.query.get_or_404(team_id)
    
    # Check if user is team captain or admin
    if team.created_by != session['user_id'] and session.get('role') != 'organizer':
        flash('You do not have permission to manage this team', 'danger')
        return redirect(url_for('dashboard'))
    
    members = TeamMember.query.filter_by(team_id=team_id).all()
    pending_invites = []  # You can implement invitation system here
    
    return render_template('team/manage.html',
                         team=team,
                         members=members,
                         pending_invites=pending_invites)

@app.route('/team/<int:team_id>/add_member', methods=['POST'])
@token_required
def add_team_member(team_id):
    team = Team.query.get_or_404(team_id)
    
    # Check if user is team captain
    if team.created_by != session['user_id']:
        flash('Only team captain can add members', 'danger')
        return redirect(url_for('team_manage', team_id=team_id))
    
    username = request.form['username']
    user = User.query.filter_by(username=username).first()
    
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('team_manage', team_id=team_id))
    
    # Check if already a member
    existing_member = TeamMember.query.filter_by(
        team_id=team_id,
        user_id=user.id
    ).first()
    
    if existing_member:
        flash('User is already a team member', 'warning')
        return redirect(url_for('team_manage', team_id=team_id))
    
    # Check team size (max 5 members for most esports)
    current_members = TeamMember.query.filter_by(team_id=team_id).count()
    if current_members >= 5:  # Adjust based on game
        flash('Team is full (max 5 members)', 'danger')
        return redirect(url_for('team_manage', team_id=team_id))
    
    team_member = TeamMember(
        team_id=team_id,
        user_id=user.id,
        role='member'
    )
    
    db.session.add(team_member)
    db.session.commit()
    
    flash(f'{username} added to team successfully!', 'success')
    return redirect(url_for('team_manage', team_id=team_id))

# Profile Routes
@app.route('/profile')
@token_required
def profile():
    user = User.query.get(session['user_id'])
    stats = user.get_stats()
    
    return render_template('profile/view.html', user=user, stats=stats)

@app.route('/profile/edit', methods=['GET', 'POST'])
@token_required
def edit_profile():
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        user.full_name = request.form.get('full_name')
        user.bio = request.form.get('bio')
        user.ign = request.form['ign']
        
        # Handle avatar upload
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(f"{user.username}_{datetime.now().timestamp()}.{file.filename.rsplit('.', 1)[1].lower()}")
                file.save(os.path.join('static/uploads', filename))
                user.avatar = filename
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('profile/edit.html', user=user)

# Admin Routes
@app.route('/admin')
@role_required(['organizer'])
def admin_panel():
    pending_registrations = TournamentRegistration.query.filter_by(status='pending').count()
    pending_teams = Team.query.filter_by(is_verified=False).count()
    total_users = User.query.count()
    active_tournaments = Tournament.query.filter_by(status='ongoing').count()
    total_tournaments = Tournament.query.count()
    
    stats = {
        'pending_registrations': pending_registrations,
        'pending_teams': pending_teams,
        'total_users': total_users,
        'active_tournaments': active_tournaments,
        'total_tournaments': total_tournaments
    }
    
    return render_template('admin/panel.html', stats=stats)

@app.route('/admin/users')
@role_required(['organizer'])
def admin_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/user/<int:user_id>/toggle')
@role_required(['organizer'])
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    
    action = "activated" if user.is_active else "deactivated"
    flash(f'User {user.username} has been {action}', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/teams')
@role_required(['organizer'])
def admin_teams():
    teams = Team.query.all()
    return render_template('admin/teams.html', teams=teams)

@app.route('/admin/team/<int:team_id>/toggle_verify')
@role_required(['organizer'])
def toggle_team_verify(team_id):
    team = Team.query.get_or_404(team_id)
    team.is_verified = not team.is_verified
    db.session.commit()
    
    action = "verified" if team.is_verified else "unverified"
    flash(f'Team {team.name} has been {action}', 'success')
    return redirect(url_for('admin_teams'))

@app.route('/admin/registrations')
@role_required(['organizer'])
def admin_registrations():
    registrations = TournamentRegistration.query.filter_by(status='pending').all()
    return render_template('admin/registrations.html', registrations=registrations)

@app.route('/admin/registration/<int:reg_id>/<action>')
@role_required(['organizer'])
def handle_registration(reg_id, action):
    registration = TournamentRegistration.query.get_or_404(reg_id)
    
    if action == 'approve':
        registration.status = 'approved'
        flash('Registration approved', 'success')
    elif action == 'reject':
        registration.status = 'rejected'
        flash('Registration rejected', 'success')
    
    db.session.commit()
    return redirect(url_for('admin_registrations'))

@app.route('/admin/announcements', methods=['GET', 'POST'])
@role_required(['organizer'])
def admin_announcements():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category = request.form['category']
        priority = int(request.form['priority'])
        
        announcement = Announcement(
            title=title,
            content=content,
            category=category,
            priority=priority,
            created_by=session['user_id'],
            created_at=datetime.utcnow()
        )
        
        db.session.add(announcement)
        db.session.commit()
        
        flash('Announcement created successfully!', 'success')
        return redirect(url_for('admin_announcements'))
    
    announcements = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return render_template('admin/announcements.html', announcements=announcements)

# API Routes
@app.route('/api/generate_bracket/<int:tournament_id>', methods=['POST'])
@role_required(['organizer'])
def api_generate_bracket(tournament_id):
    success = generate_bracket(tournament_id)
    if success:
        return jsonify({'success': True, 'message': 'Bracket generated successfully'})
    else:
        return jsonify({'success': False, 'message': 'Failed to generate bracket'}), 400

@app.route('/api/update_match/<int:match_id>', methods=['POST'])
@token_required
def api_update_match(match_id):
    match = Match.query.get_or_404(match_id)
    
    # Check permissions
    user_id = session['user_id']
    is_organizer = match.tournament_rel.organizer_id == user_id
    is_participant = False
    
    if match.tournament_rel.max_players == 1:
        is_participant = match.player1_id == user_id or match.player2_id == user_id
    else:
        user_teams = [tm.team_id for tm in TeamMember.query.filter_by(user_id=user_id).all()]
        is_participant = match.team1_id in user_teams or match.team2_id in user_teams
    
    if not (is_organizer or is_participant):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    data = request.json
    winner_type = data.get('winner_type')
    winner_id = data.get('winner_id')
    scores = data.get('scores', {})
    
    # Update match result
    if match.result:
        result = match.result
    else:
        result = MatchResult(match_id=match_id)
    
    if match.tournament_rel.max_players == 1:
        result.player1_score = scores.get('player1', 0)
        result.player2_score = scores.get('player2', 0)
        if winner_type == 'player':
            match.winner_player_id = winner_id
    else:
        result.team1_score = scores.get('team1', 0)
        result.team2_score = scores.get('team2', 0)
        if winner_type == 'team':
            match.winner_id = winner_id
    
    result.reported_by = user_id
    if is_organizer:
        result.verified_by = user_id
    
    match.status = 'completed'
    
    if not match.result:
        db.session.add(result)
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Match updated successfully'})

# Static file serving (supports avatars and team logos)
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    # First check the main uploads folder
    main_path = os.path.join('static', 'uploads', filename)
    if os.path.exists(main_path):
        return send_from_directory('static/uploads', filename)

    # Then check configured upload folder (e.g., team_logos subfolder)
    configured_folder = app.config.get('UPLOAD_FOLDER', 'static/uploads')
    configured_path = os.path.join(configured_folder, filename)
    if os.path.exists(configured_path):
        # send_from_directory expects the folder and the filename separately
        return send_from_directory(configured_folder, filename)

    # Not found
    abort(404)

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

# Initialize database (compatible with newer Flask versions)
def initialize_database():
    with app.app_context():
        db.create_all()
        # Create upload directories
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs('static/uploads', exist_ok=True)

# Run initialization at import time so setup scripts can use it too
initialize_database()

if __name__ == '__main__':
    import webbrowser
    import threading
    import time
    
    # Open browser after a short delay to ensure server is ready
    def open_browser():
        time.sleep(1)
        webbrowser.open('http://localhost:5000')
    
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    app.run(debug=True)