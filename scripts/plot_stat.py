import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_excel("../docs/record/EMzhao_OpenStack_stat.xlsx")

stat = pd.DataFrame(columns=['srange', 'count'])
stat.loc[stat.shape[0]] = ["-2w", 0]
stat.loc[stat.shape[0]] = ["-2w~-5k", 0]
stat.loc[stat.shape[0]] = ["-5k~-1k", 0]
stat.loc[stat.shape[0]] = ["-1k~-500", 0]
stat.loc[stat.shape[0]] = ["-500~-100", 0]
stat.loc[stat.shape[0]] = ["-100", 0]
stat.loc[stat.shape[0]] = ["-50", 0]
stat.loc[stat.shape[0]] = ["0", 0]
stat.loc[stat.shape[0]] = ["50", 0]
stat.loc[stat.shape[0]] = ["100", 0]
stat.loc[stat.shape[0]] = ["100~500", 0]
stat.loc[stat.shape[0]] = ["500~1k", 0]
stat.loc[stat.shape[0]] = ["1k~5k", 0]
stat.loc[stat.shape[0]] = ["5k~2w", 0]
stat.loc[stat.shape[0]] = ["2w", 0]

x = [-20000, -19999, -5000, -1000, -500, -100, -50, 0, 50, 100, 101, 500, 1000, 5000, 20000]
y = [-19999, -5000, -1000, -500, -100, -99, -49, 1, 51, 101, 500, 1000, 5000, 20000, 20001]

for row in range(df.shape[0]):
    m = -df.iloc[row, 6]
    count = 0
    for i in range(15):
        if m >= x[i] and m < y[i]:
            stat.iloc[i, 1] += 1
            count += 1
    if count != 1:
        print(m)

plt.figure(figsize=(15, 5))
sns.barplot(x="srange", y="count", data=stat)
plt.xlabel(u'筹码')
plt.savefig("每局收益筹码的分布直方图.jpg")