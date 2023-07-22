import cv2
import numpy as np
from datetime import datetime
from PIL import Image
import os
import xml.etree.ElementTree as ET
from cryptography.fernet import Fernet

def process_window(filename):
    # Accessing WebCam
    cap = cv2.VideoCapture(filename)

    # define the color thresholds for red and green
    red_lower = (0, 0, 150)
    red_upper = (50, 50, 255)
    green_lower = (0, 150, 0)
    green_upper = (50, 255, 50)
    yellow_lower = (0, 150, 150)
    yellow_upper = (50, 255, 255)

    #------------------------------ VARIABLES SUBJECT TO CHANGE FOR EACH VIDEO-------------------------

    # Focus postion of traffic lights (subject to change), rectangle dimensions 
    # red & yellow dimensions: 60, 150, 200, 300 
    # video2 dimensions: 600, 850, 0, 600
    focus_x_left, focus_x_right, focus_y_top, focus_y_bottom = 60, 150, 200, 300

    # video1 dimensions: 550, 700, 1200
    # Position of line used to count the vehicles (subject to change depending on road and location of intersection)
    counter_line_position_y, counter_line_left_position_x, counter_line_right_position_x = 500, 50, 600  # vertical position, left and right ends

    # Location coordinates
    location = "-37.889034, 144.652779"

    #------------------------------ VARIABLES SUBJECT TO CHANGE FOR EACH VIDEO-------------------------

    # Minimum width and height of bounding rectangle
    min_width_rect = 80
    min_height_rect = 80

    # List of captured detections
    detections = []
    detection_details = []

    # Allowable error space
    offset = 6
    counter = 0

    # Initialize detection algorithm
    algorithm = cv2.bgsegm.createBackgroundSubtractorMOG() # eliminates background data to focus on vehicle

    # Function to return the centre position of a target
    def center_pos(x,y,w,h):
        x1 = int(w/2)
        y1 = int(h/2)
        cx = x+x1
        cy = y+y1
        return cx,cy

    # Time label
    def display_time():
        now = datetime.now()
        date = datetime.today()
        current_time = now.strftime("%H: %M: %S")
        current_date = now.strftime("%d/%m/%Y")
        cv2.putText(frame1, f"{current_time} {current_date}", (190, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)
        return f"{current_time} {current_date}"

    # screenshot
    def capture_screenshot(frame, filename):
        # Convert the frame from OpenCV's BGR format to RGB (PIL's format)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(frame_rgb) # converts an array of RGB colours into a visible image
        # Save the image as a PNG file
        pil_image.save(filename)

    # Status of whether a certain vehicle has already been detected or not (avoid redundant detections)
    last_detection_status = False

    # Reading the captured video
    while True:
        ret,frame1 = cap.read()

        # If video has ended then break loop
        if not ret:
            break

        # resize the frame for faster processing
        # frame1 = cv2.resize(frame1, (1280, 720))

        # ------------------------------------------TRAFFIC SIGNAL DETECTION CODE------------------------------------------------------------------

        # apply color thresholding to detect red and green pixels
        red_mask = cv2.inRange(frame1[focus_y_top: focus_y_bottom, focus_x_left: focus_x_right], red_lower, red_upper)
        green_mask = cv2.inRange(frame1[focus_y_top: focus_y_bottom, focus_x_left: focus_x_right], green_lower, green_upper)
        yellow_mask = cv2.inRange(frame1[focus_y_top: focus_y_bottom, focus_x_left: focus_x_right], yellow_lower, yellow_upper)

        # count the number of red and green pixels
        num_red_pixels = cv2.countNonZero(red_mask)
        num_green_pixels = cv2.countNonZero(green_mask)
        num_yellow_pixels = cv2.countNonZero(yellow_mask)

        # determine the color of the traffic signal based on the number of red and green pixels
        if num_red_pixels > num_green_pixels and num_red_pixels > num_yellow_pixels:
            colour = "RED" # first initialization of colour variable
        elif num_yellow_pixels > num_red_pixels and num_yellow_pixels > num_green_pixels:
            colour = "YELLOW"
        else:
            colour = "GREEN"
        #colour = "RED" # Hardcode colour for testing
        
        # Colour label
        cv2.putText(frame1, colour, (10,50), 0, 1, (255,0,0), 2) # text label

        # ------------------------------------------VEHICLE DETECTION CODE--------------------------------------------------------------

        grey = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(grey,(3,3),5)

        # applying algorithm on each frame
        img_sub = algorithm.apply(blur)
        dilat = cv2.dilate(img_sub,np.ones((5,5)))
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
        dilatadd = cv2.morphologyEx(dilat, cv2.MORPH_CLOSE, kernel) # Morphological image to produce black/white image using exposure
        dilatadd = cv2.morphologyEx(dilatadd, cv2.MORPH_CLOSE, kernel)
        countershape,h = cv2.findContours(dilatadd, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # time label
        display_time()

        # Detector Line creation
        cv2.line(frame1, (counter_line_left_position_x,counter_line_position_y), (counter_line_right_position_x,counter_line_position_y), (0,255,0), 4) # horizontal positions specified

        for (i,c) in enumerate(countershape): # for each vehicle
            (x,y,w,h) = cv2.boundingRect(c) # dimensions of the bounding rectangle we want to add for each vehicle

            validate_counter = (w>=min_width_rect) and (h>=min_height_rect) # The bounding rect function looks for an object that is of minimum specified dimensions (cars in this case)
            if not validate_counter: # If vehicle not detected
                continue

            cv2.rectangle(frame1,(x,y),(x+w, y+h),(0,255,0), 4) # rectangle specifications
            center = center_pos(x,y,w,h) # stores centre position of rectangle
            detections.append(center)

            if center[0] > counter_line_left_position_x and center[0] < counter_line_right_position_x and center[1] < (counter_line_position_y + 6) and center[1] > (counter_line_position_y - 6): # If vehicle within line
                if colour == "RED":
                    if not last_detection_status: # If vehicle has not already been detected
                        # capture screenshot with image name as detection(counter length)
                        capture_screenshot(frame1, f"detection{len(detection_details) + 1}.png")
                        detection_image = f"detection{len(detection_details) + 1}.png"
                        detection_time = display_time()
                        detection_details.append({"Reg": "", "Time": detection_time[:10], "Date": detection_time[11:], "Location": location, "Evidence": detection_image}) # append timestamp
                        cv2.line(frame1, (counter_line_left_position_x,counter_line_position_y), (counter_line_right_position_x,counter_line_position_y), (0,127,255), 4) # line that flashes when object/vehicle detected
                        print(detection_details)
                    last_detection_status = True
                else:
                    last_detection_status = False
            else: # vehicle leaves the line, next vehicle is ready for detection
                last_detection_status = False

            cv2.circle(frame1,center,4,(0,255,0),-1) # draws a circle at the center of each rectangle
        
        cv2.putText(frame1, "Traffic System", (500,70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255), 4) # Heading

        # frame focus on traffic light, beware this might disrupt affect colour detection code if placed before that
        cv2.rectangle(frame1, (focus_x_left, focus_y_top), (focus_x_right, focus_y_bottom), (0,0,255), 4)

        # Morhpological algorithm end (background eliminator), only objects that move are exposed. The line commented below shows the background frame used to detect vehicles, uncomment to explore.
        # cv2.imshow('Detector: ', dilatadd)

        #--------------------------------------------------VEHICLE DETECTION CODE END-------------------------------------------------------
        cv2.imshow("Traffic System: ", frame1) # Window title, top to bottom, left to right

        if cv2.waitKey(30) == 27: # press esc to exit window
            break
     
    # Close captured video
    cv2.destroyAllWindows()
    cap.release()

process_window("yellow.mp4")
process_window("red.mp4")