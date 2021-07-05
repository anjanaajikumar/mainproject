from sklearn import metrics
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
# import matplotlib.pyplot as mpt
from flask import Flask, redirect, url_for, render_template, request
import pymysql
# import numpy as np
import pandas as pd
from flask_table import Table, Col
from numpy import split

pymysql.install_as_MySQLdb()

app = Flask(__name__)

conn = pymysql.connect(host="localhost", user="root", password="", db="flask")


# building flask table for showing recommendation results
class Results(Table):
    id = Col('Id', show=False)
    title = Col('Recommending Cars with Details')
    


# home page

@app.route("/")
def home():
    return render_template("index.html")


# registration page

@app.route("/register", methods=["POST"])
def registration():
    fname = str(request.form["fname"])
    lname = str(request.form["lname"])
    email = str(request.form["email"])
    password = str(request.form["password"])

    cursor = conn.cursor()
    cursor.execute("INSERT INTO user (fname,lname,email,password)VALUES(%s,%s,%s,%s)",
                   (fname, lname, email, password))
    conn.commit()
    return redirect(url_for("login"))


# userlogin page

@app.route("/login")
def login():
    return render_template("index.html")


# user registration page

@app.route("/register")
def register():
    return render_template("registration.html")


# login check
@app.route("/validuser", methods=["POST"])
def check():
    email = str(request.form["email"])
    password = str(request.form["password"])
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM user where email ='" + email + "'")
    user = cursor.fetchone()

    if len(user) == 1:
        return redirect(url_for("user"))
    else:
        return ("failed")


# userlogin page
@app.route("/user", methods=["GET", "POST"])
def user():
    if request.method == "POST":
        return render_template('recommendation.html')
    return render_template("rating.html")


# about page
@app.route("/about")
def about():
    return render_template("about.html")


# recommendation page
@app.route("/recommendation", methods=["GET", "POST"])
def recommendation():
    dataset = pd.read_csv('data.csv')
    fueltype = request.form['FUELTYPE']
    vehicletype = request.form['vehicletype']
    price = int(request.form['price'])
    minprice = int(request.form['minprice'])
    Kilometer = int(request.form['Kilometer'])
    try:
        x = dataset.iloc[:, 1:7][
            (dataset['FUEL TYPE'] == fueltype) &
            (dataset['VEHICLE TYPE'] == vehicletype) &
            (dataset['PRICE'] <= price) &
            (dataset['PRICE'] >= minprice) &
            (dataset['KM'] <= Kilometer)
        ].values

        y = dataset.iloc[:, 0][
            (dataset['FUEL TYPE'] == fueltype) &
            (dataset['VEHICLE TYPE'] == vehicletype) &
            (dataset['PRICE'] <= price) &
            (dataset['PRICE'] >= minprice) &
            (dataset['KM'] <= Kilometer)
        ].values
        del dataset

        enc_fuel_type = LabelEncoder()
        enc_veh_type = LabelEncoder()
        enc_VEHICLE_COLOR = LabelEncoder()
        enc_y = LabelEncoder()

        x[:, 5] = enc_veh_type.fit_transform(x[:, 5])   
        x[:, 3] = enc_VEHICLE_COLOR.fit_transform(x[:, 3])  
        x[:, 4] = enc_fuel_type.fit_transform(x[:, 4])  

        y = enc_y.fit_transform(y)
        x_train, x_test, y_train, y_test = train_test_split(
        x, y, random_state=0, shuffle=True)
        del x
        del y
        st_x = StandardScaler()
        x_train = st_x.fit_transform(x_train)
        x_test = st_x.fit_transform(x_test)
        print('RandomForestClassifier finding recommendations')
        clf = RandomForestClassifier(n_estimators=100)
        clf.fit(x_train, y_train)
        
        y_pred = clf.predict(x_test)
        r = enc_y.inverse_transform(y_pred)
        #re = x_test[:,0]

        output = r[:5]
        
        table = Results(output)
        
           
        
        table.border = True
        table.classes = ['table', 'table-hover', 'table-bordered']
        return render_template('recommendation.html', table=table)
    except:
        return render_template('error.html')

if __name__ == "__main__":
    app.run(debug=True)
