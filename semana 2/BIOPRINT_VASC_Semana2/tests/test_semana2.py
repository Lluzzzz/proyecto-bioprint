"""Comprobaciones automáticas de algoritmos, escenarios y persistencia.
Ejecutar: python -m unittest discover -s tests -v
"""
import unittest,sys,os,math,tempfile,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from numericos import (simulate,CASES,SCENARIOS,bisection,newton,secant,trapezoid,simpson,romberg,
                       rk2,rk4,lagrange,newton_coeff,newton_eval,spline_coeff,spline_eval,
                       gaussian,lu,iterative,matvec,norm2)
from app import save,load,history,session,jsondump

class Models(unittest.TestCase):
 def test_all_12_scenarios_and_graphs(self):
  for case in CASES:
   for scenario in SCENARIOS:
    with self.subTest(case=case,scenario=scenario):
     r=simulate(case,scenario);self.assertGreaterEqual(len(r['methods']),3)
     self.assertEqual(len(r['charts']),2)
     self.assertEqual(r['scenario'],scenario)
     for g in r['charts']:
      self.assertGreater(len(g['series']),0)
      for se in g['series']:
       self.assertGreater(len(se['points']),0)
       self.assertTrue(all(len(p)==2 and all(math.isfinite(v) for v in p) for p in se['points']))
     for m in r['methods']:
      self.assertTrue(math.isfinite(m['value']))
      self.assertTrue(math.isfinite(m['error_abs']))
      self.assertTrue(math.isfinite(m['residual']))

 def test_roots_analytical(self):
  f=lambda x:x*x-9
  self.assertLess(abs(bisection(f,0,5)['root']-3),1e-8)
  self.assertLess(abs(newton(f,lambda x:2*x,4)['root']-3),1e-8)
  self.assertLess(abs(secant(f,1,4)['root']-3),1e-8)
  for fn in (bisection,):
   with self.assertRaises(ValueError):fn(lambda x:x*x+1,-1,1)

 def test_integrals(self):
  f=lambda x:x*x*x
  for v in [trapezoid(f,0,1,1000),simpson(f,0,1,20),romberg(f,0,1,5)['value']]:self.assertAlmostEqual(v,.25,delta=.000002)
  with self.assertRaises(ValueError):simpson(f,0,1,7)

 def test_ode_accuracy(self):
  f=lambda t,y:[y[0]]
  p2=rk2(f,[1],1,20)[-1][1];p4=rk4(f,[1],1,20)[-1][1]
  self.assertLess(abs(p2-math.e),.002)
  self.assertLess(abs(p4-math.e),abs(p2-math.e)/100)

 def test_interpolation_reproduces_polynomial(self):
  xs=[0,1,2,3,4];g=lambda x:x*x*x-2*x+5;ys=list(map(g,xs))
  a=newton_coeff(xs,ys);M=spline_coeff(xs,ys)
  for t in [0,.4,1.6,3.8,4]:
   self.assertAlmostEqual(lagrange(xs,ys,t),g(t),delta=1e-9)
   self.assertAlmostEqual(newton_eval(xs,a,t),g(t),delta=1e-9)
  for x,y in zip(xs,ys):self.assertAlmostEqual(spline_eval(xs,ys,M,x),y,delta=1e-10)

 def test_mal_condicionamiento_no_es_estrés(self):
  n=simulate('extrusion','NORMAL');bad=simulate('extrusion','MAL_CONDICIONADO')
  self.assertAlmostEqual(n['reference']['tiempo_parada_s'],bad['reference']['tiempo_parada_s'])
  self.assertFalse(bad['methods'][1]['converged'])  # Newton derivada casi nula en raíz múltiple
  self.assertGreater(simulate('sensores','MAL_CONDICIONADO')['reference']['lebesgue_aproximado'],100)
  for s in SCENARIOS:
   d=simulate('hidrogel',s)
   for m in d['methods'][-5:]:self.assertTrue(m['converged'])
  self.assertGreater(simulate('hidrogel','MAL_CONDICIONADO')['reference']['condicion_infinito'],1e4)

 def test_linear_reference_4x4(self):
  A=[[4.,-1.,0.,0.],[-1.,4.,-1.,0.],[0.,-1.,4.,-1.],[0.,0.,-1.,4.]]
  xstar=[1.,2.,3.,4.];b=matvec(A,xstar)
  for y in [gaussian(A,b),lu(A,b)]+[iterative(A,b,m)[0] for m in ('Jacobi','Gauss-Seidel','Gradiente conjugado')]:
   self.assertLess(norm2([a-b for a,b in zip(y,xstar)]),1e-9)

 def test_validate_invalid_params(self):
  for p in [{'n':13},{'q0':0.},{'a':0.},{'beta':1.},{'ruido':.08}]:
   case=('extrusion' if 'n' in p or 'q0' in p or 'a' in p else 'sensores' if 'ruido' in p else 'hidrogel')
   with self.assertRaises(ValueError):simulate(case,'NORMAL',p)

class Database(unittest.TestCase):
 def test_save_close_reopen_reload_replay(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/'run.sqlite3';entry={'case':'hidrogel','scenario':'ESTRES','params':{'alpha':.12}}
   saved=save(path,entry)
   self.assertEqual(saved['id'],1)
   with session(path) as conn:
    self.assertEqual(conn.execute('SELECT COUNT(*) FROM ejecucion_metodo').fetchone()[0],8)
    self.assertGreater(conn.execute('SELECT COUNT(*) FROM iteracion_resultado').fetchone()[0],0)
   # Tras cerrar el contexto/conexión, se vuelve a abrir una base persistida en disco.
   recovered=load(path,saved['id']);self.assertEqual(recovered['input'],entry)
   self.assertEqual(recovered['sha256'],saved['sha256'])
   fresh=simulate(**{'case':entry['case'],'scenario':entry['scenario'],'params':entry['params']})
   self.assertEqual(hashlib.sha256(jsondump(fresh).encode('utf8')).hexdigest(),saved['sha256'])
   self.assertEqual(len(history(path)),1)
   self.assertEqual(len(recovered['result']['charts']),2)
   self.assertEqual(len(recovered['result']['methods']),8)

if __name__=='__main__':unittest.main()
