from flask import Flask, request, jsonify, render_template, send_file
import cv2
import numpy as np
import base64
from flask_cors import CORS
import CharacterSegmentation as cs
import random
import pyodbc as odbc

connection_string = "Driver={ODBC Driver 18 for SQL Server};Server=tcp:plates-server.database.windows.net;Database=plates-characters;Uid=plateslogin;Pwd=Geribosiballa123;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"

app = Flask(__name__)
CORS(app, origins='https://pinakides.azurewebsites.net/', supports_credentials=True, allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Headers"])

@app.route("/")
def index():
    return send_file('html/MainPage.html')

@app.route("/<path:path>")
def returnFiles(path):
    return send_file(path)


@app.route('/process-image', methods=['POST'])
def processImage():
    try:
        #Connect to SQLite Database
        conn = odbc.connect(connection_string)
        cursor = conn.cursor()

        #Create a table
        cursor.execute("CREATE TABLE IF NOT EXISTS characters (id INTEGER PRIMARY KEY, image BLOB, label TEXT)")
        
        #Process Website Request to send Image
        if 'image' not in request.json:
            return jsonify({'error' : 'Image data not found in request'}), 400
        
        image_data = request.json['image']

        try:
            decodedData = base64.b64decode(image_data)
        except Exception as e:
            return jsonify({'error':'Failed to decode Base64 image data'}), 400
        
        try:
            nparr = np.frombuffer(decodedData, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        except Exception as e:
            return jsonify({'error':'Failed to decode image data into numpy array'}), 400
        

        #Extract characters from image
        images = cs.extractCharactersFromPlate(image)
        for img, i in zip(images, range(0, len(images))):
            #Insert images into the table
            buffer = cv2.imencode('.png', img)[1]
            image_binary = buffer.tobytes()
            cursor.execute('INSERT INTO characters (image, label) VALUES (?, ?)', (image_binary, "-1"))

        #Commit the changes
        conn.commit()

        return jsonify({'message':'Image received, decoded and processed'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/random-pic', methods=['GET'])
def random_image():
    #Connect to SQLite database
    conn = odbc.connect(connection_string)
    cursor = conn.cursor()

    #Select random image from data
    cursor.execute("SELECT id, image FROM characters WHERE LABEL = ? ORDER BY RANDOM() LIMIT 1", ("-1",))
    row = cursor.fetchone()
    conn.close()

    if(row):
       image_id, image_data = row
       image_base64 = base64.b64encode(image_data).decode('utf-8')
       return jsonify({'id': image_id, 'image_blob': image_base64})
    else:
        return jsonify({'id': '', 'image_blob': ''})

@app.route('/process-user-input', methods=['POST'])
def update_label():
    try:
        #Connect to SQLite database
        conn = odbc.connect(connection_string)
        cursor = conn.cursor()

        if 'id' not in request.json:
            return jsonify({'error' : 'ID data not found in request'}), 400
        
        if 'label' not in request.json:
            return jsonify({'error' : 'Label data not found in request'}), 400
        
        #Update the label
        data = request.json
        image_id = data.get('id')
        new_label = data.get('label')

        cursor.execute("UPDATE characters SET label = ? WHERE id = ?", (new_label, image_id))
        conn.commit()
    except Exception as e:
        return jsonify({'error':str(e)}), 500
    finally:
        conn.close()



if __name__ == '__main__':
    app.run(debug=False)
    
