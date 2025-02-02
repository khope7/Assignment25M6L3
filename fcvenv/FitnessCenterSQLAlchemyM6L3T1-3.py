# Task 1: Setting Up Flask with Flask-SQLAlchemy - Initialize a new Flask project and set up a virtual environment. - Install Flask, Flask-SQLAlchemy, and Flask-Marshmallow.
# - Configure Flask-SQLAlchemy to connect to your database. - Define `Members` and `WorkoutSessions` models using Flask-SQLAlchemy ORM.

# Task 2: Implementing CRUD Operations for Members Using ORM - Create Flask routes to add, retrieve, update, and delete members using the ORM models.
# - Apply HTTP methods: POST to add, GET to retrieve, PUT to update, and DELETE to delete members. - Handle errors effectively and return appropriate JSON responses.

# Task 3: Managing Workout Sessions with ORM - Develop routes to schedule, update, and view workout sessions using SQLAlchemy.
# Implement a route to retrieve all workout sessions for a specific member.


#Writing code for M6L3T1-2
 
#Initializing imports from pip installs
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields
from marshmallow import ValidationError

#Initializing database call
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:CodingTemple.1@localhost/workout_session_db'
db = SQLAlchemy(app)
ma = Marshmallow(app)

#Creating Members and Sessions Schemas along with fields
class MemberSchema(ma.Schema):
    name = fields.String(required=True)
    age = fields.String(required=True)

    class Meta:
        fields = ("name", "age", "id")    


class SessionSchema(ma.Schema):
    member_id = fields.Integer(required=True)
    session_date = fields.Date(required=True)
    duration_minutes = fields.Integer(required=True)
    calories_burned = fields.Integer(required=True)

    class Meta:
        fields = ("session_id", "member_id", "session_date", "duration_minutes", "calories_burned")    


#Creating schemas for single and multiple record pulls
member_schema = MemberSchema()
members_schema = MemberSchema(many=True)
session_schema = SessionSchema()
sessions_schema = SessionSchema(many=True)

#Creating Member and Session Models
class Member(db.Model):
    __tablename__ = 'members'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    sessions = db.relationship('Session', backref='member')

class Session(db.Model):
    __tablename__ = 'workoutsessions'
    session_id = db.Column(db.Integer, primary_key=True)
    session_date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    calories_burned = db.Column(db.Integer, nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'))

#Creating CRUD methods for members Table
@app.route('/members', methods=['GET'])
def get_members():
    members = Member.query.all()
    return members_schema.jsonify(members)

@app.route('/members', methods=['POST'])
def add_member():
    try:
# Validate and deserialize input
        member_data = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_member = Member(name=member_data['name'], age=member_data['age'])
    db.session.add(new_member)
    db.session.commit()
    return jsonify({"message": "New member added succesfully"}), 201

@app.route('/members/<int:id>', methods=['PUT'])
def update_member(id):
    member = Member.query.get_or_404(id)
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages),400
    
    member.name = member_data['name']
    member.age = member_data['age']
    db.session.commit()
    return jsonify({"message": "Member details updated successfully"}), 200

@app.route('/members/<int:id>', methods=['DELETE'])
def delete_member(id):
    member = Member.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    return jsonify({"message": "Member removed successfully"}), 200


#Writing code for M6L3T3

#Creating Crud Methods for workoutsessions Table
@app.route('/workoutsessions', methods=['GET'])
def get_workoutsessions():
    workoutsessions = Session.query.all()
    return sessions_schema.jsonify(workoutsessions)

@app.route('/workoutsessions', methods=['POST'])
def add_session():
    try:
# Validate and deserialize input
        session_data = session_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_session = Session(member_id=session_data['member_id'], session_date=session_data['session_date'], duration_minutes=session_data['duration_minutes'], calories_burned=session_data['calories_burned'])
    db.session.add(new_session)
    db.session.commit()
    return jsonify({"message": "New session added succesfully"}), 201

@app.route('/workoutsessions/<int:member_id>', methods=['PUT'])
def update_session(member_id):
    session = Session.query.get_or_404(member_id)
    try:
        session_data = session_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages),400
    
    session.member_id = session_data['member_id']
    session.session_date = session_data['session_date']
    session.duration_minutes = session_data['duration_minutes']
    session.calories_burned = session_data['calories_burned']
    db.session.commit()
    return jsonify({"message": "Session details updated successfully"}), 200

@app.route('/workoutsessions/<int:member_id>', methods=['DELETE'])
def delete_session(member_id):
    session = Session.query.get_or_404(member_id)
    db.session.delete(session)
    db.session.commit()
    return jsonify({"message": "Session removed successfully"}), 200

#Creating GET methods to find specific members in members Table and to query all sessions based on FK member_id referencing id from members Table
@app.route('/members/by-id', methods = ['GET'])
def query_member_by_id():
    id = request.args.get('id')
    member = Member.query.filter_by(id=id).first()
    if member:
        return member_schema.jsonify(member)
    else:
        return jsonify({"message" : "Customer not found."})
    
@app.route('/workoutsessions/by-member_id', methods = ['GET'])
def query_workoutsessions_by_member_id():
    member_id = request.args.get('member_id')
    sessions = Session.query.filter(Session.member_id==member_id)
    if sessions:
        return sessions_schema.jsonify(sessions)
    else:
        return jsonify({'message' : 'Product not found'}), 404


#Initializing the database and creating tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug = True)