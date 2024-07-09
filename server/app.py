#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
#app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"
#restaurants
class Restaurants(Resource):
    def get(self):
        restautants = [restaurant.to_dict() for restaurant in Restaurant.query.all()]
        return make_response(jsonify(restautants), 200)
    
#restaurant by id
class ReastaurantById(Resource):
    def get(self, id):
        restaurant = Restaurant.query.filter_by(id = id).first()
        if restaurant:
            return make_response(jsonify(restaurant.to_dict()), 200)
        else:
            return make_response(jsonify({"error": "Restaurant not found"}), 404)
        
    def delete(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            response_dict = {"message": "Record successfully deleted"}
            return make_response(jsonify(response_dict), 204)
        else:
            return make_response(jsonify({"error": "Restaurant not found"}), 404)

class Pizzas(Resource):
    def get(self):
        pizzas = [pizza.to_dict() for pizza in Pizza.query.all()]
        return make_response(jsonify(pizzas), 200)

class RestaurantPizzas(Resource):
   def post(self):
        try:
            data = request.get_json()

            price = data.get('price')
            pizza_id = data.get('pizza_id')
            restaurant_id = data.get('restaurant_id')

            if not (price and pizza_id and restaurant_id):
                return make_response(jsonify({"errors": ["validation errors"]}), 400)
            
            pizza = Pizza.query.filter_by(id=pizza_id).first()
            restaurant = Restaurant.query.filter_by(id=restaurant_id).first()
            
            if not (pizza and restaurant):
                return make_response(jsonify({"errors": "validation errors"}), 400)

            if not (isinstance(price, (int, float)) and 1 <= price <= 30):
                return make_response(jsonify({"errors":["validation errors"]}), 400)

            new_restaurant_pizza_item = RestaurantPizza(
                price=price,
                pizza_id=pizza_id,
                restaurant_id=restaurant_id,
            )

            db.session.add(new_restaurant_pizza_item)
            db.session.commit()

            response_data = {
                "id": new_restaurant_pizza_item.id,
                "pizza": {
                    "id": pizza.id,
                    "ingredients": pizza.ingredients,
                    "name": pizza.name, 
                },
                "pizza_id": pizza.id,
                "price": new_restaurant_pizza_item.price,
                "restaurant": {
                    "address": restaurant.address,
                    "id": restaurant.id,
                    "name": restaurant.name, 
                },
                "restaurant_id": restaurant.id
            }

            return make_response(jsonify(response_data), 201)

        except Exception as e:
            return make_response(jsonify({"errors": [str(e)]}), 400)
api.add_resource(Restaurants, "/restaurants")        
api.add_resource(ReastaurantById, "/restaurants/<int:id>")
api.add_resource(Pizzas, "/pizzas") 
api.add_resource(RestaurantPizzas, "/restaurant_pizzas")

@app.errorhandler(404)
def not_found_error(error):
    return make_response(jsonify({"error": "Not Found"}), 404)

@app.errorhandler(400)
def bad_request_error(error):
    return jsonify({'error': 'Bad Request'}), 400


if __name__ == "__main__":
    app.run(port=5555, debug=True)
