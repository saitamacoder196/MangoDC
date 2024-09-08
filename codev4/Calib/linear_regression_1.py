import pandas as pd
from sklearn.linear_model import LinearRegression 
import numpy as np 
import matplotlib.pyplot as mpl

#doc du lieu tu tep co dinh dang csv luu vao bien df
df=pd.DataFrame()
df=pd.read_csv('Calib/Data/Center.csv', sep=',', header=0)


#lay gia tri cua cot 0 va cot 1 luu vao mang v va h dong thoi tach rieng tung gia tri trong mang
v=df.values[:,0].reshape(-1,1)
h=df.values[:,1].reshape(-1,1)

# #tao doi tuong de fit du lieu va tien haanh fit du lieu
reg = LinearRegression()
reg.fit(v,h)


a=reg.coef_#he so uoc luong cho bai toan hoi quy tuyen tinh
b=reg.intercept_#so hang doc lap trong mo hinh tuyen tinh

print("a,b: ",a[0][0],",",b[0])

print('y=a*v+b')

y=a*v+b

# print('y:\n',y)

mpl.figure('Do thi')
mpl.title('Regression: y=a*x+b')
mpl.xlabel('Do cao ban co (pixel)')
mpl.ylabel(f'Dien tich thuc cua mot pixel ($mm^2$/pixel)')
mpl.grid(1)
mpl.scatter(v,h,c='blue',alpha=0.6)
mpl.subplots_adjust(left=0.2)
mpl.plot(v,y,color='red',label='y= '+ str(round(a[0][0], 8))+'x + '+str(round(b[0], 5)))
mpl.legend()

mpl.show()








