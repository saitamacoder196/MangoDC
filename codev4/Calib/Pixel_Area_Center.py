import cv2
import glob
import numpy as np
import matplotlib.pyplot as plt
import csv

cam = "Center"
ratio = 0.8 * (1/1.72)
distance_calib = 6

minarea = 1500
maxarea = 3000

write = False


def View(imge2view, ratio):
    view = imge2view.copy()
    h, w = view.shape[:2]
    scaledH = int(h * ratio)
    scaledW = int(w * ratio)
    dim = (scaledW, scaledH)
    view = cv2.resize(view, dim, interpolation=cv2.INTER_AREA)

    return view


image_folder  = "Calib/Raw/"+ cam +"/"
name_image = "RC" + str(distance_calib) + "*"
load_images = glob.glob(f'{image_folder}{name_image}.png')

xpoints = []
ypoints = []
countRect = 0


for image in load_images:
    img = cv2.imread(image)
    gray = img[:,:,2]

    # lowThresh = find_Thresh(grayFrame=a_channel, plothist=True)
    
    # _,thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    _, thresh = cv2.threshold(gray, 150, 250, cv2.THRESH_BINARY)

    cont, hier = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)


    for contour in cont:
        blank = np.zeros(img.shape[:2], dtype=np.uint8)
        cv2.drawContours(blank, [contour], 0, 255, -1)
        pixel = cv2.countNonZero(blank)
        x,y,w,h = cv2.boundingRect(contour)
        
        if (np.abs(w-h) <= 5) and pixel > minarea and pixel < maxarea:
            cv2.drawContours(img, [contour], 0, (0,255,0), 2)

            if write == True:
                ypoints.append(25/pixel)
            else:
                ypoints.append(pixel)
            countRect = countRect+1
            xpoints.append(countRect)

    VIEW_gray = View(gray, ratio)
    VIEW_thresh = View(thresh, ratio)
    VIEW_img = View(img, ratio)
    
    cv2.imshow("gray", VIEW_gray)
    cv2.imshow("thresh", VIEW_thresh)
    cv2.imshow("color", VIEW_img)
    cv2.waitKey(0)

# ymeans = np.mean(ypoints)

# plt.scatter(xpoints, ypoints)
# plt.plot([0,max(xpoints)], [ymeans, ymeans], color = 'red')
# plt.show()


# if write:
#     data = [distance_calib, ymeans]

#     csvfile = open('Center.csv', 'a')
#     outcsv = csv.writer(csvfile)

#     outcsv.writerow(data)

#     csvfile.close()



