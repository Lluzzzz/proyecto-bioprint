"""Informe UMSA: ecuaciones OMML nativas editables, experimentos S2 y fallos.
Requisitos de autoría solamente: python-docx, matplotlib (figuras ya generadas).
"""
from pathlib import Path
import sys,math
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from numericos import simulate,SCENARIOS,CASES
from docx import Document
from docx.shared import Cm,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

BURG='713849';DARK='3C3237';GREY='71696D';GOLD='C59B59';LINE='E9DEDB';PALE='FAF7F3'
def rgb(x):return RGBColor.from_string(x)
def H(doc,title,lvl=1):p=doc.add_paragraph(style=f'Heading {lvl}');p.add_run(title);return p
def P(doc,text,bold_start=None):
 p=doc.add_paragraph(style='Normal')
 if bold_start and text.startswith(bold_start):p.add_run(bold_start).bold=True;p.add_run(text[len(bold_start):])
 else:p.add_run(text)
 return p

def bullet(doc,text):p=doc.add_paragraph(style='List Bullet');p.add_run(text);return p

def fnum(a):
 if a is None:return '—'
 if not isinstance(a,(int,float)):return str(a)
 if a!=0 and (abs(a)<.0001 or abs(a)>1e4):return f'{a:.3e}'
 return f'{a:.6f}'.rstrip('0').rstrip('.') if a!=0 else '0'

def tab(doc,headers,rows,widths=None):
 table=doc.add_table(rows=1,cols=len(headers));table.alignment=WD_TABLE_ALIGNMENT.CENTER;table.autofit=False
 if widths:
  for i,width in enumerate(widths):table.columns[i].width=Cm(width)
 for i,title in enumerate(headers):
  cell=table.cell(0,i);cell.text=str(title)
  for run in cell.paragraphs[0].runs:run.bold=True;run.font.size=Pt(8.25);run.font.color.rgb=rgb(BURG)
 for ri,row in enumerate(rows):
  cells=table.add_row().cells
  for j,text in enumerate(row):
   cells[j].text=str(text)
   cells[j].vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
   for pp in cells[j].paragraphs:
    pp.paragraph_format.space_after=Pt(1)
    for r in pp.runs:r.font.size=Pt(8.25)
   if ri%2==0:
    tcPr=cells[j]._tc.get_or_add_tcPr();sh=OxmlElement('w:shd');sh.set(qn('w:fill'),PALE);tcPr.append(sh)
 for row in table.rows:
  for cell in row.cells:
   tcPr=cell._tc.get_or_add_tcPr();bd=OxmlElement('w:tcBorders');b=OxmlElement('w:bottom');b.set(qn('w:val'),'single');b.set(qn('w:sz'),'4');b.set(qn('w:color'),LINE);bd.append(b);tcPr.append(bd)
 trPr=table.rows[0]._tr.get_or_add_trPr();hdr=OxmlElement('w:tblHeader');hdr.set(qn('w:val'),'true');trPr.append(hdr)
 doc.add_paragraph().paragraph_format.space_after=Pt(0)
 return table

def math_run(par,t):
 r=OxmlElement('m:r');tx=OxmlElement('m:t');tx.text=str(t);r.append(tx);par.append(r)
def math_frac(par,num,den):
 f=OxmlElement('m:f');n=OxmlElement('m:num');d=OxmlElement('m:den');math_run(n,num);math_run(d,den);f.append(n);f.append(d);par.append(f)
def math_sup(par,base,exponent):
 e=OxmlElement('m:sSup');baseel=OxmlElement('m:e');sup=OxmlElement('m:sup');math_run(baseel,base);math_run(sup,exponent);e.append(baseel);e.append(sup);par.append(e)
def math_root(par,rad):
 e=OxmlElement('m:rad');pr=OxmlElement('m:radPr');deg=OxmlElement('m:degHide');deg.set(qn('m:val'),'1');pr.append(deg);degel=OxmlElement('m:deg');body=OxmlElement('m:e');math_run(body,rad);e.extend((pr,degel,body));par.append(e)
def math_matrix(par,matrix):
 d=OxmlElement('m:d');pr=OxmlElement('m:dPr');begin=OxmlElement('m:begChr');begin.set(qn('m:val'),'[');end=OxmlElement('m:endChr');end.set(qn('m:val'),']');pr.append(begin);pr.append(end);d.append(pr);m=OxmlElement('m:m')
 for row in matrix:
  mr=OxmlElement('m:mr')
  for a in row:
   e=OxmlElement('m:e');math_run(e,a);mr.append(e)
  m.append(mr)
 ewrap=OxmlElement('m:e');ewrap.append(m);d.append(ewrap);par.append(d)
def Eq(doc,*items):
 p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.space_before=Pt(5);p.paragraph_format.space_after=Pt(9);p.paragraph_format.keep_together=True
 para=OxmlElement('m:oMathPara');equ=OxmlElement('m:oMath')
 for item in items:
  if isinstance(item,str):math_run(equ,item)
  elif item[0]=='frac':math_frac(equ,item[1],item[2])
  elif item[0]=='sup':math_sup(equ,item[1],item[2])
  elif item[0]=='root':math_root(equ,item[1])
  elif item[0]=='matrix':math_matrix(equ,item[1])
 para.append(equ);p._p.append(para)
 return p

def fig(doc,name,caption,w=14.8):
 p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.keep_with_next=True
 p.add_run().add_picture(str(ROOT/'docs'/'figuras'/name),width=Cm(w))
 cp=doc.add_paragraph();cp.alignment=WD_ALIGN_PARAGRAPH.CENTER;cp.paragraph_format.space_after=Pt(8)
 r=cp.add_run(caption);r.italic=True;r.font.size=Pt(8.4);r.font.color.rgb=rgb(GREY)

def page(doc):doc.add_page_break()

D=Document();section=D.sections[0]
section.page_width=Cm(21);section.page_height=Cm(29.7);section.top_margin=Cm(1.9);section.bottom_margin=Cm(1.75);section.left_margin=Cm(2.05);section.right_margin=Cm(1.9)
section.different_first_page_header_footer=True
st=D.styles['Normal'];st.font.name='Carlito';st.font.size=Pt(10.5);st.font.color.rgb=rgb(DARK);st.paragraph_format.line_spacing=1.13;st.paragraph_format.space_after=Pt(5)
for lvl,size in [(1,16),(2,12.3),(3,11)]:
 sty=D.styles[f'Heading {lvl}'];sty.font.name='Noto Serif';sty.font.size=Pt(size);sty.font.bold=True;sty.font.color.rgb=rgb(BURG)
 sty.paragraph_format.space_before=Pt(13 if lvl==1 else 9);sty.paragraph_format.space_after=Pt(7 if lvl==1 else 4);sty.paragraph_format.keep_with_next=True
foot=section.footer.paragraphs[0];foot.alignment=WD_ALIGN_PARAGRAPH.RIGHT;foot.add_run('BIOPRINT-VASC  ·  UMSA  ·  Métodos Numéricos  ·  Semana 2').font.size=Pt(8)

# Carátula sin tabla ni líneas
p=D.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.space_before=Pt(10);p.add_run().add_picture(str(ROOT/'assets'/'escudo_umsa.png'),height=Cm(6.5))
def centered(text,size=11,bold=False,color=DARK,space=3):
 p=D.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.space_before=Pt(space);r=p.add_run(text);r.font.name='Noto Serif' if bold else 'Carlito';r.font.size=Pt(size);r.bold=bold;r.font.color.rgb=rgb(color);return p
centered('UNIVERSIDAD MAYOR DE SAN ANDRÉS',16,True,BURG,14)
centered('CARRERA DE INFORMÁTICA',13,True,DARK,2)
centered('MATERIA: MÉTODOS NUMÉRICOS',11.5,True,DARK,3)
centered('BIOPRINT-VASC',20,True,BURG,21)
centered('Modelación y análisis numérico de procesos de bioimpresión 3D',12,False,DARK,7)
centered('INFORME DE EXPERIMENTOS Y FALLOS DETECTADOS — SEMANA 2',11,True,DARK,10)
centered('Integrantes',11.4,True,BURG,22)
for line in ['Carlos Illed Burgoa Orellana — C.I. 14478827 LP',
             'Deivid Enrique Mamani Trujillo — C.I. 7235715-1',
             'Carlos Andrés Mamani Mamani — C.I. 8439346',
             'Luz Gabriela Castañeta Tarquino — C.I. 8467269 LP']:
 centered(line,10,False,DARK,3)
centered('La Paz, Bolivia · Noviembre de 2026',10.3,False,GREY,23)
page(D)

H(D,'1. Resumen del avance')
P(D,'Para la segunda semana integramos los métodos que faltaban en BIOPRINT-VASC. La web ejecuta los cuatro casos biomédicos y permite comparar las condiciones NORMAL, ESTRÉS y MAL CONDICIONADO. También se implementó una base de datos SQLite que guarda los parámetros, los resultados, las trazas y los gráficos. El programa está diseñado con fines educativos y utiliza datos sintéticos.')
P(D,'El trabajo responde a la consigna de semana 2 de Métodos Numéricos: interpolación, raíces, integración y ecuaciones diferenciales; cuatro módulos con escenario normal y dos gráficos por caso; escenarios adicionales; persistencia y reporte de fallos. El docente aprobó el cambio de temática hacia bioimpresión, según la confirmación del equipo.')
H(D,'2. Objetivo y alcance')
P(D,'Objetivo general: implementar y contrastar los métodos numéricos de la segunda fase en modelos simples de procesos relacionados con la bioimpresión 3D, y construir una plataforma que permita ejecutar, guardar, recuperar y repetir simulaciones.')
for s in ['Programar bisección, Newton-Raphson y secante; trapecio, Simpson 1/3 y Romberg; Lagrange, Newton por diferencias divididas y splines; RK2 de punto medio y RK4 clásico.',
          'Mostrar resultados normales y escenarios de estrés y mal condicionamiento con al menos dos gráficos por módulo.',
          'Aplicar errores absoluto, relativo y porcentual cuando corresponda; residuales y sensibilidad en problemas que lo requieran.',
          'Comprobar el historial tras detener y reiniciar la aplicación, recuperando entradas, iteraciones, curvas y referencias.']:
 bullet(D,s)
H(D,'3. Arquitectura de la plataforma')
P(D,'La interfaz usa HTML, CSS y JavaScript sin librerías externas. El servidor Python app.py recibe peticiones HTTP; numericos.py ejecuta los cálculos y SQLite almacena las sesiones. La aplicación se abre con python app.py y luego http://127.0.0.1:8000. Abrir index.html por separado no activa los cálculos del servidor ni la base de datos.')
tab(D,['Componente','Responsabilidad','Evidencia'],[
 ('numericos.py','Cuatro modelos y métodos numéricos.','9 pruebas unitarias; 12 combinaciones.'),
 ('app.py','API REST local y base SQLite.','HTTP, reinicio y SHA-256.'),
 ('index.html / src','Panel general, 4 módulos, gráficos, tablas e historial.','Capturas de QA visual con API de prueba.'),
 ('docs/esquema.sql','Seis entidades relacionales con claves foráneas.','Consultas e integridad verificadas.')],[4.1,7.2,5.6])

H(D,'4. Cobertura matemática de la semana 2')
tab(D,['Familia','Algoritmos integrados','Módulo'],[
 ('Raíces','Bisección, Newton-Raphson, secante','Extrusión e hidrogel'),
 ('Integración','Trapecio compuesto, Simpson 1/3 compuesto, Romberg','Extrusión y oscilaciones'),
 ('EDO','Runge-Kutta 2 (punto medio) y RK4 clásico','Extrusión y oscilaciones'),
 ('Interpolación','Lagrange baricéntrico, Newton dividido, spline cúbico natural','Sensores'),
 ('Sistemas lineales S1','Jacobi, Gauss-Seidel, LU, gradiente conjugado, directa','Calibración SPD de hidrogel'),
 ('Errores','Absoluto, relativo, porcentual, residuo, sensibilidad','Transversal')],[3.25,8.15,5.5])

H(D,'5. Módulo 1: parada controlada de extrusión')
P(D,'Se idealiza la disminución del caudal de biotinta tras una orden de parada. Q se mide en mL/s, a en mL/s², V en mL y t en segundos. El modelo no incluye tixotropía ni viscoelasticidad.')
Eq(D,'dQ/dt = −a ;    dV/dt = Q ;    Q(0)=q₀ ;    V(0)=0')
Eq(D,'T = ',('frac','q₀','a'),' ;     V(T) = ',('frac','q₀²','2a'))
P(D,'Para q₀=1,2 mL/s y a=0,4 mL/s², la referencia da T=3 s y V(T)=1,8 mL. La integración de la función lineal Q(t)=q₀−at permite contrastar trapecio, Simpson y Romberg; la EDO conjunta se aproxima con RK2 y RK4.')
H(D,'5.1 Procedimientos de raíces')
Eq(D,'f(t)=q₀−at ;   tₖ₊₁ = ',('frac','aₖ+bₖ','2'),'    (bisección)')
Eq(D,'tₖ₊₁ = tₖ − ',('frac','f(tₖ)','fʹ(tₖ)'),'    (Newton-Raphson)')
Eq(D,'tₖ₊₁ = tₖ − ',('frac','f(tₖ)(tₖ−tₖ₋₁)','f(tₖ)−f(tₖ₋₁)'),'    (secante)')
P(D,'Se inicia bisección en [0,1,8T], que encierra la raíz. En la versión lineal, Newton y secante llegan a la solución en pocos pasos. Para el subexperimento mal condicionado se aplica g(t)=[q₀−at]³: la raíz no cambia, pero gʹ(T)=0, por lo que el residual puede resultar engañosamente pequeño.')
H(D,'5.2 Procedimientos de integración y EDO')
Eq(D,'I ≈ ',('frac','h','2'),' [f(a)+2Σ f(tᵢ)+f(b)]     (trapecio)')
Eq(D,'I ≈ ',('frac','h','3'),' [f(a)+4Σf(tᵢ impar)+2Σf(tᵢ par)+f(b)]')
Eq(D,'Rₖ,ⱼ = Rₖ,ⱼ₋₁ + ',('frac','Rₖ,ⱼ₋₁−Rₖ₋₁,ⱼ₋₁','4ʲ−1'),'     (Romberg)')
P(D,'RK2 usa la variante de punto medio: k₁=F(tᵢ,yᵢ), k₂=F(tᵢ+h/2,yᵢ+h·k₁/2) y yᵢ₊₁=yᵢ+h·k₂. RK4 combina cuatro pendientes con pesos 1,2,2,1. En este caso lineal ambos reproducen V(T) con errores cercanos al redondeo.')
R=simulate('extrusion','NORMAL')
tab(D,['Método','Resultado','Error abs.','Iter. / n'],[[m['method'],fnum(m['value']),fnum(m['error_abs']),m['iterations']] for m in R['methods']],[5.3,4.1,4.1,3.4])
page(D)

H(D,'6. Módulo 2: degradación del hidrogel')
P(D,'Representamos un indicador hipotético D(t) de deterioro, con t en días. Usamos D₀=0,10; α=0,07 día⁻¹; β=0,004 día⁻² y umbral u=0,65. Estos parámetros no provienen de ensayos materiales.')
Eq(D,'D(t)=D₀+αt+βt² ;    f(t)=D(t)−u')
Eq(D,'t = ',('frac','2(u−D₀)','α+√(α²+4β(u−D₀))'))
P(D,'Sustituyendo valores se obtiene t*=5,88087 días (solo como índice temporal del modelo). Los tres métodos de raíces se comparan con esta solución cuadrática verificable.')
H(D,'6.1 Sistemas lineales SPD de calibración')
P(D,'Como prueba controlada se elige x*=(D₀,α,β,u)ᵀ y A tridiagonal SPD de tamaño 4×4. Se calcula b=A x*; de esta manera conocemos la solución exacta desde el inicio y podemos medir el error de los cuatro solucionadores.')
Eq(D,'A = ',('matrix',[['4','−1','0','0'],['−1','4','−1','0'],['0','−1','4','−1'],['0','0','−1','4']]),' ;  x = ',('matrix',[['0,10'],['0,07'],['0,004'],['0,65']]))
Eq(D,'b = ',('matrix',[['0,33'],['0,176'],['−0,704'],['2,596']]))
P(D,'Desde x⁽⁰⁾=0, Jacobi da x⁽¹⁾=(0,0825;0,044;−0,176;0,649)ᵀ. Gauss-Seidel reutiliza los componentes actualizados; LU resuelve dos sistemas triangulares; gradiente conjugado se aplica porque A=Aᵀ y xᵀAx>0 para todo x distinto de cero.')
Eq(D,'Aʹ=SAS ;    bʹ=Sb ;    x=Sy     (reescalamiento SPD)')
P(D,'En el escenario MAL CONDICIONADO se usa S=diag(1;0,05;0,005;1). La condición en norma infinito aumenta de 2,727 a aproximadamente 47 821, pero x recuperado debe seguir igual a x*. La dificultad es numérica, no una degradación adicional del hidrogel.')
R=simulate('hidrogel','NORMAL')
tab(D,['Método','Iteraciones','Error abs.','Estado'],[[m['method'],m['iterations'],fnum(m['error_abs']),'Sí' if m['converged'] else 'No'] for m in R['methods']],[7,2.7,3.6,3.5])

H(D,'7. Módulo 3: oscilaciones del cabezal')
P(D,'Se considera un sistema libre masa–resorte–amortiguador. x es desplazamiento en metros, c amortiguamiento en N·s/m, m masa en kg y k rigidez en N/m. El modelo no reproduce una impresora concreta.')
Eq(D,'mxʺ(t)+cxʹ(t)+kx(t)=0 ;    x(0)=x₀ ;    xʹ(0)=v₀')
Eq(D,'α = ',('frac','c','2m'),' ;    ωd = √(k/m−α²)')
Eq(D,'x(t)=e⁻ᵅᵗ [x₀ cos(ωd t)+',('frac','v₀+αx₀','ωd'),'sin(ωd t)]')
P(D,'Se compara RK2 de punto medio y RK4 con la solución anterior; adicionalmente se calcula J=∫₀ᵀx(t)²dt por trapecio, Simpson y Romberg, tomando como referencia un Simpson muy refinado. En NORMAL con n=80, el error máximo de RK2 es aproximadamente 1,478×10⁻³ m frente a 1,198×10⁻⁵ m de RK4.')
R=simulate('oscilaciones','NORMAL')
tab(D,['Método','Resultado / indicador','Error abs.'],[[m['method'],fnum(m['value']),fnum(m['error_abs'])] for m in R['methods']],[6.3,5.2,5.4])
H(D,'7.1 Escenario numéricamente sensible')
P(D,'El caso MAL CONDICIONADO acerca c a su valor crítico 2√(mk), haciendo muy pequeño ωd. La sensibilidad del cálculo de las raíces características crece; el programa evalúa sin(ωd t)/ωd con una aproximación estable cuando ωd t es pequeño. No se trata de un diagnóstico de vibración peligrosa.')
page(D)

H(D,'8. Módulo 4: reconstrucción de sensores')
P(D,'En NORMAL se usan seis nodos de una señal sintética s(t)=0,65+0,25e⁻ᵗ⁄⁴ (sin unidades). El algoritmo oculta 100 puntos de prueba, interpola los nodos disponibles y compara las predicciones contra la expresión conocida. En ESTRÉS se agrega ruido determinista a los nodos; en MAL CONDICIONADO se utiliza el benchmark matemático de Runge con 15 nodos equiespaciados.')
Eq(D,'P(x)=Σᵢ yᵢ Lᵢ(x) ;    Lᵢ(x)=Πⱼ≠ᵢ ',('frac','x−xⱼ','xᵢ−xⱼ'))
Eq(D,'P(x)=a₀+a₁(x−x₀)+a₂(x−x₀)(x−x₁)+⋯')
Eq(D,'Sᵢ(x)=Aᵢ yᵢ+Bᵢ yᵢ₊₁+',('frac','hᵢ²','6'),' [(Aᵢ³−Aᵢ)Mᵢ+(Bᵢ³−Bᵢ)Mᵢ₊₁]')
P(D,'Lagrange se evalúa mediante pesos baricéntricos; Newton utiliza diferencias divididas; el spline natural impone segundas derivadas nulas en los extremos. Ambos métodos polinomiales reconstruyen el mismo polinomio con los mismos nodos, mientras el spline es una interpolación por tramos.')
tab(D,['Escenario','Error máx. Lagrange','Error máx. Newton','Error máx. spline'],[[s,*(fnum(m['error_abs']) for m in simulate('sensores',s)['methods'])] for s in SCENARIOS],[4.4,4.2,4.2,4.1])
P(D,'El índice de Lebesgue aproximado crece de 3,105 en NORMAL a 283,181 en Runge. El error máximo de Lagrange pasa a aproximadamente 6,938 mientras el del spline queda en 0,00246. Esto evidencia sensibilidad de interpolación global en nodos desfavorables; no representa un sensor real fallando de esa forma.')

H(D,'9. Errores y referencias')
Eq(D,'eₐ = |yₐₚᵣₒₓ−yᵣₑ𝒻| ;   eᵣ = ',('frac','eₐ','|yᵣₑ𝒻|'),' (si yᵣₑ𝒻≠0)')
Eq(D,'e% = 100eᵣ ;    r = Ax−b ;    κ∞(A)=||A||∞ ||A⁻¹||∞')
P(D,'Cada cálculo informa referencia, error absoluto y, cuando la referencia no es cero, error porcentual. En raíces se guarda |f(t)|, en sistemas lineales ||Ax−b||₂, en EDO el error se estima frente a la solución analítica y en interpolación se evalúan puntos conocidos que fueron ocultados. No deben compararse métricas de familias distintas como si tuvieran unidades equivalentes.')
H(D,'9.1 Tabla de refinamiento y pasos')
P(D,'Las tablas del simulador muestran por método sus iteraciones o tamaños de subintervalo. Los pasos de bisección contienen el intervalo implícito, raíz aproximada y residual; en integrales se registran refinamientos n=8,16,32,64 y en Romberg sus niveles. La comparación se apoya en las tablas y en los dos gráficos dentro de cada módulo.')
page(D)

H(D,'10. Experimentos por módulo — gráficos calculados')
P(D,'Las siguientes figuras provienen directamente de la ejecución de numericos.py. No se trata de imágenes representativas inventadas: muestran los perfiles y errores correspondientes a los parámetros NORMAL. Las comparaciones de los otros escenarios se encuentran en el archivo docs/experimentos_12.json y dentro del simulador.')
for case,title in [('extrusion','Extrusión'),('hidrogel','Degradación'),('oscilaciones','Oscilaciones'),('sensores','Sensores')]:
 H(D,'10.'+str(['extrusion','hidrogel','oscilaciones','sensores'].index(case)+1)+' '+title,2)
 fig(D,f'{case}_1.png',f'{title}: solución o señal de referencia frente a métodos de la semana 2.',w=14.6)
 fig(D,f'{case}_2.png',f'{title}: error, convergencia o refinamiento del cálculo.',w=14.6)

H(D,'11. Comparación de los 12 escenarios')
tab(D,['Caso','Normal','Estrés','Mal condicionado'],[
 ('Extrusión: T (s)',*[fnum(simulate('extrusion',s)['reference']['tiempo_parada_s']) for s in SCENARIOS]),
 ('Extrusión: V (mL)',*[fnum(simulate('extrusion',s)['reference']['volumen_extra_mL']) for s in SCENARIOS]),
 ('Hidrogel: t* (días)',*[fnum(simulate('hidrogel',s)['reference']['tiempo_umbral_dias']) for s in SCENARIOS]),
 ('Hidrogel: κ∞ SPD',*[fnum(simulate('hidrogel',s)['reference']['condicion_infinito']) for s in SCENARIOS]),
 ('Oscilación: error máx. RK4 (m)',*[fnum(simulate('oscilaciones',s)['reference']['error_max_RK4_m']) for s in SCENARIOS]),
 ('Sensores: error máx. Lagrange',*[fnum(simulate('sensores',s)['methods'][0]['error_abs']) for s in SCENARIOS])],[6.5,3.45,3.4,3.55])
P(D,'Cada fila describe un indicador distinto: las variaciones son interpretables dentro del mismo modelo, no comparables directamente entre módulos. En MAL CONDICIONADO puede mantenerse la misma referencia física mientras cambian las propiedades matemáticas del problema.')

H(D,'12. Persistencia: diseño y prueba real de SQLite')
P(D,'El servidor almacena seis entidades: caso_estudio, escenario, simulacion, ejecucion_metodo, iteracion_resultado y resultado_resumen. Cada simulación registra entrada JSON, salida JSON completa, fecha y huella SHA-256 de los resultados. Las tablas relacionadas guardan métodos, tolerancias, iteraciones, errores y conclusiones. El DER coincide con docs/esquema.sql.')
P(D,'Procedimiento de aceptación ejecutado: (1) iniciar app.py; (2) simular y guardar un caso con parámetros no predeterminados; (3) detener el servidor y cerrar la conexión; (4) reiniciar usando la misma base SQLite; (5) recuperar los parámetros y el resultado; (6) repetir el cálculo; (7) comprobar que las dos huellas SHA-256 coinciden. El archivo de base de datos permanece en disco, por lo que no depende de variables temporales del navegador.')
tab(D,['Prueba','Evidencia obtenida'],[
 ('12 módulos/escenarios por API','12 respuestas 200 y resultados con dos gráficos por ejecución.'),
 ('Guardado + cierre del servidor','Registro insertado y persistido en archivo SQLite.'),
 ('Recuperación tras reinicio','Entradas, tablas de métodos y dos gráficos accesibles.'),
 ('Repetición y comparación SHA-256','Huella idéntica sobre el mismo resultado serializado.'),
 ('Protección de base de datos','GET /data/... responde HTTP 403.')],[7.1,9.8])

H(D,'13. Fallos detectados, correcciones y límites')
tab(D,['Problema identificado','Resultado observado','Acción'],[
 ('Raíz múltiple con Newton/secante','No cumplen criterio de convergencia aunque |f(t)| sea pequeño.','Mostrar estado real, comparar con bisección y raíz exacta.'),
 ('Oscilaciones con RK2','Error mayor que RK4 con el mismo paso.','Mostrar ambas trayectorias y el error temporal.'),
 ('Runge con nodos equiespaciados','Polinomios globales oscilan mucho entre los nodos.','Comparar con spline, error oculto e índice de Lebesgue.'),
 ('Validación HTML','Algunos min/step rechazaban valores válidos.','Ajustar pasos y volver a probar los cuatro módulos.'),
 ('Servidor de archivos','Existía riesgo de descarga de SQLite.','Restringir /data/ y ficheros de BD.'),
 ('Persistencia','Se requería demostrar datos tras reinicio.','Prueba HTTP de guardado/reinicio/recuperación/repetición.')],[5.1,6,5.8])
P(D,'Limitación del entorno de pruebas: el navegador automatizado no pudo navegar al servidor local por restricciones de administración. Se hizo una prueba visual con respuestas numéricas precomputadas y, por separado, una prueba HTTP real sobre el servidor y SQLite. Estas dos verificaciones se describen sin confundirlas.')

H(D,'14. Conclusiones de la semana 2')
P(D,'Conclusión matemática: los métodos obligatorios se encuentran implementados y comparados sobre funciones con referencia analítica o verificación independiente. La convergencia depende de la formulación: la raíz cúbica multiplica sensibilidad, el interpolador global es vulnerable a nodos equiespaciados en Runge y RK4 entrega menores errores que RK2 en el caso oscilatorio seleccionado. El estado de convergencia se informa, no se fuerza como correcto.')
P(D,'Conclusión del problema: los modelos ilustran tendencias de extrusión, deterioro, vibraciones y señales de sensores bajo supuestos explícitos. No respaldan por sí solos el diseño de una biotinta, la supervivencia celular ni el funcionamiento seguro de una impresora real. La implementación constituye una plataforma de evaluación computacional preliminar que puede extenderse con datos experimentales.')
P(D,'La base de datos y el historial constituyen un avance verificable frente a la semana 1. Para la tercera semana corresponde completar pruebas de validación más exhaustivas, revisar las conclusiones dobles en cada escenario, elaborar el video de hasta tres minutos y preparar la defensa de todos los integrantes.')
H(D,'15. Ejemplos de cálculo manual')
H(D,'15.1 Bisección del tiempo de parada',2)
P(D,'Usamos q₀=1,2 mL/s, a=0,4 mL/s² y f(t)=1,2−0,4t con intervalo inicial [0;5,4] segundos. En la primera iteración, el punto medio es (0+5,4)/2=2,7 s; f(2,7)=0,12 y se actualiza el límite inferior. En la segunda, t₂=(2,7+5,4)/2=4,05 s; f(4,05)=−0,42, de modo que el límite superior se reduce. En la tercera, el punto medio es 3,375 s, con f(3,375)=−0,15. Continuamos hasta obtener t≈3 s con la tolerancia indicada.')
Eq(D,'t₁ = ',('frac','0+5,4','2'),' = 2,7  ;   f(t₁)=0,12')
Eq(D,'t₂ = ',('frac','2,7+5,4','2'),' = 4,05  ;   f(t₂)=−0,42')
H(D,'15.2 Simpson compuesto y volumen acumulado',2)
P(D,'Tomamos n=8 subintervalos en [0;3] s. El paso es h=3/8=0,375 s y el caudal Q(t)=1,2−0,4t. Los nueve valores de Q son: 1,2; 1,05; 0,9; 0,75; 0,6; 0,45; 0,3; 0,15; 0 (mL/s). La suma de valores interiores impares vale 2,4 y la de pares vale 1,8.')
Eq(D,'V ≈ ',('frac','0,375','3'),' [1,2+4(2,4)+2(1,8)+0] = 1,8 mL')
H(D,'15.3 Primera iteración de Runge-Kutta 2 (punto medio)',2)
P(D,'En la EDO (Qʹ,Vʹ)=(−0,4,Q), y₀=(1,2;0), h=0,375 s. La primera pendiente es k₁=(−0,4;1,2); el estado intermedio resulta (1,125;0,225) y la segunda pendiente k₂=(−0,4;1,125). Por tanto, y₁=y₀+h k₂=(1,05;0,421875). La expresión analítica V(t)=1,2t−0,2t² también da V(0,375)=0,421875 mL.')
Eq(D,'k₁=(−0,4;1,2)  ;  k₂=(−0,4;1,125)')
Eq(D,'y₁=(1,2;0)+0,375 k₂=(1,05;0,421875)')
H(D,'15.4 Primera iteración de calibración Jacobi',2)
P(D,'Para la matriz A con diagonal 4 y vecinos −1, junto con b=(0,33;0,176;−0,704;2,596)ᵀ, empezamos en x⁽⁰⁾=0. Jacobi divide cada componente de b por la diagonal 4 y obtiene x⁽¹⁾=(0,0825;0,044;−0,176;0,649)ᵀ. Las iteraciones siguientes se contrastan con x*=(0,10;0,07;0,004;0,65)ᵀ y se verifica el residuo ||Ax−b||₂.')
Eq(D,'x⁽¹⁾ = ',('matrix',[['0,0825'],['0,044'],['−0,176'],['0,649']]))
H(D,'15.5 Interpolación con Lagrange en tres nodos',2)
import math as _math
_y=[.65+.25*_math.exp(-t/4) for t in (0,2,4)]
_interp=.375*_y[0]+.75*_y[1]-.125*_y[2]
_exact=.65+.25*_math.exp(-.25)
P(D,'Seleccionamos tres nodos de la señal sintética en t=0,2 y 4 s, con valores '+', '.join(fnum(v) for v in _y)+'. Para estimar t=1, los factores de Lagrange son L₀=0,375, L₁=0,75 y L₂=−0,125. Su combinación entrega P(1)='+fnum(_interp)+'. El valor exacto es s(1)='+fnum(_exact)+'; el error absoluto es '+fnum(abs(_interp-_exact))+'. Este ejemplo aislado usa 3 nodos; la simulación principal utiliza los seis nodos definidos y 100 puntos ocultos.')
Eq(D,'P(1)=0,375 s(0)+0,75 s(2)−0,125 s(4)')

H(D,'16. Bibliografía y archivos de evidencia')
for t in [
 'Consigna oficial (2026). SIMTELE-RISK — Desafío integrador final, asignatura Métodos Numéricos, Universidad Mayor de San Andrés. Adaptación biomédica autorizada por el docente según el equipo.',
 'Shin, Y. J., Safina, D., Zheng, Y. y Levenberg, S. (2025). Microvascularization in 3D Human Engineered Tissue and Organoids. Annual Review of Biomedical Engineering, 27, 473–498. DOI: 10.1146/annurev-bioeng-103023-115236.',
 'Krajewska, U., Chechlińska, M. y Kurzyk, A. (2026). Vascularisation in 3D bioprinted models: emerging solutions engineering functional tissues and tumour models. Biofabrication, 18, 022001. DOI: 10.1088/1758-5090/ae2f02.',
 'Elaboración propia del equipo (2026). numericos.py, app.py, src/app.js, docs/esquema.sql y pruebas automatizadas de BIOPRINT-VASC, Semana 2.'
]:P(D,t)
P(D,'Archivos complementarios: docs/experimentos_12.json, docs/figuras/ (gráficos verificados), docs/DER_Semana2.mmd, docs/REGISTRO_FALLOS_Y_PRUEBAS.md, tests/test_semana2.py y tests/test_api.py.')
P(D,'Importante para la entrega: el repositorio debe actualizarse y el enlace público requiere un alojamiento con ejecución de Python y SQLite persistente. Un sitio estático de GitHub Pages no ejecutará app.py automáticamente.')

out=ROOT/'docs'/'Informe_Experimentos_Semana2_UMSA.docx'
D.core_properties.title='BIOPRINT-VASC — Informe de experimentos y fallos detectados — Semana 2'
D.core_properties.author='Equipo UMSA · Carrera de Informática'
D.save(str(out))
print('DOCX',out,out.stat().st_size,'bytes')
