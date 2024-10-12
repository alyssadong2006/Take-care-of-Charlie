from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pet.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Pet model
class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hunger = db.Column(db.Integer, default=50)
    happiness = db.Column(db.Integer, default=50)
    health = db.Column(db.Integer, default=100)

@app.route('/get_stats', methods=['GET'])
def get_stats():
    pet = Pet.query.first()
    if pet:
        return jsonify({
            'hunger': pet.hunger,
            'happiness': pet.happiness,
            'health': pet.health
        })
    return jsonify({'error': 'No pet found'}), 404

# Initialize the database
with app.app_context():
    db.create_all()

# Function to decrease pet stats
def decrease_stats():
    with app.app_context():
        pet = Pet.query.first()
        if pet:
            pet.hunger = min(pet.hunger + 5, 100)
            pet.happiness = max(pet.happiness - 5, 0)
            pet.health = max(pet.health - 5, 0)
            db.session.commit()

# Schedule the stat decrease every 30 seconds
scheduler = BackgroundScheduler(timezone=utc)
scheduler.add_job(func=decrease_stats, trigger="interval", seconds=30)
scheduler.start()

# Home route
@app.route('/')
def index():
    pet = Pet.query.first()
    if not pet:
        pet = Pet(hunger=50, happiness=50, health=100)
        db.session.add(pet)
        db.session.commit()
    return render_template('index.html', pet=pet)

# API routes to update pet stats
@app.route('/feed', methods=['POST'])
def feed():
    pet = Pet.query.first()
    pet.hunger = max(pet.hunger - 20, 0)
    db.session.commit()
    return jsonify({'hunger': pet.hunger, 'happiness': pet.happiness, 'health': pet.health})

@app.route('/play', methods=['POST'])
def play():
    pet = Pet.query.first()
    pet.happiness = min(pet.happiness + 10, 100)
    db.session.commit()
    return jsonify({'hunger': pet.hunger, 'happiness': pet.happiness, 'health': pet.health})

@app.route('/clean', methods=['POST'])
def clean():
    pet = Pet.query.first()
    pet.health = min(pet.health + 10, 100)
    db.session.commit()
    return jsonify({'hunger': pet.hunger, 'happiness': pet.happiness, 'health': pet.health})

if __name__ == '__main__':
    app.run(debug=True)