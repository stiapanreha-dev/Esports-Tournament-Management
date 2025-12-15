#!/usr/bin/env python3
"""Seed database with sample data for testing."""

import os
import sys
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from app import app, db, User, Team, Tournament, Announcement

def seed_database():
    """Add sample data to the database."""
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        print("[INFO] Creating sample users...")
        
        # Admin user
        admin = User(
            username='admin',
            email='admin@esports.com',
            full_name='Admin User',
            password=generate_password_hash('admin123'),
            role='organizer',
            is_active=True
        )
        
        # Organizer users
        organizer1 = User(
            username='organizer1',
            email='organizer1@esports.com',
            full_name='John Organizer',
            password=generate_password_hash('password123'),
            role='organizer',
            is_active=True
        )
        
        # Team leaders
        leader1 = User(
            username='leader1',
            email='leader1@esports.com',
            full_name='Alice Team Lead',
            password=generate_password_hash('password123'),
            role='team_leader',
            is_active=True
        )
        
        leader2 = User(
            username='leader2',
            email='leader2@esports.com',
            full_name='Bob Team Lead',
            password=generate_password_hash('password123'),
            role='team_leader',
            is_active=True
        )
        
        # Players
        player1 = User(
            username='player1',
            email='player1@esports.com',
            full_name='Charlie Player',
            password=generate_password_hash('password123'),
            role='player',
            is_active=True
        )
        
        player2 = User(
            username='player2',
            email='player2@esports.com',
            full_name='Diana Player',
            password=generate_password_hash('password123'),
            role='player',
            is_active=True
        )
        
        player3 = User(
            username='player3',
            email='player3@esports.com',
            full_name='Eve Player',
            password=generate_password_hash('password123'),
            role='player',
            is_active=True
        )
        
        player4 = User(
            username='player4',
            email='player4@esports.com',
            full_name='Frank Player',
            password=generate_password_hash('password123'),
            role='player',
            is_active=True
        )
        
        db.session.add_all([admin, organizer1, leader1, leader2, player1, player2, player3, player4])
        db.session.commit()
        print("[OK] Created 8 users")
        
        print("[INFO] Creating sample teams...")
        
        # Teams
        team1 = Team(
            name='Phoenix Rising',
            tag='PHX',
            game='VALORANT',
            created_by=leader1.id,
            is_verified=True,
            description='Professional VALORANT team'
        )
        
        team2 = Team(
            name='Dragon Slayers',
            tag='DRAG',
            game='DOTA 2',
            created_by=leader2.id,
            is_verified=True,
            description='Competitive DOTA 2 squad'
        )
        
        team3 = Team(
            name='Cyber Ninjas',
            tag='CYN',
            game='Free Fire',
            created_by=leader1.id,
            is_verified=False,
            description='Free Fire grinding team'
        )
        
        db.session.add_all([team1, team2, team3])
        db.session.commit()
        print("[OK] Created 3 teams")
        
        print("[INFO] Creating sample tournaments...")
        
        # Tournaments
        tournament1 = Tournament(
            name='VALORANT Championship 2025',
            game='VALORANT',
            organizer_id=admin.id,
            description='Premier VALORANT tournament with prize pool of $10,000',
            status='ongoing',
            start_date=datetime.now() - timedelta(days=5),
            end_date=datetime.now() + timedelta(days=25),
            max_teams=16,
            rules='Standard 5v5 matches, bo3 format',
            prize_pool=10000
        )
        
        tournament2 = Tournament(
            name='DOTA 2 Winter Cup',
            game='DOTA 2',
            organizer_id=organizer1.id,
            description='Amateur DOTA 2 tournament for aspiring teams',
            status='upcoming',
            start_date=datetime.now() + timedelta(days=10),
            end_date=datetime.now() + timedelta(days=35),
            max_teams=8,
            rules='5v5 matches, standard rules apply',
            prize_pool=5000
        )
        
        tournament3 = Tournament(
            name='Free Fire Royale Battle',
            game='Free Fire',
            organizer_id=admin.id,
            description='Large-scale Free Fire tournament',
            status='upcoming',
            start_date=datetime.now() + timedelta(days=2),
            end_date=datetime.now() + timedelta(days=30),
            max_teams=32,
            rules='Battle Royale mode, squad of 4',
            prize_pool=3000
        )
        
        tournament4 = Tournament(
            name='PUBG Mobile Invitational',
            game='PUBG Mobile',
            organizer_id=organizer1.id,
            description='Invitational PUBG Mobile tournament',
            status='completed',
            start_date=datetime.now() - timedelta(days=30),
            end_date=datetime.now() - timedelta(days=5),
            max_teams=16,
            rules='10 matches with points system',
            prize_pool=8000
        )
        
        db.session.add_all([tournament1, tournament2, tournament3, tournament4])
        db.session.commit()
        print("[OK] Created 4 tournaments")
        
        print("[INFO] Creating sample announcements...")
        
        # Announcements
        announcement1 = Announcement(
            title='New Tournament: VALORANT Championship 2025',
            content='We are proud to announce the start of VALORANT Championship 2025. Register your team now!',
            created_by=admin.id,
            category='tournament',
            priority=2,
            expires_at=datetime.now() + timedelta(days=30)
        )
        
        announcement2 = Announcement(
            title='Maintenance Scheduled for Tomorrow',
            content='The platform will undergo maintenance from 2 AM to 4 AM UTC. Please save your progress.',
            created_by=admin.id,
            category='announcement',
            priority=3,
            expires_at=datetime.now() + timedelta(days=1)
        )
        
        announcement3 = Announcement(
            title='Referral Program Launched',
            content='Invite friends and earn bonus credits! Refer 3 friends to get 500 bonus credits.',
            created_by=organizer1.id,
            category='promotion',
            priority=1,
            expires_at=datetime.now() + timedelta(days=60)
        )
        
        db.session.add_all([announcement1, announcement2, announcement3])
        db.session.commit()
        print("[OK] Created 3 announcements")
        
        print("\n[OK] Database seeding completed successfully!")
        print("\n[INFO] Sample credentials:")
        print("   Admin: admin / admin123")
        print("   Organizer: organizer1 / password123")
        print("   Team Leader: leader1 / password123")
        print("   Player: player1 / password123")

if __name__ == '__main__':
    seed_database()
