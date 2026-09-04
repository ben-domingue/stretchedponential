import numpy as np, battery
rng=np.random.default_rng(42)
def simulate(r_true,n=6000,K=6,beta=1.5):
    x=rng.normal(0,1,n)
    w=r_true**np.arange(K-1); t=np.r_[0,np.cumsum(w[:-1])]
    t=t-np.mean(t)
    eta=beta*x
    cum=1/(1+np.exp(-(t[None,:]-eta[:,None])))
    cum=np.column_stack([np.zeros(n),cum,np.ones(n)])
    p=np.diff(cum,axis=1); p=np.clip(p,1e-12,None); p/=p.sum(1,keepdims=True)
    S=np.array([rng.choice(K,p=pi) for pi in p])+1
    return S,x
for rt in (1.0,1.24,1.41):
    est=[]
    for rep in range(5):
        S,x=simulate(rt)
        est.append(battery.battery(S,x,label="sim")['r'])
    print(f"true r={rt}: recovered {np.round(est,3)}  mean={np.mean(est):.3f}")
