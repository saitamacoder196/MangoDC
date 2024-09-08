import pandas as pd
import numpy as np
from sklearn.metrics import r2_score

csvfile = "Check Accuracy/Areas_CC.csv"
df = pd.read_csv(csvfile)
df= df.drop(df.columns[0], axis=1) #Bỏ cột ID

"""ĐẦU"""
Head = df['Head'].values

AVR = np.mean(Head)
STD = np.std(Head)
MAE = np.mean(np.abs(Head - 100))

print("<==================HEAD==================>")
print("Average: ", np.round(AVR, 2))
print("Standard deviation: ", np.round(STD, 2))
print("Mean absolute error: ", np.round(MAE, 2))

"""ĐUÔI"""
Tail = df['Tail'].values

AVR = np.mean(Tail)
STD = np.std(Tail)
MAE = np.mean(np.abs(Tail - 100))

print("<==================TAIL==================>")
print("Average: ", np.round(AVR, 2))
print("Standard deviation: ", np.round(STD, 2))
print("Mean absolute error: ", np.round(MAE, 2))

"""4 MẶT CHÍNH"""
Main = df[['Center 11','Center 12','Center 13','Center 14','Center 15','Center 16','Center 17',
        'Center 21','Center 22','Center 23',
        'Center 31','Center 32','Center 33','Center 34','Center 35','Center 36','Center 37',
        'Center 41','Center 42','Center 43']].values
MAE = []
AVR = []
STD = []
for i in range(len(Main)):
    MAE.append(np.mean(np.abs(Main[i] - 100)))
    AVR = np.mean(Main[i])
    STD = np.std(Main[i])

MAE = np.mean(MAE)
AVR = np.mean(AVR)
STD = np.mean(STD)

print("<==================MAIN==================>")
print("Average: ", np.round(AVR, 2))
print("Standard deviation: ", np.round(STD, 2))
print("Mean absolute error: ", np.round(MAE, 2))

"""(ĐẦU, ĐUÔI, 4 MẶT CHÍNH)"""
All = df.values

MAE = []
AVR = []
STD = []
for i in range(len(Main)):
    MAE.append(np.mean(np.abs(All[i] - 100)))
    AVR = np.mean(All[i])
    STD = np.std(All[i])

MAE = np.mean(MAE)
AVR = np.mean(AVR)
STD = np.mean(STD)

print("<==================ALL===================>")
print("Average: ", np.round(AVR, 2))
print("Standard deviation: ", np.round(STD, 2))
print("Mean absolute error: ", np.round(MAE, 2))