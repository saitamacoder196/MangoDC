import cv2

def View(imge2view, ratio):
    view = imge2view.copy()
    h, w = view.shape[:2]
    scaledH = int(h * ratio)
    scaledW = int(w * ratio)
    dim = (scaledW, scaledH)
    view = cv2.resize(view, dim, interpolation=cv2.INTER_AREA)

    return view

up_left_point = (280, 550)
bot_right_point =(2158, 1590)
save = True
name_Pic = "Light_Center.png"


img = cv2.imread(name_Pic)
if save:
    crop = img[up_left_point[1]:bot_right_point[1], up_left_point[0]:bot_right_point[0]]
    cv2.imwrite("Crop_"+name_Pic, crop)


cv2.rectangle(img, up_left_point, bot_right_point, (0,0,255), 1)
view = View(img, 0.3)
cv2.imshow("View", view)
cv2.waitKey(0)