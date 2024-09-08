import cv2


image_from_right = cv2.imread('Calib/Raw/Center/All_cube_Right.png')

h, w = image_from_right.shape[:2]

y0 = 786
y1 = 711
y2 = 642
y3 = 570
y4 = 502
y5 = 428
y6 = 355

cv2.putText(image_from_right, str(y0), (20, y0 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3, cv2.LINE_8)
cv2.putText(image_from_right, str(y1), (20, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3, cv2.LINE_8)
cv2.putText(image_from_right, str(y2), (20, y2 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3, cv2.LINE_8)
cv2.putText(image_from_right, str(y3), (20, y3 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3, cv2.LINE_8)
cv2.putText(image_from_right, str(y4), (20, y4 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3, cv2.LINE_8)
cv2.putText(image_from_right, str(y5), (20, y5 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3, cv2.LINE_8)
cv2.putText(image_from_right, str(y5), (20, y6 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3, cv2.LINE_8)

cv2.line(image_from_right, (0, y0), (w, y0), (0,0,255), 2)
cv2.line(image_from_right, (0, y1), (w, y1), (0,0,255), 2)
cv2.line(image_from_right, (0, y2), (w, y2), (0,0,255), 2)
cv2.line(image_from_right, (0, y3), (w, y3), (0,0,255), 2)
cv2.line(image_from_right, (0, y4), (w, y4), (0,0,255), 2)
cv2.line(image_from_right, (0, y5), (w, y5), (0,0,255), 2)
cv2.line(image_from_right, (0, y6), (w, y6), (0,0,255), 2)

def View(imge2view, ratio):
    view = imge2view.copy()
    h, w = view.shape[:2]
    scaledH = int(h * ratio)
    scaledW = int(w * ratio)
    dim = (scaledW, scaledH)
    view = cv2.resize(view, dim, interpolation=cv2.INTER_AREA)

    return view

view = View(image_from_right, 0.5)

cv2.imshow("View", view)
cv2.waitKey(0)
cv2.destroyAllWindows()