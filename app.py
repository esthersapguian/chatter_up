from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'your_secret_key' #chatup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chatterup.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Thread(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Initialize the database
@app.before_first_request
def create_tables():
    db.create_all()

# Routes
@app.route('/')
def home():
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists!')
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! You can log in now.')
            return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect('/search')
        else:
            flash('Invalid credentials!')
    return render_template('login.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if 'user_id' not in session:
        return redirect('/login')
    users = []
    if request.method == 'POST':
        search_query = request.form['search']
        users = User.query.filter(User.username.like(f"%{search_query}%")).all()
    return render_template('search.html', users=users)

@app.route('/chat/<int:receiver_id>', methods=['GET', 'POST'])
def chat(receiver_id):
    if 'user_id' not in session:
        return redirect('/login')
    current_user_id = session['user_id']
    receiver = User.query.get(receiver_id)

    if not receiver:
        flash("User not found!")
        return redirect('/search')

    if request.method == 'POST':
        message_text = request.form['message']
        new_message = Message(
            sender_id=current_user_id,
            receiver_id=receiver_id,
            text=message_text
        )
        db.session.add(new_message)
        db.session.commit()

    # Retrieve messages between the two users
    messages = Message.query.filter(
        ((Message.sender_id == current_user_id) & (Message.receiver_id == receiver_id)) |
        ((Message.sender_id == receiver_id) & (Message.receiver_id == current_user_id))
    ).order_by(Message.timestamp).all()

    return render_template('chat.html', messages=messages, current_user_id=current_user_id, receiver=receiver)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# Initialize the database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
