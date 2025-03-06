from flask import render_template, request, redirect, url_for, flash, Blueprint

index_bp = Blueprint('index_bp', __name__)


@index_bp.route('/index')
@index_bp.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')