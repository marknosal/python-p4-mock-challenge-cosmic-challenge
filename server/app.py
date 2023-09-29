#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route('/')
def home():
    return make_response({'message': 'Welcome Home!'}, 200)

class Scientists(Resource):
    def get(self):
        scientists = [sci.to_dict(rules=('-missions',)) for sci in Scientist.query.all()]
        if scientists:
            return make_response(scientists, 200)
        return make_response({'error': 'There are no scientists!'}, 404)

    def post(self):
        request_json = request.get_json()
        try:
            new_scientist = Scientist(
                name = request_json['name'],
                field_of_study = request_json['field_of_study']
            )
            db.session.add(new_scientist)
            db.session.commit()
            return make_response(new_scientist.to_dict(), 201)
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)

api.add_resource(Scientists, '/scientists')

class ScientistById(Resource):
    def get(self, id):
        scientist = Scientist.query.filter_by(id=id).one_or_none()
        if scientist:
            return scientist.to_dict(), 200
        return {"error": "Scientist not found"}, 404
    def patch(self, id):
        scientist = Scientist.query.filter_by(id=id).one_or_none()
        if not scientist:
            return {"error": "Scientist not found"}, 404
        fields = request.get_json()
        try:
            for field in fields:
                setattr(scientist, field, fields[field])
            db.session.add(scientist)
            db.session.commit()
            return make_response(scientist.to_dict(), 202)
        except ValueError:
            return {"errors": ["validation errors"]}, 400
        
    def delete(self, id):
        scientist = Scientist.query.filter(Scientist.id == id).first()
        if not scientist:
            return make_response({"error": "Scientist not found"}, 404)
        db.session.delete(scientist)
        db.session.commit()
        return make_response({}, 204)

api.add_resource(ScientistById, '/scientists/<int:id>')


class Planets(Resource):
    def get(self):
        planets = [planet.to_dict(rules=('-missions',)) for planet in Planet.query.all()]
        if planets:
            return make_response(planets, 200)
        return {'error': 'There are no planets!!'}, 404
    def post(self):
        fields = request.get_json()
        try:
            new_planet = Planet()
            for field in fields:
                setattr(new_planet, field, fields[field])
            db.session.add(new_planet)
            db.commit()
            return make_response(new_planet.to_dict(rules=('-missions',)), 201)
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)

api.add_resource(Planets, '/planets')


class Missions(Resource):
    def get(self):
        missions = [mission.to_dict(rules=('-scientist', '-planet',)) for mission in Mission.query.all()]
        if not missions:
            return {'error': 'There are no missions!'}, 404
        return missions, 200

    def post(self):
        fields = request.get_json()
        try:
            # new_mission = Mission(
            #     name=fields['name'],
            #     scientist_id=fields['scientist_id'],
            #     planet_id=fields['planet_id']
            # )
            new_mission = Mission()
            for field in fields:
                setattr(new_mission, field, fields[field])
            db.session.add(new_mission)
            db.session.commit()
            return make_response(new_mission.to_dict(), 201)
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)

api.add_resource(Missions, '/missions')



if __name__ == '__main__':
    app.run(port=5555, debug=True)
