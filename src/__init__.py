from flask import Flask
from .config.settings import Config

def create_app():
    """Application factory function"""
    app = Flask(__name__)
    app.secret_key = 'academic_portal_secret_key_2025'  # Change this in production
    
    # Initialize configuration
    Config.init_app(app)
    
    # Register template filters
    from .utils.template_filters import register_filters
    register_filters(app)
    
    # Register blueprints
    from .controllers.main_controller import main_bp
    from .controllers.admin_controller import admin_bp
    from .controllers.api_controller import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
    
    return app