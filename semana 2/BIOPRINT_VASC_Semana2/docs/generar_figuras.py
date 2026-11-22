"""Gráficos verificables derivados de numericos.simulate, no ilustrativos."""
import sys
from pathlib import Path
import math
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from numericos import simulate,CASES,SCENARIOS
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
figs=root/'docs'/'figuras';figs.mkdir(exist_ok=True)
COL=['#713849','#bf9355','#527f72','#86769d','#b86b6b','#6093af']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.titlesize':11,'axes.spines.top':False,'axes.spines.right':False})
for case in CASES:
 result=simulate(case,'NORMAL')
 for ix,graph in enumerate(result['charts']):
  fig,ax=plt.subplots(figsize=(8.6,3.4))
  for k,serie in enumerate(graph['series']):
   xx=[p[0] for p in serie['points']]; yy=[p[1] for p in serie['points']]
   if 'Nodos' in serie['name']: ax.scatter(xx,yy,s=15,c=COL[k%len(COL)],label=serie['name'],zorder=3)
   else: ax.plot(xx,yy,lw=1.7,c=COL[k%len(COL)],label=serie['name'])
  ax.set(xlabel=graph['xLabel'],ylabel=graph['yLabel'],title=graph['title']);ax.grid(alpha=.2)
  ax.legend(fontsize=7,loc='best',ncol=min(3,len(graph['series'])))
  fig.tight_layout();fig.savefig(figs/f'{case}_{ix+1}.png',dpi=170);plt.close(fig)
# Comparación de 12 escenarios con métricas significativas por caso
labels={'extrusion':('Tiempo hasta detener la extrusión (s)','tiempo_parada_s'),
        'hidrogel':('Tiempo hasta el umbral (días)','tiempo_umbral_dias'),
        'oscilaciones':('Error máximo de RK4 (m)','error_max_RK4_m'),
        'sensores':('Error máximo de Lagrange (adimensional)',None)}
for case,(title,key) in labels.items():
 vals=[]
 for s in SCENARIOS:
  result=simulate(case,s)
  v=result['reference'][key] if key else result['methods'][0]['error_abs']
  vals.append(v)
 fig,ax=plt.subplots(figsize=(8.4,3.6));bars=ax.bar(['Normal','Estrés','Mal condicionado'],vals,color=COL[:3],width=.55)
 ax.set_ylabel(title);ax.set_title('Comparación de escenarios · '+result['title']);ax.grid(alpha=.15,axis='y');ax.set_axisbelow(True)
 for bar,v in zip(bars,vals):ax.text(bar.get_x()+bar.get_width()/2,bar.get_height(),f'{v:.4g}',ha='center',va='bottom',fontsize=8)
 if max(vals)/max(min([v for v in vals if v>0],default=1),1e-30)>1000:ax.set_yscale('symlog',linthresh=1e-3)
 fig.tight_layout();fig.savefig(figs/f'{case}_comparacion.png',dpi=170);plt.close(fig)
print('figures',len(list(figs.glob('*.png'))))
