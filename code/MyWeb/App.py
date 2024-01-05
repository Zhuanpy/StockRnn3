from flask import Flask
from flask import render_template, request
from flask import jsonify
from web_utils import *
import json

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


@app.route("/")
def hello_word():
    return render_template("main.html")


@app.route("/timing")
def get_time():
    return get_times()


@app.route("/trend")
def trends_data():
    """
    get trends data
    """
    data = get_trends_data()
    print(data[2][0])
    print(data[2][1])
    print(data[2][2])
    print(data[2][3])
    print(data[2][4])

    return render_template('PlotPoolCount.html',

                           stocktrends1=json.dumps(data[0][0]),
                           stocktrends2=json.dumps(data[0][1]),
                           stocktrends3=json.dumps(data[0][2]),

                           box2date=json.dumps(data[1][0]),
                           box2Up=json.dumps(data[1][1]),
                           box2ReUp=json.dumps(data[1][2]),
                           box2Down=json.dumps(data[1][3]),
                           box2ReDown=json.dumps(data[1][4]),

                           box3date=json.dumps(data[2][0]),
                           box3up1=json.dumps(data[2][1]),
                           box3up2=json.dumps(data[2][2]),
                           box3down1=json.dumps(data[2][3]),
                           box3down2=json.dumps(data[2][4]),

                           box4date=json.dumps(data[3][0]),
                           box4up1=json.dumps(data[3][1]),
                           box4up2=json.dumps(data[3][2]),
                           box4up3=json.dumps(data[3][3]),
                           box4down1=json.dumps(data[3][4]),
                           box4down2=json.dumps(data[3][5]),
                           box4down3=json.dumps(data[3][6]),

                           box5date=json.dumps(data[4][0]),
                           box5up1=json.dumps(data[4][1]),
                           box5up2=json.dumps(data[4][2]),
                           box5down1=json.dumps(data[4][3]),
                           box5down2=json.dumps(data[4][4]),

                           )


@app.route("/index", methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('MyForm.html')

    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')
        print(f'name:{name}, password:{password};')
        return name, password


@app.route("/tryjson")
def try_json():
    data_ = {'name': '张三',
             'age': 18}

    return jsonify(data_)


if __name__ == '__main__':
    app.run()
