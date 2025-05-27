from flask import Blueprint, render_template, request, jsonify, current_app, flash, redirect, url_for, send_from_directory
import os
import uuid
from werkzeug.utils import secure_filename
from src.services.file_processor import FileProcessor
from src.services.pptx_generator import PPTXGenerator
from src.services.activity_generator import ActivityGenerator

# Create blueprint
lessons_bp = Blueprint('lessons', __name__)

# Configure upload folder
UPLOAD_FOLDER = os.path.join(current_app.root_path, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configure output folders
TEMPLATES_FOLDER = os.path.join(current_app.root_path, 'static', 'templates')
OUTPUT_FOLDER = os.path.join(current_app.root_path, 'static', 'output')
ACTIVITIES_FOLDER = os.path.join(current_app.root_path, 'static', 'activities')

# Ensure output folders exist
os.makedirs(TEMPLATES_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(ACTIVITIES_FOLDER, exist_ok=True)

# Initialize services
file_processor = FileProcessor(UPLOAD_FOLDER)
pptx_generator = PPTXGenerator(TEMPLATES_FOLDER, OUTPUT_FOLDER)
activity_generator = ActivityGenerator(ACTIVITIES_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@lessons_bp.route('/')
def index():
    """Render the lessons dashboard"""
    return render_template('lessons/index.html')

@lessons_bp.route('/create', methods=['GET', 'POST'])
def create_lesson():
    """Create a new lesson"""
    if request.method == 'POST':
        # Check if a file was uploaded
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        
        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # Generate a unique filename
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            
            # Save the file
            file.save(file_path)
            
            # Process the file
            try:
                content = file_processor.process_file(file_path)
                
                # Store content in session for later use
                session_id = str(uuid.uuid4())
                session_file = os.path.join(OUTPUT_FOLDER, f"{session_id}.json")
                with open(session_file, 'w', encoding='utf-8') as f:
                    json.dump(content, f, ensure_ascii=False, indent=2)
                
                # Redirect to customize page
                return redirect(url_for('lessons.customize_lesson', session_id=session_id))
            
            except Exception as e:
                flash(f'Error processing file: {str(e)}')
                return redirect(request.url)
        
        else:
            flash('File type not allowed')
            return redirect(request.url)
    
    # GET request - render the create lesson form
    return render_template('lessons/create.html')

@lessons_bp.route('/customize/<session_id>', methods=['GET', 'POST'])
def customize_lesson(session_id):
    """Customize a lesson"""
    # Load content from session file
    session_file = os.path.join(OUTPUT_FOLDER, f"{session_id}.json")
    
    if not os.path.exists(session_file):
        flash('Session not found')
        return redirect(url_for('lessons.create_lesson'))
    
    with open(session_file, 'r', encoding='utf-8') as f:
        content = json.load(f)
    
    if request.method == 'POST':
        # Get customization options
        template_name = request.form.get('template', 'default')
        color_scheme = request.form.get('color_scheme', 'default')
        output_filename = request.form.get('output_filename', 'presentation')
        
        # Generate presentation
        try:
            pptx_path = pptx_generator.generate_presentation(
                content, 
                template_name=template_name,
                color_scheme=color_scheme,
                output_filename=output_filename
            )
            
            # Generate activities if requested
            activities = []
            
            if 'generate_kahoot' in request.form:
                kahoot_path = activity_generator.generate_kahoot_activities(
                    content,
                    activity_name=f"kahoot_{output_filename}"
                )
                activities.append({
                    'type': 'kahoot',
                    'path': os.path.basename(kahoot_path)
                })
            
            if 'generate_nearpod' in request.form:
                nearpod_path = activity_generator.generate_nearpod_activities(
                    content,
                    activity_name=f"nearpod_{output_filename}"
                )
                activities.append({
                    'type': 'nearpod',
                    'path': os.path.basename(nearpod_path)
                })
            
            # Redirect to download page
            return redirect(url_for(
                'lessons.download_lesson',
                pptx_file=os.path.basename(pptx_path),
                activities=','.join([a['type'] + ':' + a['path'] for a in activities])
            ))
        
        except Exception as e:
            flash(f'Error generating presentation: {str(e)}')
            return redirect(request.url)
    
    # GET request - render the customize form
    return render_template(
        'lessons/customize.html',
        content=content,
        session_id=session_id
    )

@lessons_bp.route('/download')
def download_lesson():
    """Download generated files"""
    pptx_file = request.args.get('pptx_file')
    activities_param = request.args.get('activities', '')
    
    activities = []
    if activities_param:
        for activity_info in activities_param.split(','):
            parts = activity_info.split(':')
            if len(parts) == 2:
                activities.append({
                    'type': parts[0],
                    'path': parts[1]
                })
    
    return render_template(
        'lessons/download.html',
        pptx_file=pptx_file,
        activities=activities
    )

@lessons_bp.route('/download/<path:filename>')
def download_file(filename):
    """Download a file"""
    directory = OUTPUT_FOLDER
    
    # Check if file is an activity
    if filename.startswith('kahoot_') or filename.startswith('nearpod_'):
        directory = ACTIVITIES_FOLDER
    
    return send_from_directory(directory, filename, as_attachment=True)
