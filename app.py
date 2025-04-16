from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Progress, QuizScore, Visitor
from dotenv import load_dotenv
import os
import json
import re
from datetime import datetime
import openai
from openai import OpenAI

load_dotenv() 

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///python_tutor.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create database tables if they don't exist
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password_hash, request.form['password']):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.form['password'] != request.form['confirm_password']:
            flash('Passwords do not match')
            return redirect(url_for('register'))
            
        if User.query.filter_by(username=request.form['username']).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        if User.query.filter_by(email=request.form['email']).first():
            flash('Email already registered')
            return redirect(url_for('register'))
        
        user = User(
            username=request.form['username'],
            email=request.form['email'],
            password_hash=generate_password_hash(request.form['password'])
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/api/gpt-python', methods=['POST'])
def ask_gpt():
    try:
        app.logger.debug("Starting ask_gpt function")
        api_key = os.getenv('OPENAI_API_KEY')
        app.logger.debug(f"API key present: {bool(api_key)}")
        
        if not api_key:
            app.logger.error("OpenAI API key is not configured")
            return jsonify({"error": "OpenAI API key is not configured"}), 500
            
        data = request.get_json()
        app.logger.debug(f"Received data: {data}")
        
        if not data:
            app.logger.error("No data provided")
            return jsonify({"error": "No data provided"}), 400
            
        prompt = data.get('question') or data.get('prompt')
        if not prompt:
            app.logger.error("No question or prompt provided")
            return jsonify({"error": "No question or prompt provided"}), 400

        app.logger.debug("Making OpenAI API call")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful Python programming tutor."},
                {"role": "user", "content": prompt}
            ]
        )
        app.logger.debug("OpenAI API call successful")

        answer = response.choices[0].message.content
        return jsonify({"response": answer})
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        app.logger.error(f"Error in ask_gpt: {str(e)}\n{tb}")
        return jsonify({"error": f"{str(e)}", "traceback": tb}), 500

@app.route('/api/progress', methods=['POST'])
@login_required
def update_progress():
    data = request.get_json()
    lesson_id = data.get('lesson_id')
    completed = data.get('completed', False)
    
    progress = Progress.query.filter_by(
        user_id=current_user.id,
        lesson_id=lesson_id
    ).first()
    
    if not progress:
        progress = Progress(
            user_id=current_user.id,
            lesson_id=lesson_id,
            completed=completed
        )
        db.session.add(progress)
    else:
        progress.completed = completed
        if completed:
            progress.completed_at = datetime.utcnow()
    
    db.session.commit()
    return jsonify({"success": True})

@app.route('/api/quiz-score', methods=['POST'])
@login_required
def save_quiz_score():
    data = request.get_json()
    lesson_id = data.get('lesson_id')
    score = data.get('score')
    total_questions = data.get('total_questions')
    
    quiz_score = QuizScore(
        user_id=current_user.id,
        lesson_id=lesson_id,
        score=score,
        total_questions=total_questions
    )
    
    db.session.add(quiz_score)
    db.session.commit()
    return jsonify({"success": True})

@app.route('/track-visitor', methods=['POST'])
def track_visitor():
    data = request.get_json()
    page = data.get('page_visited', 'unknown')
    visitor = Visitor(
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string,
        page_visited=page,
        is_logged_in=current_user.is_authenticated,
        user_id=current_user.id if current_user.is_authenticated else None
    )
    db.session.add(visitor)
    db.session.commit()
    return '', 204

@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    users = User.query.all()
    visitors = Visitor.query.order_by(Visitor.visited_at.desc()).limit(100).all()
    visitor_stats = {
        'total': Visitor.query.count(),
        'unique_ips': db.session.query(db.func.count(db.distinct(Visitor.ip_address))).scalar(),
        'logged_in': Visitor.query.filter_by(is_logged_in=True).count(),
        'today': Visitor.query.filter(
            Visitor.visited_at >= datetime.utcnow().date()
        ).count()
    }
    return render_template('admin_users.html', users=users, visitors=visitors, stats=visitor_stats)

# Function to set a user as admin (can be called from a command line or admin interface)
def set_admin_user(email):
    user = User.query.filter_by(email=email).first()
    if user:
        user.is_admin = True
        db.session.commit()
        return True
    return False

if __name__ == '__main__':
    # For local development
    app.run(debug=True)
