"""BIOPRINT-VASC S2: modelos académicos y algoritmos, sin dependencias externas.
Todos los datos son sintéticos. No apto para decisiones clínicas.
"""
import math

SCENARIOS = ('NORMAL','ESTRES','MAL_CONDICIONADO')
CASES = ('extrusion','hidrogel','oscilaciones','sensores')

def valid_input(case, scenario, params):
    if case not in CASES: raise ValueError('Módulo desconocido')
    if scenario not in SCENARIOS: raise ValueError('Escenario desconocido')
    if not isinstance(params,dict): raise ValueError('Los parámetros deben ser un objeto')
    if len(params)>10: raise ValueError('Demasiados parámetros')
    clean={}
    allowed={
      'extrusion':{'q0','a','n'},
      'hidrogel':{'d0','alpha','beta','umbral'},
      'oscilaciones':{'m','c','k','x0','v0','T','n'},
      'sensores':{'ruido'}
    }
    for k,v in params.items():
        if k not in allowed[case]:
            raise ValueError('Parámetro no reconocido en '+case+': '+str(k))
        if isinstance(v,bool) or not isinstance(v,(float,int)) or not math.isfinite(v):
            raise ValueError('Los parámetros deben ser números finitos')
        if k=='n' and (not float(v).is_integer() or int(v)%2 or int(v)<8):
            raise ValueError('n debe ser un entero par ≥ 8 para Simpson 1/3')
        clean[k]=float(v)
    return clean

def metric(val,ref):
    err=abs(val-ref)
    return {'error_abs':err,'error_rel_pct':100*err/abs(ref) if abs(ref)>1e-13 else None}

def _safe(f,x):
    v=f(x)
    if not math.isfinite(v):raise ValueError('Función no finita')
    return v

def bisection(f,a,b,tol=1e-10,max_iter=250):
    fa,fb=_safe(f,a),_safe(f,b)
    if fa==0:return {'root':a,'iterations':0,'residual':0.,'trace':[[0,a,0.]],'converged':True}
    if fb==0:return {'root':b,'iterations':0,'residual':0.,'trace':[[0,b,0.]],'converged':True}
    if fa*fb>0:raise ValueError('Bisección requiere cambio de signo')
    tr=[]
    for i in range(1,max_iter+1):
        mid=(a+b)/2;fm=_safe(f,mid)
        tr.append([i,mid,abs(fm)])
        if fm==0:
            return {'root':mid,'iterations':i,'residual':0.,'trace':tr,'converged':True}
        if (b-a)/2<=tol*max(1.,abs(mid)):
            return {'root':mid,'iterations':i,'residual':abs(fm),'trace':tr,'converged':True}
        if fa*fm<=0:b,fb=mid,fm
        else:a,fa=mid,fm
    return {'root':mid,'iterations':max_iter,'residual':abs(fm),'trace':tr,'converged':False}

def newton(f,df,x0,tol=1e-10,max_iter=250):
    x=x0;tr=[]
    for i in range(1,max_iter+1):
        fx=_safe(f,x);deriv=_safe(df,x)
        if abs(deriv)<1e-18:break
        nx=x-fx/deriv
        if not math.isfinite(nx):break
        tr.append([i,nx,abs(_safe(f,nx))])
        if abs(nx-x)<=tol*max(1.,abs(nx)):
            return {'root':nx,'iterations':i,'residual':abs(_safe(f,nx)),'trace':tr,'converged':True}
        x=nx
    return {'root':x,'iterations':len(tr),'residual':abs(_safe(f,x)),'trace':tr,'converged':False}

def secant(f,x0,x1,tol=1e-10,max_iter=250):
    f0=_safe(f,x0);f1=_safe(f,x1);tr=[]
    for i in range(1,max_iter+1):
        if abs(f1-f0)<1e-25:break
        nx=x1-f1*(x1-x0)/(f1-f0)
        if not math.isfinite(nx):break
        fn=_safe(f,nx);tr.append([i,nx,abs(fn)])
        if abs(nx-x1)<=tol*max(1.,abs(nx)):
            return {'root':nx,'iterations':i,'residual':abs(fn),'trace':tr,'converged':True}
        x0,x1,f0,f1=x1,nx,f1,fn
    return {'root':x1,'iterations':len(tr),'residual':abs(f1),'trace':tr,'converged':False}

def trapezoid(f,a,b,n):
    if n<1:raise ValueError('n inválido')
    h=(b-a)/n
    return h*(.5*f(a)+sum(f(a+i*h) for i in range(1,n))+.5*f(b))

def simpson(f,a,b,n):
    if n<2 or n%2:raise ValueError('Simpson exige n par')
    h=(b-a)/n
    return h/3*(f(a)+f(b)+sum((4 if i%2 else 2)*f(a+i*h) for i in range(1,n)))

def romberg(f,a,b,levels=6):
    R=[]
    for i in range(levels):
        row=[trapezoid(f,a,b,2**i)]
        for j in range(1,i+1):
            row.append(row[j-1]+(row[j-1]-R[i-1][j-1])/(4**j-1))
        R.append(row)
    return {'value':R[-1][-1],'table':R}

def rk2(fun,y0,T,n):
    h=T/n; y=list(y0); pts=[[0.]+y[:]]
    for i in range(n):
        t=i*h;k1=fun(t,y)
        ym=[v+.5*h*k for v,k in zip(y,k1)]
        k2=fun(t+.5*h,ym)
        y=[v+h*k for v,k in zip(y,k2)]
        pts.append([(i+1)*h]+y[:])
    return pts

def rk4(fun,y0,T,n):
    h=T/n;y=list(y0);pts=[[0.]+y[:]]
    for i in range(n):
        t=i*h;k1=fun(t,y)
        k2=fun(t+h/2,[v+h*q/2 for v,q in zip(y,k1)])
        k3=fun(t+h/2,[v+h*q/2 for v,q in zip(y,k2)])
        k4=fun(t+h,[v+h*q for v,q in zip(y,k3)])
        y=[v+h*(a+2*b+2*c+d)/6 for v,a,b,c,d in zip(y,k1,k2,k3,k4)]
        pts.append([(i+1)*h]+y[:])
    return pts

def _graph(title,xlab,ylab,series):
    return {'title':title,'xLabel':xlab,'yLabel':ylab,'series':[{'name':name,'points':[[float(x),float(y)] for x,y in pts]} for name,pts in series]}

def _method(name,value,ref,iterations=0,residual=0,converged=True,details=None):
    return {'method':name,'value':float(value),'reference':float(ref),**metric(value,ref),
            'iterations':int(iterations),'residual':float(residual),'converged':bool(converged),
            'details':details or []}

def _roots(f,df,ref,a,b):
    rr=[('Bisección',bisection(f,a,b)),('Newton-Raphson',newton(f,df,a+(b-a)*.15)),('Secante',secant(f,a+(b-a)*.05,a+(b-a)*.83))]
    return [_method(name,r['root'],ref,r['iterations'],r['residual'],r['converged'],r['trace'][:120]) for name,r in rr]

def extrusion(s,p):
    defaults={'q0':1.2,'a':.4,'n':24}
    if s=='ESTRES':defaults.update(q0=1.5,a=.22)
    defaults.update(p);q0,a,n=defaults['q0'],defaults['a'],int(defaults['n'])
    if not(.05<=q0<=10 and .01<=a<=3 and 8<=n<=500):raise ValueError('q0, a o n fuera de rango')
    T=q0/a; exactV=q0*T/2
    f0=lambda t:q0-a*t
    f=lambda t:f0(t)**3 if s=='MAL_CONDICIONADO' else f0(t)
    df=lambda t:-3*a*f0(t)**2 if s=='MAL_CONDICIONADO' else -a
    methods=_roots(f,df,T,0,1.8*T)
    Q=lambda t:q0-a*t
    integ=[('Trapecio compuesto',trapezoid(Q,0,T,n)),('Simpson 1/3',simpson(Q,0,T,n)),('Romberg',romberg(Q,0,T)['value'])]
    for name,v in integ:
        scheme={'Trapecio compuesto':trapezoid,'Simpson 1/3':simpson}.get(name)
        if scheme:
            ns=[8,16,32,64] if name=='Trapecio compuesto' else [8,16,32,64]
            details=[[j,scheme(Q,0,T,j),abs(scheme(Q,0,T,j)-exactV)] for j in ns]
        else:
            table=romberg(Q,0,T,6)['table'];details=[[i+1,row[-1],abs(row[-1]-exactV)] for i,row in enumerate(table)]
        methods.append(_method(name,v,exactV,n if name!='Romberg' else 6,abs(v-exactV),details=details))
    ode=lambda t,y:[-a,y[0]]
    r2=rk2(ode,[q0,0.],T,n);r4=rk4(ode,[q0,0.],T,n)
    methods.extend([_method('RK2 (volumen)',r2[-1][2],exactV,n,abs(r2[-1][2]-exactV)),_method('RK4 (volumen)',r4[-1][2],exactV,n,abs(r4[-1][2]-exactV))])
    grid=[T*i/80 for i in range(81)]
    ch=[_graph('Caudal durante la parada','Tiempo (s)','Caudal (mL/s)',[
        ('Exacto',[(t,Q(t)) for t in grid]),('RK2',[(row[0],row[1]) for row in r2]),('RK4',[(row[0],row[1]) for row in r4])]),
        _graph('Convergencia de las raíces','Iteración','Error absoluto de tiempo (s)',[
          (method['method'],[(row[0],abs(row[1]-T)) for row in method['details']])
           for method in methods[:3]])]
    return {'title':'Parada de extrusión','model':'dQ/dt = −a; dV/dt = Q; Q(0)=q₀, V(0)=0',
        'params':defaults,'reference':{'tiempo_parada_s':T,'volumen_extra_mL':exactV},'methods':methods,'charts':ch,
        'numerical_conclusion':'Para desaceleración constante, RK2/RK4 y las tres reglas de integración reproducen la referencia con error de redondeo. La raíz cúbica en el escenario mal condicionado reduce la sensibilidad del residual como indicador de error en t.',
        'problem_conclusion':'Una desaceleración menor incrementa el tiempo de parada y el volumen adicional depositado en este modelo sintético; no se modelan propiedades reológicas reales.',
        'scenario_note':'Raíz cúbica artificial con derivada nula en la solución; no representa mayor peligro físico.' if s=='MAL_CONDICIONADO' else 'Caso físico sintético de referencia o mayor exigencia.'}

def dot(a,b):return sum(x*y for x,y in zip(a,b))
def matvec(A,x):return [dot(r,x) for r in A]
def norm2(x):return math.sqrt(dot(x,x))
def norminf(x):return max(abs(t) for t in x)
def _linres(A,x,b):return norm2([v-w for v,w in zip(matvec(A,x),b)])

def gaussian(A,b):
    n=len(b);m=[list(row)+[float(b[i])] for i,row in enumerate(A)]
    for k in range(n):
        j=max(range(k,n),key=lambda i:abs(m[i][k]))
        if abs(m[j][k])<1e-24:raise ValueError('Matriz singular')
        m[j],m[k]=m[k],m[j]
        for i in range(k+1,n):
            fac=m[i][k]/m[k][k]
            for c in range(k,n+1):m[i][c]-=fac*m[k][c]
    x=[0.]*n
    for i in range(n-1,-1,-1):x[i]=(m[i][-1]-sum(m[i][j]*x[j] for j in range(i+1,n)))/m[i][i]
    return x

def lu(A,b):
    n=len(b);L=[[0.]*n for _ in range(n)];U=[[0.]*n for _ in range(n)]
    for i in range(n):L[i][i]=1
    for i in range(n):
        for k in range(i,n):U[i][k]=A[i][k]-sum(L[i][j]*U[j][k] for j in range(i))
        if abs(U[i][i])<1e-24:raise ValueError('Pivote nulo en LU')
        for k in range(i+1,n):L[k][i]=(A[k][i]-sum(L[k][j]*U[j][i] for j in range(i)))/U[i][i]
    y=[0.]*n
    for i in range(n):y[i]=b[i]-sum(L[i][j]*y[j] for j in range(i))
    x=[0.]*n
    for i in range(n-1,-1,-1):x[i]=(y[i]-sum(U[i][j]*x[j] for j in range(i+1,n)))/U[i][i]
    return x

def iterative(A,b,kind,tol=1e-11,max_iter=5000):
    n=len(b);x=[0.]*n;target=tol*max(1.,norm2(b));trace=[]
    if kind=='Gradiente conjugado':
        r=b[:];p=r[:];rr=dot(r,r)
        for it in range(1,min(n*10,max_iter)+1):
            Ap=matvec(A,p);den=dot(p,Ap)
            if den<=0:raise ValueError('CG requiere matriz SPD')
            alpha=rr/den
            x=[v+alpha*w for v,w in zip(x,p)]
            r=[v-alpha*w for v,w in zip(r,Ap)]
            res=_linres(A,x,b);trace.append([it,res])
            if res<=target:return x,trace,True
            rrnew=dot(r,r)
            if rr<=1e-60:break
            p=[v+(rrnew/rr)*w for v,w in zip(r,p)];rr=rrnew
        return x,trace,False
    for it in range(1,max_iter+1):
        old=x[:]
        for i in range(n):
            row=A[i]
            if kind=='Jacobi':
                x[i]=(b[i]-sum(row[j]*old[j] for j in range(n) if j!=i))/row[i]
            else:
                x[i]=(b[i]-sum(row[j]*(x[j] if j<i else old[j]) for j in range(n) if j!=i))/row[i]
        res=_linres(A,x,b);trace.append([it,res])
        if res<=target:return x,trace,True
    return x,trace,False

def cond_inf(A):
    n=len(A);row=max(sum(abs(v) for v in r) for r in A)
    invcols=[gaussian(A,[1. if i==j else 0. for i in range(n)]) for j in range(n)]
    invnorm=max(sum(abs(invcols[j][i]) for j in range(n)) for i in range(n))
    return row*invnorm

def hidrogel(s,p):
    defaults={'d0':.10,'alpha':.07,'beta':.004,'umbral':.65}
    if s=='ESTRES':defaults.update(alpha=.11,beta=.007)
    defaults.update(p);d0,alpha,beta,u=[defaults[k] for k in ('d0','alpha','beta','umbral')]
    if not(0<=d0<1 and 0<alpha<=1 and 0<=beta<=.1 and d0<u<=2):raise ValueError('Parámetros de degradación inválidos')
    ref=2*(u-d0)/(alpha+math.sqrt(alpha*alpha+4*beta*(u-d0))) if beta>0 else (u-d0)/alpha
    D=lambda t:d0+alpha*t+beta*t*t
    f0=lambda t:D(t)-u
    f=lambda t:f0(t)**3 if s=='MAL_CONDICIONADO' else f0(t)
    df=lambda t:3*f0(t)**2*(alpha+2*beta*t) if s=='MAL_CONDICIONADO' else alpha+2*beta*t
    roots=_roots(f,df,ref,0,1.8*ref)
    A=[[4. if i==j else (-1. if abs(i-j)==1 else 0.) for j in range(4)] for i in range(4)]
    xstar=[d0,alpha,beta,u];b=matvec(A,xstar)
    S=[1.,.05,.005,1.] if s=='MAL_CONDICIONADO' else [1.]*4
    B=[[S[i]*A[i][j]*S[j] for j in range(4)] for i in range(4)];bb=[S[i]*b[i] for i in range(4)]
    linear=[];trace=[]
    for name in ('Jacobi','Gauss-Seidel','LU','Gradiente conjugado','Referencia directa'):
        if name=='LU': y=lu(B,bb);it=1;tr=[[1,_linres(B,y,bb)]];ok=True
        elif name=='Referencia directa':y=gaussian(B,bb);it=1;tr=[[1,_linres(B,y,bb)]];ok=True
        else:y,tr,ok=iterative(B,bb,name);it=len(tr)
        xx=[S[i]*y[i] for i in range(4)]
        val=norminf([xx[i]-xstar[i] for i in range(4)])
        linear.append({'method':name+' (calibración SPD)','value':val,'reference':0.,'error_abs':val,'error_rel_pct':None,
                       'iterations':it,'residual':_linres(B,y,bb),'converged':ok,'details':tr[:120]})
        if name in ('Jacobi','Gauss-Seidel','Gradiente conjugado'):trace.append((name,tr))
    methods=roots+linear
    grid=[i*ref*1.4/80 for i in range(81)]
    ch=[_graph('Indicador de degradación y umbral','Tiempo (días)','Indicador adimensional',[
        ('D(t)',[(t,D(t)) for t in grid]),('Umbral',[(t,u) for t in grid])]),
        _graph('Convergencia de calibración SPD','Iteraciones','Residuo ||Ay−b||₂',[
            (name,[(i,max(v,1e-16)) for i,v in tr[:100]]) for name,tr in trace])]
    return {'title':'Degradación del hidrogel','model':'D(t)=D₀+αt+βt²; hallar D(t)=D_umbral; calibración SPD de 4×4',
        'params':defaults,'reference':{'tiempo_umbral_dias':ref,'condicion_infinito':cond_inf(B),'coeficientes_referencia':xstar},
        'methods':methods,'charts':ch,'numerical_conclusion':'Las tres raíces se comparan con la solución cuadrática; Jacobi, Gauss-Seidel, LU y CG se validan sobre un sistema SPD 4×4 de solución conocida.',
        'problem_conclusion':'Un aumento de α y β reduce el tiempo estimado para alcanzar un umbral sintético. No equivale a predicción de vida útil real.',
        'scenario_note':'El escalamiento S·A·S eleva κ∞ sin modificar los coeficientes físicos recuperados; además se utiliza una raíz cúbica artificial.' if s=='MAL_CONDICIONADO' else 'Indicador sintético sin calibración experimental.'}

def oscilaciones(s,p):
    defaults={'m':1.,'c':.8,'k':16.,'x0':.015,'v0':0.,'T':8.,'n':80}
    if s=='ESTRES':defaults.update(c=.3,x0=.03,T=10.)
    if s=='MAL_CONDICIONADO':defaults.update(c=2*math.sqrt(defaults['m']*defaults['k'])*(1-1e-6))
    defaults.update(p);m,c,k,x0,v0,T,n=[defaults[z] for z in ('m','c','k','x0','v0','T','n')];n=int(n)
    if not(.1<=m<=10 and 0<c<2*math.sqrt(m*k) and .1<=k<=100 and abs(x0)<=1 and abs(v0)<=1 and 1<=T<=20 and 8<=n<=400):raise ValueError('Parámetros de oscilación inválidos o régimen no subamortiguado')
    alpha=c/(2*m);omega=math.sqrt(k/m-alpha*alpha)
    def exact(t):
        z=omega*t
        sinc=1-z*z/6+z**4/120 if abs(z)<1e-4 else math.sin(z)/z
        return math.exp(-alpha*t)*(x0*math.cos(z)+(v0+alpha*x0)*t*sinc)
    fun=lambda t,y:[y[1],(-c*y[1]-k*y[0])/m]
    r2=rk2(fun,[x0,v0],T,n);r4=rk4(fun,[x0,v0],T,n)
    err2=max(abs(row[1]-exact(row[0])) for row in r2)
    err4=max(abs(row[1]-exact(row[0])) for row in r4)
    f=lambda t:exact(t)**2
    ref=simpson(f,0,T,8192)
    ints=[('Trapecio compuesto',trapezoid(f,0,T,n)),('Simpson 1/3',simpson(f,0,T,n)),('Romberg',romberg(f,0,T,7)['value'])]
    methods=[_method('RK2 (error máximo)',err2,0.,n,err2),_method('RK4 (error máximo)',err4,0.,n,err4)]
    for name,v in ints:
        scheme={'Trapecio compuesto':trapezoid,'Simpson 1/3':simpson}.get(name)
        if scheme:
            details=[[j,scheme(f,0,T,j),abs(scheme(f,0,T,j)-ref)] for j in [8,16,32,64]]
        else:
            table=romberg(f,0,T,7)['table'];details=[[i+1,row[-1],abs(row[-1]-ref)] for i,row in enumerate(table)]
        methods.append(_method(name,v,ref,n if name!='Romberg' else 7,abs(v-ref),details=details))
    grid=[i*T/120 for i in range(121)]
    ch=[_graph('Desplazamiento del cabezal','Tiempo (s)','Desplazamiento (m)',[
        ('Analítico',[(t,exact(t)) for t in grid]),('RK2',[(r[0],r[1]) for r in r2]),('RK4',[(r[0],r[1]) for r in r4])]),
        _graph('Error temporal de las EDO','Tiempo (s)','Error absoluto (m)',[
        ('RK2',[(r[0],abs(r[1]-exact(r[0]))) for r in r2]),('RK4',[(r[0],abs(r[1]-exact(r[0]))) for r in r4])])]
    sensitivity=1/math.sqrt(max(1e-30,1-(alpha/math.sqrt(k/m))**2))
    return {'title':'Oscilaciones del cabezal','model':'m·x″+c·x′+k·x=0; x(0)=x₀, x′(0)=v₀',
        'params':defaults,'reference':{'integral_x2_m2s':ref,'error_max_RK2_m':err2,'error_max_RK4_m':err4,'sensibilidad_raices_caracteristicas':sensitivity},
        'methods':methods,'charts':ch,'numerical_conclusion':'RK4 se contrasta con la solución analítica subamortiguada. Trapecio, Simpson y Romberg integran x(t)² usando una referencia independiente de Simpson muy refinado.',
        'problem_conclusion':'Menor amortiguamiento permite oscilaciones más persistentes en el modelo libre idealizado; no se infieren vibraciones reales de una impresora.',
        'scenario_note':'Raíces características casi coincidentes: sensibilidad 1/√(1−ζ²). Es un caso de condicionamiento de parámetros, no de falla física.' if s=='MAL_CONDICIONADO' else 'Movimiento libre sin fuerza externa; parámetros sintéticos.'}

def bary_weights(xs):
    return [1./math.prod(xs[i]-xs[j] for j in range(len(xs)) if j!=i) for i in range(len(xs))]

def lagrange(xs,ys,t,w=None):
    if w is None:w=bary_weights(xs)
    for x,y in zip(xs,ys):
        if abs(t-x)<1e-13:return y
    terms=[w[i]/(t-xs[i]) for i in range(len(xs))]
    return dot(terms,ys)/sum(terms)

def newton_coeff(xs,ys):
    a=ys[:];n=len(xs)
    for j in range(1,n):
        for i in range(n-1,j-1,-1):a[i]=(a[i]-a[i-1])/(xs[i]-xs[i-j])
    return a

def newton_eval(xs,a,t):
    ans=a[-1]
    for i in range(len(a)-2,-1,-1):ans=a[i]+(t-xs[i])*ans
    return ans

def spline_coeff(xs,ys):
    n=len(xs);h=[xs[i+1]-xs[i] for i in range(n-1)]
    if any(v<=0 for v in h):raise ValueError('Nodos deben estar ordenados y ser distintos')
    if n<=2:return [0.]*n
    aa=[[0.]*(n-2) for _ in range(n-2)];bb=[]
    for i in range(1,n-1):
        j=i-1;aa[j][j]=2*(h[i-1]+h[i])
        if j>0:aa[j][j-1]=h[i-1]
        if j<n-3:aa[j][j+1]=h[i]
        bb.append(6*((ys[i+1]-ys[i])/h[i]-(ys[i]-ys[i-1])/h[i-1]))
    return [0.]+gaussian(aa,bb)+[0.]

def spline_eval(xs,ys,M,t):
    if t<=xs[0]:i=0
    elif t>=xs[-1]:i=len(xs)-2
    else:
        i=0
        while i<len(xs)-2 and xs[i+1]<t:i+=1
    h=xs[i+1]-xs[i];a=(xs[i+1]-t)/h;b=(t-xs[i])/h
    return a*ys[i]+b*ys[i+1]+((a**3-a)*M[i]+(b**3-b)*M[i+1])*h*h/6

def sensores(s,p):
    ruido=p.get('ruido',.012 if s=='ESTRES' else 0.)
    if not(0<=ruido<=.07):raise ValueError('Ruido fuera del rango sintético 0 a 0,07')
    if s=='MAL_CONDICIONADO':
        xs=[10*i/14 for i in range(15)]
        exact=lambda t:1/(1+25*((t-5)/5)**2)
        note='Benchmark de Runge con nodos equiespaciados: subexperimento matemático, no concentración fisiológica.'
    else:
        xs=[float(i*2) for i in range(6)]
        exact=lambda t:.65+.25*math.exp(-t/4)
        note=('Ruido sintético determinista de amplitud '+str(ruido)+' en los nodos.' if ruido>0 else 'Concentración normalizada sintética sin ruido.')
    ys=[exact(x)+(ruido*(1 if i%2==0 else -1) if s!='MAL_CONDICIONADO' else 0.) for i,x in enumerate(xs)]
    w=bary_weights(xs);a=newton_coeff(xs,ys);M=spline_coeff(xs,ys)
    evaluators={'Lagrange':lambda t:lagrange(xs,ys,t,w),'Newton (diferencias divididas)':lambda t:newton_eval(xs,a,t),'Spline cúbico natural':lambda t:spline_eval(xs,ys,M,t)}
    test=[10*(i+.5)/100 for i in range(100)]
    curves=[10*i/200 for i in range(201)]
    methods=[]
    for name,fun in evaluators.items():
        dif=[fun(t)-exact(t) for t in test]
        mae=max(abs(e) for e in dif);rmse=math.sqrt(sum(e*e for e in dif)/len(dif))
        methods.append({'method':name,'value':rmse,'reference':0.,'error_abs':mae,'error_rel_pct':None,'iterations':len(xs),
                        'residual':max(abs(fun(x)-y) for x,y in zip(xs,ys)),'converged':True,'details':[[i+1,test[i],abs(dif[i])] for i in range(12)]})
    lebesgue=0.
    for t in curves:
        if any(abs(t-x)<1e-12 for x in xs):val=1.
        else:
            v=[w[i]/(t-xs[i]) for i in range(len(xs))];val=sum(abs(q) for q in v)/abs(sum(v))
        lebesgue=max(lebesgue,val)
    charts=[_graph('Reconstrucción de registros sintéticos','Tiempo (s)','Señal normalizada',
        [('Referencia',[(t,exact(t)) for t in curves]),('Nodos medidos',list(zip(xs,ys)))]+[(name,[(t,fun(t)) for t in curves]) for name,fun in evaluators.items()]),
        _graph('Error de reconstrucción en puntos ocultos','Tiempo (s)','Error absoluto',
        [(name,[(t,abs(fun(t)-exact(t))) for t in curves]) for name,fun in evaluators.items()])]
    return {'title':'Reconstrucción de sensores de oxígeno','model':'Interpolación sobre nodos conocidos; Lagrange, Newton y spline natural; evaluación sobre puntos ocultos.',
        'params':{'nodos':xs,'mediciones':ys,'ruido':ruido},'reference':{'funcion':('Runge (benchmark)' if s=='MAL_CONDICIONADO' else '0,65 + 0,25·exp(−t/4)'),
        'lebesgue_aproximado':lebesgue,'puntos_prueba':len(test)},'methods':methods,'charts':charts,
        'numerical_conclusion':'Lagrange y Newton son representaciones del mismo polinomio interpolador. El spline natural usa segmentos cúbicos y suele evitar grandes oscilaciones en el benchmark de Runge.',
        'problem_conclusion':'El ruido de sensores altera las reconstrucciones. El caso de Runge es exclusivamente una prueba numérica, no un resultado de oxigenación real.',
        'scenario_note':note}

def simulate(case,scenario='NORMAL',params=None):
    p=valid_input(case,scenario,params or {})
    result={'case':case,'scenario':scenario,'synthetic':True,'version':'2.0.0','unit_note':'Parámetros sintéticos; uso académico, no clínico.'}
    result.update({'extrusion':extrusion,'hidrogel':hidrogel,'oscilaciones':oscilaciones,'sensores':sensores}[case](scenario,p))
    return result

if __name__=='__main__':
    for c in CASES:
        for s in SCENARIOS:
            r=simulate(c,s)
            print(c,s,len(r['methods']),[round(x['error_abs'],8) for x in r['methods'][:3]])
