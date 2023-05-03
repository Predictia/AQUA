from modules import *
import matplotlib.pyplot as plt
import datetime
# file_path = "/home/dese28/dese28422/one_pass/config.yml"
from aqua import Reader
reader = Reader(model = 'FESOM', exp = 'tco3999-ng5', source="interpolated_global_TS")
data = reader.retrieve()
data=data.drop("latitude")
data=data.drop("longitude")
data=data.drop("ocpt")


data=data.rename({"salt":"so"})
data=data.rename({"temp":"thetao"})

data = data.resample(time='7.39H').mean()
time = np.arange('2011-01-01', '2013-01-01', dtype='datetime64[D]')
data["time"]=time

thetao=data.thetao
unique_years = np.unique(data['time.year'])
merged_ds = xr.Dataset()
for year in [2011,2012]:
    for month in range(1,13):
        thetao_new = monthly_mean_opa.compute(data.sel(time=str(year)+'-'+str(month)).thetao)
        merged_ds = xr.merge([merged_ds, thetao_new])


  
ds2=merged_ds            



weights=np.cos(np.deg2rad(ds2.lat))
t3d=ds2.thetao.resample(time="Y").mean()
t3dw=t3d.weighted(weights)
tg=t3d.mean(("lat","lon"))
tgw=t3dw.mean(("lat","lon"))

levs=t3d.height
ilev0=0

for ilev in range(len(levs)):
    tlev = levs[ilev]
    if tlev<= 500:
        ilev500=ilev
    if tlev<= 1000:
        ilev1000=ilev
    if tlev<= 2000:
        ilev2000=ilev
    if tlev<= 3000:
        ilev3000=ilev
    if tlev<= 4000:
        ilev4000=ilev
    if tlev<= 5000:
        ilev5000=ilev


print(ilev0,ilev500,ilev1000,ilev2000,ilev3000,ilev4000,ilev5000)


tga=tg-tg[0,]

# Now standardised with respect to the temporal STD at each respective depth
tgs=tga/tga.std("time")
# And we perform the corresponding hovmoller plot
tgst=tgs.transpose()
tgst.plot()

plt.title("Stand. GLOBAL temperature anom (vs first value)")
plt.ylim((5500,0))
plt.savefig('1st.png')
plt.clf()


 # Now the same but for the anomaly with respet to the temporal mean
tga2=tg-tg.mean("time")
# Now standardised with respect to the temporal STD at each respective depth
tgs2=tga2/tga2.std("time")
# And we perform the corresponding hovmoller plot
tgs2t=tgs2.transpose()
tgs2t.plot()

plt.title("Stand. GLOBAL temperature anom (vs time mean)")
plt.ylim((5500,0))
plt.savefig('2nd.png')
plt.clf()

tgt=tg.transpose()
tgt.plot()

plt.title("GLOBAL temperature (full value)")
plt.ylim((5500,0))
plt.savefig('3rd.png')
plt.clf()
#############################################################
tga0=tgs[:,ilev0]
tga500=tgs[:,ilev500]
tga1000=tgs[:,ilev1000]
tga2000=tgs[:,ilev2000]
tga3000=tgs[:,ilev3000]
tga4000=tgs[:,ilev4000]
tga5000=tgs[:,ilev5000]
tga0.plot.line()
tga500.plot.line()
tga1000.plot.line()
tga2000.plot.line()
tga3000.plot.line()
tga4000.plot.line()
tga5000.plot.line()

#t0.plot.line(color="blue",linestyle="dotted")
plt.title("Stand GLOBAL temperature anom (vs initial value)")
plt.legend(["0","500","1000","2000","3000","4000","5000"], loc='best')
plt.savefig('4th.png')
plt.clf()


# We now extract and plot the timeseries for the standardise global anomalies at different levels
tga0b=tgs2[:,ilev0]
tga500b=tgs2[:,ilev500]
tga1000b=tgs2[:,ilev1000]
tga2000b=tgs2[:,ilev2000]
tga3000b=tgs2[:,ilev3000]
tga4000b=tgs2[:,ilev4000]
tga5000b=tgs2[:,ilev5000]
tga0b.plot.line()
tga500b.plot.line()
tga1000b.plot.line()
tga2000b.plot.line()
tga3000b.plot.line()
tga4000b.plot.line()
tga5000b.plot.line()

#t0.plot.line(color="blue",linestyle="dotted")
plt.title("Stand GLOBAL temperature anom (vs time mean)")
plt.legend(["0","500","1000","2000","3000","4000","5000"], loc='best')
plt.savefig('5th.png')
plt.clf()


# And we plot the absolute temperature mean values
tg0=tg[:,ilev0]
tg500=tg[:,ilev500]
tg1000=tg[:,ilev1000]
tg2000=tg[:,ilev2000]
tg3000=tg[:,ilev3000]
tg4000=tg[:,ilev4000]
tg5000=tg[:,ilev5000]
tg0.plot.line()
tg500.plot.line()
tg1000.plot.line()
tg2000.plot.line()
tg3000.plot.line()
tg4000.plot.line()
tg5000.plot.line()

#t0.plot.line(color="blue",linestyle="dotted")
plt.title("GLOBAL temperature mean (full value)")
plt.legend(["0","500","1000","2000","3000","4000","5000"], loc='best')
plt.savefig('6th.png')
plt.clf()

