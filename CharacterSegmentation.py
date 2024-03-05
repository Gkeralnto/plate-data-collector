import cv2
import numpy as np

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
