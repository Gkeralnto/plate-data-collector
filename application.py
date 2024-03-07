from flask import Flask, request, jsonify, send_file, abort
import cv2
import numpy as np
import base64
from flask_cors import CORS
import pyodbc as odbc

def extractCharactersFromPlate(img):
    imgCopy = img.copy()
    extractedCharacters = []

    grayImg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #Convert to grayscale

    thresh = cv2.threshold(grayImg, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)[1] #Extract the inverted binary image using the Oshu thresholding algorithm

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 5)) #Create 3x5 structuring element for the Morphology algorithm
    eroded = cv2.erode(thresh, kernel, iterations=1)
    dilation = cv2.dilate(eroded, kernel, iterations = 3) #Extract the dilated image
    contours= cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        char = imgCopy[y:y+h, x:x+w]
        extractedCharacters.append(char)

    return extractedCharacters

def connect_to_database():
    try:
        connection_string = "Driver={ODBC Driver 18 for SQL Server};Server=tcp:plates-server.database.windows.net,1433;Database=plates-characters;Uid=plateslogin;Pwd=Geribosiballa123;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
        return odbc.connect(connection_string)
    except Exception as e:
        raise e

app = Flask(__name__)
CORS(app, origins='https://pinakides.azurewebsites.net/', supports_credentials=True, allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Headers"])

@app.route("/")
def index():
    try:
        conn = connect_to_database(connection_string)
        cursor = conn.cursor()

        cursor.execute("EXEC CreateCharactersTableIfNotExists;")
        conn.commit()
        conn.close()
        return send_file('html/MainPage.html')
    except Exception as e:
        response = jsonify({'error': str(e)})
        response.status_code = 500
        return response

@app.route("/<path:path>")
def returnFiles(path):
    return send_file(path)

@app.route('/process-image', methods=['POST'])
def processImage():
    print("Process Image succesful")
    try:
        conn = connect_to_database(connection_string)
        cursor = conn.cursor()

        if 'image' not in request.json:
            return jsonify({'error' : 'Image data not found in request'}), 400
        
        image_data = request.json['image']
        decodedData = base64.b64decode(image_data)
        nparr = np.frombuffer(decodedData, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        images = extractCharactersFromPlate(image)
        for img, i in enumerate(images):
            buffer = cv2.imencode('.png', img)[1]
            image_binary = buffer.tobytes()
            cursor.execute('INSERT INTO characters (image, label) VALUES (?, ?)', (image_binary, '-1'))

        conn.commit()
        return jsonify({'message':'Image received, decoded and processed'})
    except Exception as e:
        response = jsonify({'error': str(e)})
        response.status_code = 500
        return response
    finally:
        conn.close()

@app.route('/random-pic', methods=['GET'])
def random_image():
    try:
        conn = connect_to_database(connection_string)
        cursor = conn.cursor()

        cursor.execute("SELECT TOP 1 id, image FROM characters WHERE LABEL = ? ORDER BY NEWID();", ('-1',))
        row = cursor.fetchone()
        conn.close()

        if row:
            image_id, image_data = row
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            return jsonify({'id': image_id, 'image_blob': image_base64})
        else:
            response = jsonify({'error': 'Error getting Image'})
            response.status_code = 404
            return response
    except Exception as e:
        response = jsonify({'error': str(e)})
        response.status_code = 500
        return response

@app.route('/process-user-input', methods=['POST'])
def update_label():
    print("Process User Input succesful")
    try:
        conn = connect_to_database(connection_string)
        cursor = conn.cursor()

        if 'id' not in request.json or 'label' not in request.json:
            return jsonify({'error': 'ID or Label data not found in request'}), 400
        
        data = request.json
        image_id = data.get('id')
        new_label = data.get('label')

        cursor.execute("UPDATE characters SET label = ? WHERE id = ?", (new_label, image_id))
        conn.commit()
        return jsonify({'message': 'Label updated successfully'})
    except Exception as e:
        response = jsonify({'error': str(e)})
        response.status_code = 500
        return response
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=False)
