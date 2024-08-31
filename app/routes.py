from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return "Hello, Flask is set up!"