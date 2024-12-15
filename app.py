from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
import mysql.connector
from mysql.connector import Error
from marshmallow import Schema, fields, ValidationError, validate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
ma = Marshmallow(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Luna2794@localhost/fitness_center'
db = SQLAlchemy(app)

class Member(db.Model):
    __tablename__ = "Members"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    sessions = db.relationship('workout', backref='member')

class Workout(db.Model):
    __tablename__ = 'Workouts'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration = db.Column(db.Integer)
    calories_burned = db.Column(db.Integer)
    member_id = db.Column(db.Integer, db.ForeignKey('Members.id'))



class MemberSchema(ma.Schema):
    id = fields.Int(dump_only = True)
    name = fields.Str(required = True)
    age = fields.Int(required = True)

class WorkoutSchema(ma.Schema):
    id = fields.Int(dump_only = True)
    date = fields.Str(required = True)
    duration = fields.Int(required = True)
    calories_burned =  fields.Int(required = True)

member_schema = MemberSchema()
members_schema = MemberSchema(many = True)
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many = True)

#------------------------------------------------------------------------

@app.route('/members', methods = ["POST"])
def add_member():
    try:
        member = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_member = Member(name=member['name'], age=member['age'])
    db.session.add(new_member)
    db.session.commit()
    return jsonify({"message": "Member added"})

#------------------------------------------------------------------------------------

@app.route("/members/<int:id>", methods = ["PUT"])
def update_member(id):
    member = Member.query.get_or_404(id)
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    member.name = member_data['name']
    member.age = member_data['age']
    db.session.commit()
    return jsonify({"message": "Member updated"})

#---------------------------------------------------------------------------------

@app.route("/members", methods = ["GET"])
def get_members():
    members = Member.query.all()
    return members_schema.jsonify(members)

#------------------------------------------------------------------------------------------

@app.route("/members<int:id>", methods = ["DELETE"])
def delete_member(id):
    member = Member.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    return jsonify({"message": "Member deleted"})

#---------------------------------------------------------------------------

@app.route("/sessions", methods = ["POST"])
def add_workout():
    try:
        workout = workout_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_workout = Workout(date=workout['date'], duration=workout['duration'], calories_burned=workout['calories_burned'])
    db.session.add(new_workout)
    db.session.commit()
    return jsonify({"message": "Member added"})

#------------------------------------------------------------------------------------------------------------------------------------

@app.route("/sessions/<int:id>", methods = ["PUT"])
def update_workout(id):
    workout = Workout.query.get_or_404(id)
    try:
        workout_data = workout_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    workout.date = workout_data['date']
    workout.duration = workout_data['duration']
    workout.calories_burned = workout_data['calories_burned']
    db.session.commit()
    return jsonify({"message": "Member updated"})

#------------------------------------------------------------------------------------------------------------------

@app.route("/sessions", methods = ["GET"])
def get_workouts():
    workouts = Workout.query.all()
    return workouts_schema.jsonify(workouts)

#--------------------------------------------------------------------------------------------------

@app.route("/search_members", methods = ["GET"])
def search_members():
    name = request.args.get('name')
    member = Member.query.filter_by(name=name).first()
    if member:
        return member_schema.jsonify(member)
    else:
        return jsonify({"message": "Member not found"})


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)