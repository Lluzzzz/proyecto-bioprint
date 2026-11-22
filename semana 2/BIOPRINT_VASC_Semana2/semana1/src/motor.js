/* BIOPRINT-VASC · Semana 1 · licencia educativa MIT.
   Modelo 1D FV: -D C'' + k C = 0, C(0)=C0, C'(L)=0.
   Unidades L[mm], D[mm²/s], k[s⁻¹], C adimensional. */
(function(global){
'use strict';
const M={};
const dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0);
const norm=v=>Math.sqrt(dot(v,v));
const normInf=v=>Math.max(...v.map(Math.abs));
const matvec=(A,x)=>A.map(r=>dot(r,x));
const residual=(A,b,x)=>norm(matvec(A,x).map((v,i)=>v-b[i]));
const maxDifference=(a,b)=>normInf(a.map((v,i)=>v-b[i]));
function validate(p){
 for(const n of ['L','D','k','C0','N','tol']) if(!Number.isFinite(p[n]))throw Error('Parámetro inválido: '+n);
 if(!(p.L>=.05&&p.L<=1))throw Error('L debe estar entre 0,05 y 1 mm.');
 if(!(p.D>0&&p.D<=.1))throw Error('D debe ser mayor que 0 y como máximo 0,1 mm²/s.');
 if(!(p.k>=0&&p.k<=1))throw Error('k debe estar entre 0 y 1 s⁻¹.');
 if(!(p.C0>0&&p.C0<=1))throw Error('C0 debe estar entre 0 y 1.');
 if(!(Number.isInteger(p.N)&&p.N>=4&&p.N<=40))throw Error('Usa entre 4 y 40 celdas.');
 if(!(p.tol>=1e-13&&p.tol<=1e-4))throw Error('Tolerancia fuera de rango.');
}
function assemble(p){
 validate(p);const h=p.L/p.N, g=p.k*h*h/p.D;
 const A=Array.from({length:p.N},()=>Array(p.N).fill(0)),b=Array(p.N).fill(0);
 for(let i=0;i<p.N;i++){
  A[i][i]=(i===0?3:i===p.N-1?1:2)+g;
  if(i>0)A[i][i-1]=-1;
  if(i<p.N-1)A[i][i+1]=-1;
 }
 b[0]=2*p.C0;
 return {A,b,h,g,x:Array.from({length:p.N},(_,i)=>(i+.5)*h)};
}
function exact(p,x){
 const u=Math.sqrt(p.k/p.D), a=u*(p.L-x), b=u*p.L;
 return p.C0*Math.cosh(a)/Math.cosh(b);
}
function solveDirect(A,b){
 const n=b.length,m=A.map((row,i)=>[...row,b[i]]);
 for(let i=0;i<n;i++){
  let q=i;for(let j=i+1;j<n;j++)if(Math.abs(m[j][i])>Math.abs(m[q][i]))q=j;
  if(Math.abs(m[q][i])<1e-19)throw Error('Sistema singular.');
  [m[i],m[q]]=[m[q],m[i]];
  for(let j=i+1;j<n;j++){
   const fac=m[j][i]/m[i][i];for(let c=i;c<=n;c++)m[j][c]-=fac*m[i][c];
  }
 }
 const x=Array(n).fill(0);
 for(let i=n-1;i>=0;i--){let sum=m[i][n];for(let j=i+1;j<n;j++)sum-=m[i][j]*x[j];x[i]=sum/m[i][i];}
 return x;
}
function lu(A,b){
 const n=b.length,L=Array.from({length:n},(_,i)=>Array.from({length:n},(_,j)=>i===j?1:0));
 const U=Array.from({length:n},()=>Array(n).fill(0));
 for(let i=0;i<n;i++){
  for(let j=i;j<n;j++){let v=A[i][j];for(let t=0;t<i;t++)v-=L[i][t]*U[t][j];U[i][j]=v;}
  if(Math.abs(U[i][i])<1e-19)throw Error('Pivote nulo en LU.');
  for(let j=i+1;j<n;j++){let v=A[j][i];for(let t=0;t<i;t++)v-=L[j][t]*U[t][i];L[j][i]=v/U[i][i];}
 }
 const z=Array(n).fill(0),x=Array(n).fill(0);
 for(let i=0;i<n;i++){let v=b[i];for(let j=0;j<i;j++)v-=L[i][j]*z[j];z[i]=v;}
 for(let i=n-1;i>=0;i--){let v=z[i];for(let j=i+1;j<n;j++)v-=U[i][j]*x[j];x[i]=v/U[i][i];}
 return {x,L,U,z};
}
function fixedPoint(A,b,tol,method){
 let x=Array(b.length).fill(0),iter=0,history=[];
 const target=tol*norm(b);
 for(iter=1;iter<=30000;iter++){
  const next=x.slice();
  for(let i=0;i<x.length;i++){
   let v=b[i];
   for(let j=0;j<x.length;j++)if(i!==j)v-=A[i][j]*(method==='Jacobi'?x[j]:next[j]);
   next[i]=v/A[i][i];
  }
  x=next;const r=residual(A,b,x);history.push(r);
  if(!Number.isFinite(r))break;
  if(r<=target)return {x,iterations:iter,history,converged:true};
 }
 return {x,iterations:history.length,history,converged:false};
}
function cg(A,b,tol){
 let x=Array(b.length).fill(0),r=b.slice(),direction=r.slice(),rr=dot(r,r),history=[];
 const target=tol*norm(b);
 for(let iter=1;iter<=30000;iter++){
  const Ad=matvec(A,direction), denom=dot(direction,Ad);
  if(!(denom>0))break;
  const alpha=rr/denom;
  x=x.map((v,i)=>v+alpha*direction[i]);
  r=r.map((v,i)=>v-alpha*Ad[i]);
  const fresh=residual(A,b,x);history.push(fresh);
  if(fresh<=target)return {x,iterations:iter,history,converged:true};
  const rr2=dot(r,r);if(rr2<=0)break;
  direction=r.map((v,i)=>v+(rr2/rr)*direction[i]);rr=rr2;
 }
 return {x,iterations:history.length,history,converged:false};
}
function kappaInfinity(A){
 const n=A.length, anorm=Math.max(...A.map(row=>row.reduce((s,x)=>s+Math.abs(x),0)));
 const inverse=Array.from({length:n},()=>Array(n).fill(0));
 for(let j=0;j<n;j++){const e=Array(n).fill(0);e[j]=1;solveDirect(A,e).forEach((v,i)=>inverse[i][j]=v);}
 return anorm*Math.max(...inverse.map(row=>row.reduce((s,x)=>s+Math.abs(x),0)));
}
function run(p,scenario){
 const {A:physicalA,b:physicalB,x,h,g}=assemble(p);
 const scale=Array(p.N).fill(1);
 if(scenario==='MAL_CONDICIONADO'){scale[1]=.05;scale[2]=.005;}
 const A=physicalA.map((row,i)=>row.map((v,j)=>v*scale[i]*scale[j]));
 const b=physicalB.map((v,i)=>v*scale[i]);
 const y0=solveDirect(A,b),c0=y0.map((v,i)=>v*scale[i]);
 const computed={
  'Jacobi':fixedPoint(A,b,p.tol,'Jacobi'),
  'Gauss-Seidel':fixedPoint(A,b,p.tol,'Gauss-Seidel'),
  'LU':{x:lu(A,b).x,history:[],iterations:0,converged:true},
  'Gradiente conjugado':cg(A,b,p.tol),
  'Directa':{x:y0,history:[],iterations:0,converged:true},
 };
 const methods={};
 for(const [name,data] of Object.entries(computed)){
  const c=data.x.map((v,i)=>v*scale[i]);const ea=maxDifference(c,c0);
  const rel=ea/normInf(c0);
  methods[name]={iterations:data.iterations,converged:data.converged,history:data.history,
   profile:c,absoluteError:ea,relativeError:rel,percentError:100*rel,
   residual:residual(A,b,data.x),physicalResidual:residual(physicalA,physicalB,c)};
 }
 const exactNodes=x.map(z=>exact(p,z));
 const malla=maxDifference(c0,exactNodes),condition=kappaInfinity(A);
 // b perturbation at third component, as in the written report.
 const db=Array(p.N).fill(0);db[2]=1e-6*norm(b);
 const perturbed=solveDirect(A,b.map((v,i)=>v+db[i]));
 const ampl=(norm(perturbed.map((v,i)=>v-y0[i]))/norm(y0))/(norm(db)/norm(b));
 return {p,scenario,physicalA,physicalB,A,b,x,h,g,scale,profile:c0,exactNodes,
  minExact:exact(p,p.L),gridError:malla,condition,amplification:ampl,methods};
}
Object.assign(M,{assemble,validate,exact,solveDirect,lu,fixedPoint,cg,kappaInfinity,run,residual,dot,norm});
if(typeof module!=='undefined'&&module.exports)module.exports=M;
global.BioMotor=M;
})(typeof window==='undefined'?globalThis:window);
