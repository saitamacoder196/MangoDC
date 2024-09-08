import pandas as pd 
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import numpy as np 
import matplotlib.pyplot as plt

#doc du lieu tu tep csv
data=pd.DataFrame()
data=pd.read_csv('Calib/Data/Center.csv',sep=',',header=0)

#chuyen ma tran co 1 hang, n cot thanh ma tran co n hang 1 cot
nb_pixel=data.values[:,1].reshape(-1,1)#bien phu thuoc
height=data.values[:,0].reshape(-1,1)#bien doc lap

poly_features = PolynomialFeatures(degree=2, include_bias=False)
X_poly = poly_features.fit_transform(height)

lin_reg = LinearRegression()

lin_reg.fit(X_poly, nb_pixel)

a=lin_reg.coef_#he so uoc luong cho bai toan hoi quy tuyen tinh
b=lin_reg.intercept_#so hang doc lap trong mo hinh tuyen tinh

print(a, b)

#ham hoi quy tim duoc dua vao cac he so vua tinh phia tren

plt.plot(height, nb_pixel, "b.")
plt.plot(height,lin_reg.predict(X_poly),"r-")
plt.show() 
