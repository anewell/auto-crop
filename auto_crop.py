import cv2
import numpy
import math

def comp_intersect(line1, line2):
    x = [0,line1[0], line1[2], line2[0], line2[2]]
    y = [0,line1[1], line1[3], line2[1], line2[3]]
    d = float((x[1]-x[2])*(y[3]-y[4]) - (y[1]-y[2])*(x[3]-x[4]))
    pt = [-1,-1]
    if not d == 0:
        pt[0] = int(((x[1]*y[2]-y[1]*x[2])*(x[3]-x[4]) - (x[1]-x[2])*(x[3]*y[4] - y[3]*x[4]))/d)
        pt[1] = int(((x[1]*y[2]-y[1]*x[2])*(y[3]-y[4]) - (y[1]-y[2])*(x[3]*y[4] - y[3]*x[4]))/d)
    return (pt[0],pt[1])
    
def calc_dist(line):
    pt1 = (line[0], line[1])
    pt2 = (line[2], line[3])
    return math.sqrt((pt1[0]-pt2[0])**2 + (pt1[1]-pt2[1])**2)

def calc_ang(line):
    pt1 = (line[0], line[1])
    pt2 = (line[2], line[3])
    if not ((pt1[0] - pt2[0]) == 0):
        ang = math.atan(float(pt1[1]-pt2[1])/(pt1[0]-pt2[0]))*180/math.pi
        if ang < 0:
            ang += 180
        return ang
    else:
        return 90.0
    
                    
img = cv2.imread("ad_test_4.jpg")
img_bw = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
corners = []
bound = 3
attempts = 0
edges = cv2.Canny(img_bw, 150, 200, apertureSize = 3)
lines = cv2.HoughLinesP(edges, 1, numpy.pi/180, 150, minLineLength = 100, maxLineGap = 10)
while len(corners) < 4:
    if attempts == 1:
        bound = 300
    corners = []
    max_line = 0
    max_dist = 0
    max_line_ang = 0
    for line in lines[0]:
        pt1 = (line[0], line[1])
        pt2 = (line[2], line[3])
        dist = calc_dist(line)
        if dist > max_dist:
            max_dist = dist
            max_line = line
            max_line_ang = calc_ang(line)
        #if dist > 25:
            #cv2.line(img, pt1, pt2, (0,0,255), 2)
    
    int_lines = []
    for i in range(len(lines[0])):
        pt = comp_intersect(lines[0][i], max_line)
        if (((abs(pt[0]-max_line[0]) < bound and abs(pt[1]-max_line[1]) < bound) or
            (abs(pt[0]-max_line[2]) < bound and abs(pt[1]-max_line[3]) < bound)) and
            (not pt == (-1,-1))):
            #cv2.circle(img, pt, 4, (0,0,255))
            corners += [pt]
            int_lines += [lines[0][i]]
            
    if len(int_lines) >= 2:           
        greater = max(calc_dist(int_lines[0]),calc_dist(int_lines[1]))
        for line in lines[0]:
            if (not (line == max_line).all() and
                not (line == int_lines[0]).all() and
                not (line == int_lines[1]).all()):
                ang = calc_ang(line)
                if abs(ang - max_line_ang) < 20:
                    pt_a = comp_intersect(line,int_lines[0])
                    pt_b = comp_intersect(line,int_lines[1])
                    if (calc_dist([pt_a[0], pt_a[1], max_line[0], max_line[1]]) > greater and
                        calc_dist([pt_a[0], pt_a[1], max_line[2], max_line[3]]) > greater and
                        calc_dist([pt_b[0], pt_b[1], max_line[0], max_line[1]]) > greater and
                        calc_dist([pt_b[0], pt_b[1], max_line[2], max_line[3]]) > greater):
                        #cv2.circle(img, pt_a, 4, (0,0,255))
                        #cv2.circle(img, pt_b, 4, (0,0,255))
                        corners += [pt_a]
                        corners += [pt_b]
                        break
    attempts += 1
                
            
# Sorts corners to go top left, top right, bottom right, bottom left

print corners
corners = list(set(corners))
while len(corners) > 4:
    center_x = sum(corners[x][0] for x in range(len(corners)))/len(corners)
    center_y = sum(corners[x][1] for x in range(len(corners)))/len(corners)
    min_d = 10000
    closest = (-1,-1)
    for i in range(len(corners)):
        for j in range((i+1),len(corners)):
            dist = calc_dist([corners[i][0], corners[i][1], corners[j][0], corners[j][1]])
            if dist < min_d:
                min_d = dist
                closest = (i,j)
    
    dist1 = calc_dist([center_x, center_y, corners[closest[0]][0], corners[closest[0]][1]])
    dist2 = calc_dist([center_x, center_y, corners[closest[1]][0], corners[closest[1]][1]])
    print corners[closest[0]],corners[closest[1]]
    if dist1 < dist2:
        corners.remove(corners[closest[1]])
    else:
        corners.remove(corners[closest[0]])
    
center_x = sum(corners[x][0] for x in range(len(corners)))/len(corners)
center_y = sum(corners[x][1] for x in range(len(corners)))/len(corners)  
print center_x, center_y
proper_order = [0,0,0,0]
for i in range(4):
    if corners[i][0] <= center_x and corners[i][1] <= center_y:
        proper_order[0] = corners[i]
    elif corners[i][0] >= center_x and corners[i][1] <= center_y:
        proper_order[1] = corners[i]
    elif corners[i][0] >= center_x and corners[i][1] >= center_y:
        proper_order[2] = corners[i]
    elif corners[i][0] <= center_x and corners[i][1] >= center_y:
        proper_order[3] = corners[i]
        
corners = proper_order
print corners
 
new_width = int(calc_dist([corners[0][0], corners[0][1],
                       corners[1][0], corners[1][1]]))
new_height = int(calc_dist([corners[0][0], corners[0][1],
                       corners[3][0], corners[3][1]]))
 
corners = numpy.array(corners,numpy.float32)
new_corners = numpy.array([(0,0),(new_width,0),(new_width,new_height),(0,new_height)],numpy.float32)
print new_corners
 
M = cv2.getPerspectiveTransform(corners, new_corners)
warp = cv2.warpPerspective(img, M, (new_width,new_height))
cv2.namedWindow("Original",cv2.CV_WINDOW_AUTOSIZE)
cv2.imshow("Original",img)
cv2.namedWindow("Cropped",cv2.CV_WINDOW_AUTOSIZE)
cv2.imshow("Cropped",warp)
cv2.waitKey(0)

