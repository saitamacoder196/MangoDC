import cv2
import matplotlib.pyplot as plt
import numpy as np
def View(imge2view, ratio):
    view = imge2view
    h, w = view.shape[:2]
    scaledH = int(h * ratio)
    scaledW = int(w * ratio)
    dim = (scaledW, scaledH)
    view = cv2.resize(view, dim, interpolation=cv2.INTER_AREA)

    return view

def get_std_dev(ls):
    n = len(ls)
    mean = sum(ls) / n
    var = sum((x - mean)**2 for x in ls) / n
    std_dev = var ** 0.5
    return std_dev


image_test = cv2.imread("Calib\Raw\Light_Left_11.png")
# image_test = cv2.blur(image_test, (5, 5))

gray = cv2.cvtColor(image_test, cv2.COLOR_BGR2GRAY)

h, w = gray.shape

x = np.arange(0, w)
y = np.arange(0, h)

x_axis, y_axis = np.meshgrid(x, y) 

 
# Creating figure
fig = plt.figure(figsize =(14, 9))
ax = plt.axes(projection ='3d')
 
# Creating color map
my_cmap = plt.get_cmap('plasma')
 
# Creating plot
surf = ax.plot_surface(y_axis, x_axis,  gray, cmap = my_cmap, edgecolor ='none')
 
fig.colorbar(surf, ax = ax, shrink = 0.5, aspect = 5)
 
ax.set_title('Surface plot')

plt.show()


# view = View(image_test, 0.5)
# cv2.imshow("image", view)
# # cv2.imshow("crop", crop)
# cv2.waitKey(0)

print("Mean: ",np.mean(gray[0]))
print("STD: ", get_std_dev(gray[0]))
print("Min: ", min(gray[0]))
print("Max: ", max(gray[0]))
