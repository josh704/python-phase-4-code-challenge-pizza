#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
from sqlalchemy.orm import Session
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

class GetRestaurants(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return [restaurant.to_dict(only=('id', 'name', 'address')) for restaurant in restaurants]

api.add_resource(GetRestaurants, '/restaurants')

class RestaurantDetail(Resource):
    def get(self, id):
        with Session(db.engine) as session:
            restaurant = session.get(Restaurant, id)
            if restaurant:
                return restaurant.to_dict(only=('id', 'name', 'address', 'restaurant_pizzas'))
            else:
                return {"error": "Restaurant not found"}, 404

    def delete(self, id):
        with Session(db.engine) as session:
            restaurant = session.get(Restaurant, id)
            if restaurant:
                session.delete(restaurant)
                session.commit()
                return '', 204
            else:
                return {"error": "Restaurant not found"}, 404

api.add_resource(RestaurantDetail, '/restaurants/<int:id>')


class GetPizzas(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return [pizza.to_dict(only=('id', 'name', 'ingredients')) for pizza in pizzas]

api.add_resource(GetPizzas, '/pizzas')

@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()
    try:
        restaurant_pizza = RestaurantPizza(
            price=data['price'],
            pizza_id=data['pizza_id'],
            restaurant_id=data['restaurant_id']
        )
        db.session.add(restaurant_pizza)
        db.session.commit()
        
        response = restaurant_pizza.to_dict()
        response['pizza'] = restaurant_pizza.pizza.to_dict(only=('id', 'name', 'ingredients'))
        response['restaurant'] = restaurant_pizza.restaurant.to_dict(only=('id', 'name', 'address'))
        
        return make_response(response, 201)
    except ValueError as e:
        return make_response({"errors": ["validation errors"]}, 400)
    except Exception as e:
        return make_response({"errors": ["validation errors"]}, 400)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(port=5555, debug=True)