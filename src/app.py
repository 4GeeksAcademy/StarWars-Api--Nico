"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, Character, Favorites
#from models import Person


app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

#-----------------USER-------------------#

@app.route('/user', methods=['GET'])
def get_users():
    user = User.query.all()
    all_users = list(map(lambda p : p.serialize(), user))
   

    return jsonify(all_users), 200

@app.route('/user/<int:user_id>', methods=['GET'])
def get_one_person(user_id):
    user = User.query.get(user_id)
   

    return jsonify(user.serialize()), 200

@app.route('/user', methods=['POST'])
def post_user():
    request_body = request.get_json()
    new_user = User(
        email= request_body["email"],
        name= request_body["name"],
        password= request_body["password"],
        first_name= request_body["first_name"],
        last_name= request_body["last_name"]
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.serialize()), 200

@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"message": "User not found"}), 404
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"}), 200

#-----------------------PLANETS--------------------------#

@app.route('/planet', methods=['POST'])
def post_planet():
    request_body = request.get_json()
    if request_body["climate"] not in ("arid", "temperate", "tropical", "frozen", "murky"):
        return "Climate must be arid, temperate, tropical, froze or murky", 400
    new_planet = Planet(

        name= request_body["name"],
        population= request_body["population"],
        climate= request_body["climate"]

    )
    db.session.add(new_planet)
    db.session.commit()
    return jsonify(new_planet.serialize()), 200

@app.route('/planet', methods=['GET'])
def get_planets():
    planet = Planet.query.all()
    all_planets = list(map(lambda p : p.serialize(), planet))

    return jsonify(all_planets), 200

@app.route('/planet/<int:planet_id>', methods=['GET'])
def get_one_planet(planet_id):
    planet = Planet.query.get(planet_id)
   
    return jsonify(planet.serialize()), 200

@app.route('/planet/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"message": "Planet not found"}), 404
    
    db.session.delete(planet)
    db.session.commit()
    return jsonify({"message": "Planet deleted"}), 200

#-------------------CHARACTERS----------------------#

@app.route('/character', methods=['POST'])
def post_character():
    request_body = request.get_json()
    
    new_character = Character(

        name= request_body["name"],
        gender= request_body["gender"],
        birth_year= request_body["birth_year"]

    )
    db.session.add(new_character)
    db.session.commit()
    return jsonify(new_character.serialize()), 200

@app.route('/character', methods=['GET'])
def get_characters():
    character = Character.query.all()
    all_characters = list(map(lambda p : p.serialize(), character))

    return jsonify(all_characters), 200

@app.route('/character/<int:character_id>', methods=['GET'])
def get_one_character(character_id):
    character = Character.query.get(character_id)
   
    return jsonify(character.serialize()), 200

@app.route('/character/<int:character_id>', methods=['DELETE'])
def delete_character(character_id):
    character = Character.query.get(character_id)
    if character is None:
        return jsonify({"message": "Character not found"}), 404
    
    db.session.delete(character)
    db.session.commit()
    return jsonify({"message": "Character deleted"}), 200

#---------------------FAVORITES----------------------#

@app.route('/favorite/planet/<int:planet_id_>', methods=['POST'])
def post_favorite_planet(planet_id_):
    request_body = request.get_json()
    
    new_favorite = Favorites(

        user_id= request_body["user_id"],
        planet_id= planet_id_

    )
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify(new_favorite.serialize()), 200

@app.route('/favorite/character/<int:character_id_>', methods=['POST'])
def post_favorite_character(character_id_):
    request_body = request.get_json()
    
    new_favorite = Favorites(

        user_id= request_body["user_id"],
        character_id= character_id_

    )
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify(new_favorite.serialize()), 200


@app.route('/favorite/<int:favorite_id>', methods=['DELETE'])
def delete_favorite(favorite_id):
    favorite = Favorites.query.get(favorite_id)
    if favorite is None:
        return jsonify({"message": "Favorite not found"}), 404
    
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"message": "Favorite deleted"}), 200

@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_favorite(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    
    favorites = [favorite.serialize() for favorite in user.favorites]
    return jsonify(favorites), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)