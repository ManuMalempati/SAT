import cv2
import pytesseract

def extract_license_plate(image_path):
    # Loading the image
    image = cv2.imread(image_path)

    # Converting the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # cascade XML file
    cascade_file_path = 'haarcascade_russian_plate_number.xml'

    # Loading the cascade classifier
    license_plate_cascade = cv2.CascadeClassifier(cascade_file_path)

    # Performing license plate detection
    license_plates = license_plate_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    for (x, y, w, h) in license_plates:
        # Extract the license plate from the image
        license_plate = gray[y:y + h, x:x + w]

        # Use Tesseract to perform OCR on the license plate
        text = pytesseract.image_to_string(license_plate)

        print(f'License Plate Text: {text}')

        # Draw a rectangle around the license plate in the original image
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
    
    # uncomment for test run
    # Create a named window and adjust its size
    # cv2.namedWindow('License Plate Detection', cv2.WINDOW_NORMAL)
    # cv2.resizeWindow('License Plate Detection', 600, 600)

    # # Display the image with license plate detected
    # cv2.imshow('License Plate Detection', image)
    # cv2.waitKey(0)

    return

# uncomment for test run
# img = "car1.png"
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# extract_license_plate(img)
