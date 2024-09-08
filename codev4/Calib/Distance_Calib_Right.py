import cv2

image_from_right = cv2.imread('Calib/Raw/Right/Distance_Center.png')

h, w = image_from_right.shape[:2]

x0 = 1235
x1 = 1150
x2 = 1070
x3 = 985
x4 = 900
x5 = 820
x6 = 738
x7 = 653
x8 = 570
x9 = 488
x10 = 404
x11 = 324

cv2.putText(image_from_right, str(x0), (x0 + 2,400), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_8)
cv2.putText(image_from_right, str(x1), (x1 + 2,400), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_8)
cv2.putText(image_from_right, str(x2), (x2 + 2,400), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_8)
cv2.putText(image_from_right, str(x3), (x3 + 2,400), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_8)
cv2.putText(image_from_right, str(x4), (x4 + 2,400), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_8)
cv2.putText(image_from_right, str(x5), (x5 + 2,400), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_8)
cv2.putText(image_from_right, str(x6), (x6 + 2,400), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_8)
cv2.putText(image_from_right, str(x7), (x7 + 2,400), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_8)
cv2.putText(image_from_right, str(x8), (x8 + 2,400), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_8)
cv2.putText(image_from_right, str(x9), (x9 + 2,400), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_8)
cv2.putText(image_from_right, str(x10), (x10 + 2, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_8)
cv2.putText(image_from_right, str(x11), (x11 + 2, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_8)


cv2.line(image_from_right, (x0, 0), (x0, h), (0,0,255), 2)
cv2.line(image_from_right, (x1, 0), (x1, h), (0,0,255), 2)
cv2.line(image_from_right, (x2, 0), (x2, h), (0,0,255), 2)
cv2.line(image_from_right, (x3, 0), (x3, h), (0,0,255), 2)
cv2.line(image_from_right, (x4, 0), (x4, h), (0,0,255), 2)
cv2.line(image_from_right, (x5, 0), (x5, h), (0,0,255), 2)
cv2.line(image_from_right, (x6, 0), (x6, h), (0,0,255), 2)
cv2.line(image_from_right, (x7, 0), (x7, h), (0,0,255), 2)
cv2.line(image_from_right, (x8, 0), (x8, h), (0,0,255), 2)
cv2.line(image_from_right, (x9, 0), (x9, h), (0,0,255), 2)
cv2.line(image_from_right, (x10, 0), (x10, h), (0,0,255), 2)
cv2.line(image_from_right, (x11, 0), (x11, h), (0,0,255), 2)

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