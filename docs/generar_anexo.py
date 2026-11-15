import json,os
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
B=os.path.dirname(os.path.abspath(__file__))
results=json.load(open(B+'/resultados_prueba.json'))['escenarios'];r=results['NORMAL']
pdfmetrics.registerFont(TTFont('Dej','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejBold','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
styles={
 'title':ParagraphStyle('title',fontName='DejBold',fontSize=18,leading=26,textColor=colors.HexColor('#66343F'),spaceAfter=14),
 'head':ParagraphStyle('head',fontName='DejBold',fontSize=12.5,leading=17,textColor=colors.HexColor('#66343F'),spaceBefore=12,spaceAfter=7),
 'body':ParagraphStyle('body',fontName='Dej',fontSize=9.2,leading=14,spaceAfter=7),
 'small':ParagraphStyle('small',fontName='Dej',fontSize=8,leading=12,spaceAfter=5),
}
def P(x,style='body'):story.append(Paragraph(x,styles[style]))
def T(rows,widths):
 t=Table([[Paragraph(str(v),styles['small']) for v in row] for row in rows],colWidths=[v*cm for v in widths],repeatRows=1,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#F1E8E2')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,-1),.4,colors.HexColor('#DDD4D0')),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]));story.append(t);story.append(Spacer(1,10))
story=[]
P('BIOPRINT-VASC | Anexo de cálculo de Semana 1','title')
P('Universidad Mayor de San Andrés · Carrera de Informática · Métodos Numéricos')
P('Esta hoja complementaria recoge operaciones, referencias y verificaciones reproducibles de la web. Todos los parámetros son sintéticos; no es un modelo clínico.')
P('1. Formulación física y modelo continuo','head')
P('Se estudia la mitad del espacio entre dos microcanales ideales. El canal se fija a C(0)=1 y el plano medio no tiene flujo: C\'(L)=0. Con difusión efectiva D=0,002 mm²/s, consumo k=0,04 s⁻¹, L=0,15 mm:')
P('−D·C\'\' + k·C=0;  C(x)=cosh[√(k/D)(L−x)] / cosh[√(k/D)L].')
P('El valor analítico en la posición más alejada es C(L) = 0,81065848, adimensional. Cuando L aumenta a 0,40 mm, C(L) disminuye a 0,32521667 bajo los mismos D y k. No se infiere viabilidad celular real.')
P('2. Obtención completa del sistema 4 × 4','head')
P('Con N=4 volúmenes finitos: h=L/N=0,0375 mm; γ=k·h²/D=0,028125. Al integrar cada celda y usar la distancia h/2 al contorno izquierdo:')
P('Primera celda: (3+γ)C₁−C₂=2. Interiores: −Cᵢ₋₁+(2+γ)Cᵢ−Cᵢ₊₁=0. Última: −C₃+(1+γ)C₄=0.')
T([['Fila de A','Coeficientes','Componente de b'],['1','[3,028125; −1; 0; 0]','2'],['2','[−1; 2,028125; −1; 0]','0'],['3','[0; −1; 2,028125; −1]','0'],['4','[0; 0; −1; 1,028125]','0']],[3,9,4.6])
P('La matriz es simétrica definida positiva: zᵀAz = 2z₁² + Σ(zᵢ−zᵢ₊₁)² + γΣzᵢ² &gt; 0 para z no nulo. Por ello se justifica gradiente conjugado estándar.')
P('3. Operación manual inicial de Jacobi y Gauss-Seidel','head')
P('Condición inicial: C⁽⁰⁾=(0,0,0,0). Jacobi calcula las cuatro incógnitas usando solo el vector anterior. La primera entrada es 2/3,028125 = 0,6604747162; las restantes valen 0. Por tanto C⁽¹⁾=(0,6604747162; 0; 0; 0).')
P('Gauss-Seidel reutiliza inmediatamente los nuevos valores. En su primera pasada: C₁⁽¹⁾=2/3,028125; C₂⁽¹⁾=C₁⁽¹⁾/2,028125; C₃⁽¹⁾=C₂⁽¹⁾/2,028125; C₄⁽¹⁾=C₃⁽¹⁾/1,028125.')
from itertools import accumulate
x1=2/3.028125;x2=x1/2.028125;x3=x2/2.028125;x4=x3/1.028125
P(f'C⁽¹⁾(Gauss-Seidel)=[{x1:.10f}; {x2:.10f}; {x3:.10f}; {x4:.10f}].')
P('4. Factorización LU y gradiente conjugado','head')
P('LU (Doolittle): u₁₁=3,028125; ℓ₂₁=−1/u₁₁=−0,3302373581; u₂₂=2,028125−ℓ₂₁·(−1)=1,6978876419. Continuando, los pivotes U son [3,028125; 1,6978876419; 1,4391578768; 0,3332742014]. Los elementos subdiagonales de L son [−0,3302373581; −0,5889671232; −0,6948507986].')
P('Se resuelven Lz=b y UC=z mediante sustitución directa y regresiva. El vector calculado es C=[0,9511174701; 0,8801025891; 0,8338405934; 0,8110303644].')
P('Gradiente conjugado inicia C₀=0, r₀=b y p₀=b. El primer coeficiente es α₀=(r₀ᵀr₀)/(p₀ᵀAp₀)=1/3,028125=0,3302373581. Tras cuatro pasos, el residuo de CG es del orden de 10⁻¹⁵ en este sistema de cuatro incógnitas.')
P('5. Error algebraico, de malla y residuo','head')
P('Para cada método se calcula e_abs=||C_aprox−C_directa||∞, e_rel=e_abs/||C_directa||∞, e%=100·e_rel y residual=||Ay−b||₂. Distinto de esto, e_malla=||C_directa−C_exacta(nodos)||∞. Si se reescala C=Sy, el residual se mide sobre Ay−b del sistema reescalado.')
T([['Método','Iteraciones','Residual (norma 2)','Error abs. ∞'],*[[k,str(v['iterations']) if v['iterations'] else 'Directo',f"{v['residual']:.3e}",f"{v['absoluteError']:.3e}"] for k,v in r['methods'].items()]],[5.2,2.6,4.6,4.6])
P(f'El error máximo de discretización normal frente a la solución analítica en los centros es {r["gridError"]:.6f}. No corresponde al error de los solucionadores.')
P('6. Tres escenarios y condicionamiento','head')
T([['Caso','C(L) exacta','κ∞ de la matriz','Interpretación'],*[[k.replace('_',' '),f"{v['minExact']:.6f}",f"{v['condition']:.3e}",'Físico' if k=='ESTRES' else 'Algebraico' if k=='MAL_CONDICIONADO' else 'Referencia'] for k,v in results.items()]],[4.1,3.9,4.1,4.9])
P('Para el escenario mal condicionado se reescala con S=diag(1; 0,05; 0,005; 1), A\'=SAS, b\'=Sb y C=Sy. La matriz continúa siendo SPD, pero κ∞ aumenta. La concentración física resultante sigue siendo la misma que en NORMAL.')
P('7. Alcance y evidencias','head')
P('Los cálculos anteriores están implementados y son reproducibles en src/motor.js y tests/test_motor.js. El ejercicio de oxígeno corresponde al módulo 4 como experimento de referencia espacial; faltan los algoritmos de interpolación del módulo, además de raíces, integración y RK2/RK4 para la semana 2. La autorización del docente es necesaria para reemplazar los casos originales de SIMTELE-RISK.')
path=B+'/ANEXO_Calculos_Semana1.pdf'
doc=SimpleDocTemplate(path,pagesize=(21*cm,29.7*cm),leftMargin=2*cm,rightMargin=2*cm,topMargin=1.8*cm,bottomMargin=1.8*cm)
doc.build(story)
print(path)
