from flask import Flask, redirect, url_for, render_template, request
from flaskext.mysql import MySQL
import sys
import ast

#BHAVIK
from ftplib import FTP
import os
import psutil
from time import sleep

# print("HEREEEEEE",request.form['productType'],file=sys.stderr)
# print("HEREEEEEE",selectedProductId,file=sys.stderr)

app = Flask(__name__)

#DB Connection
app.config['MYSQL_DATABASE_USER'] = 'front_end'
app.config['MYSQL_DATABASE_PASSWORD'] = '52sjmR4zggYH'
app.config['MYSQL_DATABASE_DB'] = 'Kiosk'
app.config['MYSQL_DATABASE_HOST'] = 'database-2.cslzwwrmb888.us-east-2.rds.amazonaws.com'

mysql = MySQL(app)

raceTypes = ["Thoroughbred","Harness"]

bundleSelectedFlag = False

gSelectedProductId = ""

userSelection = {
    "race":"",
    "date":"",
    "product":"",
    "track":""
}

# conn = mysql.connect()
# cursor = conn.cursor()

conn = ""
cursor = ""

@app.route("/", methods=["POST","GET"])
def landing():
    global conn
    global cursor
    conn = mysql.connect()
    cursor = conn.cursor()

    if request.method == 'POST':
        selectedRaceType = request.form['raceType']
        userSelection.update({
            "race": selectedRaceType
        })
        return redirect(url_for("product",userSelection = userSelection, selectedRaceType=selectedRaceType))
    else:
        userSelection.update({
            "race":"",
            "date":"",
            "product":"",
            "track":""
        })
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
            "product": selectedProductName
        })
        global bundleSelectedFlag
        if "Bundle" in selectedProductId:
            bundleSelectedFlag = True
        else:
            bundleSelectedFlag = False
        return redirect(url_for("date",userSelection = userSelection, selectedProductId=selectedProductId))
    else:
        returnedValue = cursor.execute("SELECT product_name FROM Product where product_type = %s",selectedRaceType)
        if returnedValue > 0 :
            result = cursor.fetchall()
            return render_template("productSelection.html",userSelection = userSelection,result=result)
        else:
            return("PRODUCT NOT WORKING!")#ERROR PAGE

@app.route("/date/<selectedProductId>", methods=["POST","GET"])
def date(selectedProductId):
    if request.method == 'POST':
        selectedDate = request.form['date']
        userSelection.update({
            "date":selectedDate
        })
        return redirect(url_for("track",userSelection = userSelection, selectedDate=selectedDate))
    else:
        returnedValue = cursor.execute("SELECT DISTINCT Date FROM Race where product_id = %s ORDER BY Date",selectedProductId)
        if returnedValue > 0 :
            result = cursor.fetchall()
            return render_template("dateSelection.html",userSelection = userSelection,result=result)
        else:
            return("DATE NOT WORKING!")#ERROR PAGE

@app.route("/track/<selectedDate>", methods=["POST","GET"])
def track(selectedDate):
    if request.method == 'POST':
        selectedTrack = []
        selectedTrack.append(request.form['track']) 
        userSelection.update({
            "track":selectedTrack
        })
        return redirect(url_for("printPPE", userSelection=userSelection))
    else:
        returnedValue = cursor.execute("SELECT race_course_name FROM Race where Date = %s and product_id = %s",(selectedDate,gSelectedProductId))
        if returnedValue > 0 :
            result = cursor.fetchall()
            return render_template("trackSelection.html",userSelection = userSelection,result=result)
        else:
            return("DATE NOT WORKING!")#ERROR PAGE

@app.route("/get_ppe_name/<userSelection>")
def printPPE(userSelection):
    userSelection = ast.literal_eval(userSelection)
    get_ppe_name(userSelection)
    conn.close()
    return ('', 204)
    # return(userSelection)

#BHAVIK
def get_ppe_name(data_dict):
    product = data_dict['product']
    product_type = data_dict['race']
    product_qty_query = f"select product_id,product_qty from Product where product_name = '{product}' and product_type = '{product_type}'"
    cursor.execute(product_qty_query)
    result = list(cursor.fetchone())
    product = result[0]
    product_qty = int(result[1])
    ppe_file_name  = []
    ppe_file = []
    for i in range(product_qty):
        ppe_file_query = f"select ppe_id from Kiosk.Race where product_id = '{product}' and date = '{data_dict['date']}' and race_course_name = '{data_dict['track'][i]}'"
        cursor.execute(ppe_file_query)
        result = str(cursor.fetchone()[0])
        ppe_file_name.append(result)
    
    for file in ppe_file_name:
        get_details = f"select location, ftp_client,ppe_file_name from PPE where ppe_id= '{file}'"
        cursor.execute(get_details)
        result =  list(cursor.fetchone())
        ppe_file.append(download_ppe(result))
    print_ppe(ppe_file)
    return ppe_file_name
     
def download_ppe(location_list):
    location = location_list[0]
    ftp_client = location_list[1]
    ppe_filename = location_list[2]
    if ftp_client == "ftp.jockeyclub.com":
        creds = ["mshs","3Wqbg3FK"]
    with FTP(ftp_client) as ftp:
        ftp.login(user=creds[0],passwd=creds[1])
        ftp.cwd(location)
        path = os.path.join(os.path.expanduser('~'), 'downloads')
        local_filename = os.path.join(path, ppe_filename)
        lf = open(local_filename, "wb")
        ftp.retrbinary("RETR " + ppe_filename, lf.write, 8*1024)
        lf.close()
    return ppe_filename
    
def print_ppe(ppe_file):
    path = os.path.join(os.path.expanduser('~'), 'downloads')
    for file in ppe_file:
        local_filename = os.path.join(path, file)
        os.startfile(local_filename,"print")
        sleep(10)
        for p in psutil.process_iter(): #Close Acrobat after printing the PDF
            if 'AcroRd' in str(p):
                p.kill()
    
if __name__ == "__main__":
    app.run(debug=True)