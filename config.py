import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///instance/tournament.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'static/uploads/team_logos'
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB max file size
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # Steam
    STEAM_API_KEY = os.environ.get('STEAM_API_KEY', '')

    # Game options
    GAMES = ['Free Fire', 'BGMI', 'Valorant', 'COD Mobile', 'PUBG PC', 'CS:GO', 'Dota 2', 'League of Legends']
    
    # Tournament types
    TOURNAMENT_TYPES = ['solo', 'team']
    
    # Bracket types
    BRACKET_TYPES = ['single_elimination', 'double_elimination', 'round_robin']