import os
import json
from flask import Flask, session, redirect, url_for

def create_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(24)
    
    # Configure upload folder
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    app.config['TEMPLATES_FOLDER'] = os.path.join(app.root_path, 'static', 'templates')
    app.config['OUTPUT_FOLDER'] = os.path.join(app.root_path, 'static', 'output')
    app.config['ACTIVITIES_FOLDER'] = os.path.join(app.root_path, 'static', 'activities')
    
    # Ensure folders exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['TEMPLATES_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    os.makedirs(app.config['ACTIVITIES_FOLDER'], exist_ok=True)
    
    # Import blueprints
    from src.routes.lessons import lessons_bp
    
    # Register blueprints
    app.register_blueprint(lessons_bp, url_prefix='/lessons')
    
    # Add root route
    @app.route('/')
    def index():
        return redirect(url_for('lessons.index'))
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
