from flask import Flask, redirect, url_for, render_template, request
from flaskext.mysql import MySQL

app = Flask(__name__)

#DB Connection
app.config['MYSQL_DATABASE_USER'] = 'front_end'
app.config['MYSQL_DATABASE_PASSWORD'] = '52sjmR4zggYH'
app.config['MYSQL_DATABASE_DB'] = 'Kiosk'
app.config['MYSQL_DATABASE_HOST'] = 'database-2.cslzwwrmb888.us-east-2.rds.amazonaws.com'

mysql = MySQL(app)

raceTypes = ["Throughbreed","Harness"]

userSelection = {
    'race':'',
    'date':'',
    'product':'',
    'track':''
}

@app.route("/", methods=["POST","GET"])
def landing():
    if request.method == 'POST':
        selectedRaceType = request.form['raceType']
        userSelection.update({
            "race": selectedRaceType
        })
        return redirect(url_for("product",userSelection=userSelection, selectedRaceType=selectedRaceType))
    else:
        return render_template("raceSelection.html",userSelection = userSelection, raceTypes=raceTypes)

@app.route("/<selectedRaceType>", methods=["POST","GET"])
def product(selectedRaceType):
    if request.method == 'POST':
        return redirect(url_for("date",userSelection=userSelection, selectedRaceType=selectedRaceType))
    else:
        conn = mysql.connect()
        cursor = conn.cursor()
        returnedValue = cursor.execute("SELECT product_name FROM Product where product_type = %s",selectedRaceType)
        if returnedValue > 0 :
            result = cursor.fetchall()
            return render_template("productSelection.html",result=result,userSelection=userSelection)
        else:
            return("NOT WORKING!")#ERROR PAGE

if __name__ == "__main__":
    app.run(debug=True)