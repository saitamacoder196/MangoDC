import cv2
import numpy as np
import matplotlib.pyplot as plt
import csv

cam = "Left"
ratio = 1 * (1)
distance_calib = 0
minarea = 200
maxarea = 340

write = False


def View(imge2view, ratio):
    view = imge2view.copy()
    h, w = view.shape[:2]
    scaledH = int(h * ratio)
    scaledW = int(w * ratio)
    dim = (scaledW, scaledH)
    view = cv2.resize(view, dim, interpolation=cv2.INTER_AREA)

    return view

xpoints = []
ypoints = []
countRect = 0

for i in range(3):
    img = cv2.imread("Calib/Raw/"+ cam +"/RL" + str(distance_calib) + str(i)+ ".png")
    gray  = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # gray = img[:,:,1]
    
    # blur = cv2.blur(gray, (5, 5))
    # _,thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)

    cont, hier = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)


    for contour in cont:
        blank = np.zeros(img.shape[:2], dtype=np.uint8)
        cv2.drawContours(blank, [contour], 0, 255, -1)
        pixel = cv2.countNonZero(blank)
        x,y,w,h = cv2.boundingRect(contour)
        
        if (np.abs(w-h) <= 3) and pixel > minarea and pixel < maxarea:
            blank1 = np.zeros(img.shape[:2], dtype=np.uint8)

            cv2.drawContours(img, [contour], 0, (0,255,0), 2)

            if write:
                ypoints.append(9/pixel)
            else:
                ypoints.append(pixel)
            countRect = countRect+1
            xpoints.append(countRect)

    if write == False:
        VIEW_gray = View(gray, ratio)
        VIEW_thresh = View(thresh, ratio)
        VIEW_img = View(img, ratio)
        # VIEW_edge = View(th2, ratio)
        
        # cv2.imshow("edge", VIEW_edge)
        cv2.imshow("gray", VIEW_gray)
        cv2.imshow("thresh", VIEW_thresh)
        cv2.imshow("color", VIEW_img)
        cv2.waitKey(0)

ymeans = np.mean(ypoints)

plt.scatter(xpoints, ypoints)
plt.plot([0,max(xpoints)], [ymeans, ymeans], color = 'red')
plt.show()


if write:
    data = [distance_calib, ymeans]

    csvfile = open('Left.csv', 'a')
    outcsv = csv.writer(csvfile)

    outcsv.writerow(data)

    csvfile.close()




