import cv2
import numpy
import math

#===============================================================================
# Helper functions.
#===============================================================================
def intersect(line1, line2):
    # Find point of intersection of two lines.
    x = [0,line1[0], line1[2], line2[0], line2[2]]
    y = [0,line1[1], line1[3], line2[1], line2[3]]
    d = float((x[1]-x[2])*(y[3]-y[4]) - (y[1]-y[2])*(x[3]-x[4]))
    pt = [-1,-1]
    if not d == 0:
        pt[0] = int(((x[1]*y[2]-y[1]*x[2])*(x[3]-x[4]) - (x[1]-x[2])*(x[3]*y[4] - y[3]*x[4]))/d)
        pt[1] = int(((x[1]*y[2]-y[1]*x[2])*(y[3]-y[4]) - (y[1]-y[2])*(x[3]*y[4] - y[3]*x[4]))/d)
    return (pt[0],pt[1])
def calc_dist(line): 
    # Calculate the distance between two points
    x1,y1,x2,y2 = line[0],line[1],line[2],line[3]
    return math.sqrt((x1-x2)**2 + (y1-y2)**2)
def calc_ang(line):
    # Calculate the angle that describes a line
    x1,y1,x2,y2 = line[0],line[1],line[2],line[3]
    if not ((x1-x2) == 0):
        ang = math.atan(float(y1-y2)/(x1-x2))*180/math.pi
        if ang < 0:
            ang+=180
        return ang
    else:
        return 90.0
def calc_area(points):
    points = sorted(points, key = lambda tup: tup[0])
    x1,y1 = points[0][0],points[0][1]
    x2,y2 = points[1][0],points[1][1]
    x3,y3 = points[2][0],points[2][1]
    x4,y4 = points[3][0],points[3][1]
    a1 = .5*abs(x1*(y2-y3)+x2*(y3-y1)+x3*(y1-y2))
    a2 = .5*abs(x2*(y3-y4)+x3*(y4-y2)+x4*(y2-y3))
    return a1+a2
    
#===============================================================================
# Initialize variables.
#===============================================================================
filename = "images/ad_test_15.jpg"
corners = []
ver = []
hor = []
angle_var = 7   # Amount allowed to diverge from strictly perpendicular angles.
area_lim = 250000 # Minimum rectangle requirement
bound = 3
attempts = 0
TL = TR = BR = BL = (0,0)

#===============================================================================
# Import and set up image to be processed.
#===============================================================================
img = cv2.imread(filename)
# Convert image to grayscale, then canny to get edges
img_bw = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
edges = cv2.Canny(img_bw, 150, 180, apertureSize = 3)
# Apply Hough operation to get lines.
lines = cv2.HoughLinesP(edges,1,numpy.pi/180, 95, minLineLength = 80, maxLineGap = 10)

#===============================================================================
# Find corners of rectangle.
#===============================================================================
# Filter lines into groups that are roughly horizontal and vertical.
for line in lines[0]:
    angle = calc_ang(line)
    if abs(angle - 90) < angle_var:
        ver += [line] # VERTICAL
    elif abs(angle) < angle_var or abs(angle-180) < angle_var:
        hor += [line] # HORIZONTAL

# Make every possible rectangle, keeping those above a certain size req.
for i in range(len(ver)):
    for j in range((i+1),len(ver)):
        for k in range(len(hor)):
            for l in range((k+1),len(hor)):
                pts = []
                pts += [intersect(ver[i],hor[k])]
                pts += [intersect(ver[i],hor[l])]
                pts += [intersect(ver[j],hor[k])]
                pts += [intersect(ver[j],hor[l])]
                area = calc_area(pts)
                if (area > area_lim):
                    corners += [(pts,area)]

corners = sorted(corners, key = lambda tup: tup[1])
# We'll go with the largest rectangle just to see what it's like
largest = corners[1][0]
center_x = sum(largest[x][0] for x in range(len(largest)))/len(largest)
center_y = sum(largest[x][1] for x in range(len(largest)))/len(largest)
for i in range(4):
    if largest[i][0] <= center_x and largest[i][1] <= center_y:
        TL = largest[i]
    if largest[i][0] >= center_x and largest[i][1] <= center_y:
        TR = largest[i]
    if largest[i][0] >= center_x and largest[i][1] >= center_y:
        BR = largest[i]
    if largest[i][0] <= center_x and largest[i][1] >= center_y:
        BL = largest[i]
  
#===============================================================================
# Warp and crop for final image.
#===============================================================================
corners = [TL,TR,BR,BL]
new_width = int(calc_dist([TL[0], TL[1], TR[0], TR[1]]))
new_height = int(calc_dist([TL[0], TL[1], BL[0], BL[1]]))
corners = numpy.array(corners,numpy.float32)
new_corners = numpy.array([(0,0),(new_width,0),
                           (new_width,new_height),(0,new_height)],numpy.float32)
# Transformation matrix.
M = cv2.getPerspectiveTransform(corners, new_corners)
warp = cv2.warpPerspective(img, M, (new_width,new_height))
 
#===============================================================================
# Display results.
#===============================================================================
cv2.namedWindow("Original",cv2.CV_WINDOW_AUTOSIZE)
cv2.imshow("Original",img)
cv2.namedWindow("Cropped",cv2.CV_WINDOW_AUTOSIZE)
cv2.imshow("Cropped",warp)
cv2.imwrite("cropped_img.jpg", warp)

# Wait for user keypress to close window.
cv2.waitKey(0)