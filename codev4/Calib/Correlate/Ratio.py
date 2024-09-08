import cv2
import numpy as np

def View(imge2view, ratio):
    view = imge2view.copy()

    h, w = view.shape[:2]
    scaledH = int(h * ratio)
    scaledW = int(w * ratio)
    dim = (scaledW, scaledH)
    view = cv2.resize(view, dim, interpolation=cv2.INTER_AREA)

    return view

def Binary(image, low, upp):
   
    blur = cv2.blur(image, (3, 3))
    LAB = cv2.cvtColor(blur, cv2.COLOR_BGR2LAB)
    threshLAB = cv2.inRange(LAB, np.array(low), np.array(upp))
    blank = np.zeros(image.shape[:2], dtype=np.uint8)
    contours, _ = cv2.findContours(threshLAB, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contour = max(contours, key=cv2.contourArea)
    cv2.drawContours(blank, [contour], 0, 255, -1)

    x,y,w,h = cv2.boundingRect(contour)
    cv2.rectangle(image,(x,y),(x+w,y+h),(0,0,255),2)

    image = cv2.putText(image, "Width: " + str(w) , (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 4,(255,255,255), 3, cv2.LINE_AA)
    image = cv2.putText(image, "Height: " + str(h) , (20, 200), cv2.FONT_HERSHEY_SIMPLEX, 4,(255,255,255), 3, cv2.LINE_AA)

    return image, blank, w, h

Center = cv2.imread("Calib\Correlate\Single_cube_Center.png")
Left = cv2.imread("Calib\Correlate\Single_cube_Left.png")
Right = cv2.imread("Calib\Correlate\Single_cube_Right.png")

# h, w = Center.shape[:2]
# cen_h = h / 2
# cen_w = w / 2
# cv2.line(Center, (0, int(cen_h)), (w, int(cen_h)), (0, 0, 255), 2)
# cv2.line(Center, (int(cen_w), 0), (int(cen_w), h), (0, 0, 255), 2)

# h1, w1 = Left.shape[:2]
# cen_h1 = h1/2
# cen_w1 = w1/2
# cv2.line(Left, (0,int(cen_h1)), (w1,int(cen_h1)), (0,0,255), 2)
# cv2.line(Left, (int(cen_w1), 0), (int(cen_w1), h1), (0,0,255), 2)

# h2, w2 = Right.shape[:2]
# cen_h2 = h2/2
# cen_w2 = w2/2
# cv2.line(Right, (0,int(cen_h2)), (w1,int(cen_h2)), (0,0,255), 2)
# cv2.line(Right, (int(cen_w2), 0), (int(cen_w2), h2), (0,0,255), 2)

Center, BinC, _, h_C, = Binary(Center, [0, 0, 149], [255, 255, 255])
Left, BinL, w_L, _ = Binary(Left, [0, 0, 149], [255, 255, 255])
Right, BinR, w_R, _ = Binary(Right, [0, 0, 149], [255, 255, 255])

print("Center/Left: ",h_C/w_L)
print("Right/left: ", w_R/w_L)

# view_center = View(BinC, 0.3)
# view_left = View(BinL, 0.4)
# view_right = View(BinR, 0.4)

view_center = View(Center, 0.5*(1/1.72))
view_left = View(Left, 0.5)
view_right = View(Right, 0.5*(1/1.46666666))

cv2.imshow("Center", view_center)
cv2.imshow("Left", view_left)
cv2.imshow("Right", view_right)

cv2.waitKey(0)
cv2.destroyAllWindows()