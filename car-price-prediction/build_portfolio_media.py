#!/usr/bin/env python3
"""Reproduce the notebook's model evaluation and export LinkedIn-ready PNG figures.

Run inside this folder: python build_portfolio_media.py
Requires: pandas, numpy, matplotlib, scikit-learn.
The original notebook is preserved. For determinism, Decision Tree is seeded
with random_state=42 here (the original notebook left it unseeded).
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Lasso
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"assets"
OUT.mkdir(parents=True,exist_ok=True)
df=pd.read_csv(ROOT/"car_data.csv")
assert df.shape[0] == 301, "Please check that the original 301-row CSV is being used"
df=df.drop_duplicates().copy()
for col,mapping in {
    "Fuel_Type":{"Petrol":0,"Diesel":1,"CNG":2},
    "Selling_type":{"Dealer":0,"Individual":1},
    "Transmission":{"Manual":0,"Automatic":1},
}.items():
    df[col]=df[col].map(mapping)
assert df[["Fuel_Type","Selling_type","Transmission"]].notna().all().all()
df=df.loc[df.Present_Price!=df.Present_Price.max()].copy()
assert df.shape[0] == 298
X=df.drop(columns=["Car_Name","Selling_Price"])
y=df["Selling_Price"]
Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.2,random_state=42)
models={
    "Linear Regression":LinearRegression(),
    "Lasso":Lasso(alpha=.1),
    "Decision Tree":DecisionTreeRegressor(max_depth=29,random_state=42),
    "Random Forest":RandomForestRegressor(n_estimators=100,max_depth=20,min_samples_split=2,min_samples_leaf=1,random_state=42),
    "Extra Trees":ExtraTreesRegressor(n_estimators=68,max_depth=10,random_state=42),
}
result=[]
preds={}
for name,model in models.items():
    model.fit(Xtr,ytr)
    p=model.predict(Xte)
    preds[name]=p
    result.append({"Model":name,"R2":r2_score(yte,p),
                   "RMSE":np.sqrt(mean_squared_error(yte,p)),
                   "MAE":mean_absolute_error(yte,p)})
m=pd.DataFrame(result)
m.to_csv(OUT/"model_metrics_reproduced.csv",index=False)
best=m.set_index("Model").loc["Extra Trees"]
print(m.to_string(index=False,float_format=lambda n:f"{n:.4f}"))

BG="#071529"; PANEL="#10233d"; INK="#f1f7ff"
MUTED="#9fb8d0"; TEAL="#4dd4c0"; DIM="#567897"
plt.rcParams.update({"font.family":"DejaVu Sans","figure.facecolor":BG,"savefig.facecolor":BG})
fig=plt.figure(figsize=(16,9),dpi=150)
fig.text(.07,.87,"CAR PRICE PREDICTION",fontsize=32,fontweight="bold",color=INK)
fig.text(.07,.82,"Five regression models | 60 held-out test rows",fontsize=15,color=MUTED)
fig.text(.07,.71,f"301 source records     298 modelled     BEST R²  {best.R2:.3f}     TEST RMSE  {best.RMSE:.2f}",
         fontsize=18,color=TEAL,fontweight="bold")
ax=fig.add_axes([.17,.29,.31,.31],facecolor=PANEL)
sort=m.sort_values("R2",ascending=True)
ax.barh(sort.Model,sort.R2,color=[TEAL if v=="Extra Trees" else DIM for v in sort.Model])
ax.set_xlim(0,1.03)
ax.set_xlabel("Held-out R²",color=MUTED)
ax.tick_params(axis="both",colors=INK,length=0)
for s in ax.spines.values():s.set_visible(False)
ax.grid(axis="x",color="#294762",alpha=.5)
ax.set_axisbelow(True)
ax2=fig.add_axes([.59,.29,.30,.31],facecolor=PANEL)
pred=preds["Extra Trees"]
bound=max(max(yte),max(pred))*1.04
ax2.scatter(yte,pred,c=TEAL,alpha=.6,s=35)
ax2.plot([0,bound],[0,bound],"--",color="#67aaf9")
ax2.set_xlim(0,bound);ax2.set_ylim(0,bound)
ax2.set_xlabel("Actual selling price",color=MUTED)
ax2.set_ylabel("Predicted selling price",color=MUTED)
ax2.tick_params(axis="both",colors=INK)
for s in ax2.spines.values():s.set_visible(False)
ax2.grid(color="#294762",alpha=.45)
fig.text(.07,.14,f"EXTRA TREES    R² {best.R2:.3f}  |  RMSE {best.RMSE:.2f}  |  MAE {best.MAE:.2f}",color=TEAL,fontsize=20)
fig.text(.07,.08,"Single 80/20 split; source dataset price units unspecified; not a production benchmark",color=MUTED,fontsize=11)
fig.savefig(OUT/"car_price_portfolio_overview.png",dpi=150)
plt.close(fig)
fig=plt.figure(figsize=(14,8),dpi=150)
fig.text(.08,.87,"MODEL COMPARISON",color=INK,fontsize=30,fontweight="bold")
fig.text(.08,.81,"Test-set RMSE | Lower is better",color=MUTED,fontsize=15)
a=fig.add_axes([.31,.23,.59,.48],facecolor=PANEL)
s=m.sort_values("RMSE",ascending=False)
a.barh(s.Model,s.RMSE,color=[TEAL if z=="Extra Trees" else DIM for z in s.Model])
a.tick_params(axis="both",colors=INK,length=0)
a.set_xlabel("RMSE (source price units)",color=MUTED)
for spine in a.spines.values():spine.set_visible(False)
a.grid(axis="x",alpha=.4,color="#294762")
a.set_axisbelow(True)
fig.text(.08,.11,"301 source rows | 298 modelled | 60 test cases | Single split",color=MUTED,fontsize=11)
fig.savefig(OUT/"car_price_model_comparison.png",dpi=150)
plt.close(fig)
print("Wrote two PNGs and model_metrics_reproduced.csv to",OUT)
