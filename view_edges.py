import cv2
import numpy
    
#===============================================================================
# Initialize variables.
#===============================================================================
filename = "images/ad_test_15.jpg"

#===============================================================================
# Import and set up image to be processed.
#===============================================================================
img = cv2.imread(filename)
# Convert image to grayscale, then canny to get edges
img_bw = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
edges = cv2.Canny(img_bw, 150, 200, apertureSize = 3)
# Apply Hough operation to get lines.
lines = cv2.HoughLinesP(edges,1,numpy.pi/180, 70, minLineLength = 50, maxLineGap = 5)
for line in lines[0]:
    cv2.line(img, (line[0],line[1]), (line[2],line[3]), (0,255,0))

#===============================================================================
# Display results.
#===============================================================================
cv2.namedWindow("Original",cv2.CV_WINDOW_AUTOSIZE)
cv2.imshow("Original",edges)

# Wait for user keypress to close window.
cv2.waitKey(0)