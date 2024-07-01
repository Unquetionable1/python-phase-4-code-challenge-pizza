#!/usr/bin/env python3
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource, reqparse
from models import db, Restaurant, RestaurantPizza, Pizza
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

class RestaurantsResource(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return [restaurant.to_dict(only=('address', 'id', 'name')) for restaurant in restaurants], 200
api.add_resource(RestaurantsResource, '/restaurants')

class RestaurantResource(Resource):
    def get(self, id):
        restaurant = db.session.get(Restaurant,id)
        if not restaurant:
            return {'error': "Restaurant not found"}, 404
        return restaurant.to_dict(only=('address', 'id', 'name', 'restaurant_pizzas')), 200
    
    def delete(self, id):
        restaurant = db.session.get(Restaurant,id)
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return {}, 204
        else:
            return {'error': "Restaurant not found"}, 404
api.add_resource(RestaurantResource, '/restaurants/<int:id>')

class PizzasResource(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return [pizza.to_dict(only=('id', 'name', 'ingredients')) for pizza in pizzas], 200
api.add_resource(PizzasResource, '/pizzas')

class RestaurantPizzasResource(Resource):
    def post(self):
        data = request.get_json()

        price = data.get('price')
        restaurant_id = data.get('restaurant_id')
        pizza_id = data.get('pizza_id')

        if not (1 <= price <= 30):
            return {'errors': ['validation errors']}, 400
        
        restaurant = db.session.get(Restaurant,restaurant_id)
        pizza = db.session.get(Pizza,pizza_id)
        
        if not restaurant or not pizza:
            return {'errors': ['Invalid restaurant_id or pizza_id']}, 400
        
        
        restaurant_pizza = RestaurantPizza(
            price=price,
            pizza_id=pizza_id,
            restaurant_id=restaurant_id
        )
        
        
        db.session.add(restaurant_pizza)
        db.session.commit()

        return {
            'id': restaurant_pizza.id,
            'price': restaurant_pizza.price,
            'pizza_id': pizza_id,
            'restaurant_id': restaurant_id,
            'pizza': pizza.to_dict(only=('id', 'name', 'ingredients')),
            'restaurant': restaurant.to_dict(only=('id', 'name', 'address'))
        }, 201
api.add_resource(RestaurantPizzasResource, '/restaurant_pizzas')

if __name__ == "__main__":
    app.run(port=5555, debug=True)
