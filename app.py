from flask import Flask, redirect, url_for, render_template, request
from flaskext.mysql import MySQL
import sys

# print("HEREEEEEE",request.form['productType'],file=sys.stderr)
# print("HEREEEEEE",selectedProductId,file=sys.stderr)

app = Flask(__name__)

#DB Connection
app.config['MYSQL_DATABASE_USER'] = 'front_end'
app.config['MYSQL_DATABASE_PASSWORD'] = '52sjmR4zggYH'
app.config['MYSQL_DATABASE_DB'] = 'Kiosk'
app.config['MYSQL_DATABASE_HOST'] = 'database-2.cslzwwrmb888.us-east-2.rds.amazonaws.com'

mysql = MySQL(app)

raceTypes = ["Throughbreed","Harness"]

bundleSelectedFlag = False

gSelectedProductId = ""

userSelection = {
    'race':'',
    'date':'',
    'product':'',
    'track':''
}

conn = mysql.connect()
cursor = conn.cursor()

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

@app.route("/product/<selectedRaceType>", methods=["POST","GET"])
def product(selectedRaceType):
    if request.method == 'POST':
        selectedProductName = request.form['productType']
        returnedValue = cursor.execute("SELECT product_id FROM Product where product_name = %s and product_type = %s", (selectedProductName, selectedRaceType))
        result = cursor.fetchone()
        selectedProductId = result[0]
        global gSelectedProductId
        gSelectedProductId = selectedProductId
        userSelection.update({
            "product": selectedProductId
        })
        global bundleSelectedFlag
        if "Bundle" in selectedProductId:
            bundleSelectedFlag = True
        else:
            bundleSelectedFlag = False
        return redirect(url_for("date",userSelection=userSelection, selectedProductId=selectedProductId))
    else:
        returnedValue = cursor.execute("SELECT product_name FROM Product where product_type = %s",selectedRaceType)
        if returnedValue > 0 :
            result = cursor.fetchall()
            return render_template("productSelection.html",result=result,userSelection=userSelection)
        else:
            return("PRODUCT NOT WORKING!")#ERROR PAGE

@app.route("/date/<selectedProductId>", methods=["POST","GET"])
def date(selectedProductId):
    if request.method == 'POST':
        selectedDate = request.form['date']
        userSelection.update({
            "date":selectedDate
        })
        return redirect(url_for("track",userSelection=userSelection, selectedDate=selectedDate))
    else:
        returnedValue = cursor.execute("SELECT Date FROM Race where product_id = %s",selectedProductId)
        if returnedValue > 0 :
            result = cursor.fetchall()
            return render_template("dateSelection.html",result=result,userSelection=userSelection)
        else:
            return("DATE NOT WORKING!")#ERROR PAGE

@app.route("/track/<selectedDate>", methods=["POST","GET"])
def track(selectedDate):
    if request.method == 'POST':
        selectedTrack = request.form['track']
        userSelection.update({
            "track":selectedTrack
        })
        return (userSelection)
    else:
        returnedValue = cursor.execute("SELECT race_course_name FROM Race where Date = %s and product_id = %s",(selectedDate,gSelectedProductId))
        if returnedValue > 0 :
            result = cursor.fetchall()
            return render_template("trackSelection.html",result=result,userSelection=userSelection)
        else:
            return("DATE NOT WORKING!")#ERROR PAGE

if __name__ == "__main__":
    app.run(debug=True)