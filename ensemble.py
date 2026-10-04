#!/usr/bin/env python3
"""Portable, reproducible runner. Retains every run, including censored and failed runs."""
import argparse,hashlib,json,subprocess,time,statistics,math
from pathlib import Path
from audit_replay import load,audit

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def wilson(successes,n):
    if not n:return None
    z=1.959963984540054;p=successes/n;d=1+z*z/n
    m=(p+z*z/(2*n))/d;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return [max(0,m-h),min(1,m+h)]

def run(args):
    root=Path(args.output);root.mkdir(parents=True,exist_ok=False)
    executable=Path(args.executable).resolve();manifest=Path(args.manifest).resolve() if args.manifest else None
    records=[]
    for rng in args.rng_seeds:
        name=f'rng_{rng}';j=root/(name+'.jsonl');t=root/(name+'.tsv');log=root/(name+'.log')
        command=[str(executable),'--seed',str(args.seed),'--rng-seed',str(rng),'--rng-help',str(args.rng_help),'--runtime-seconds',str(args.seconds),'--no-schems','--quiet','--replay',str(t.resolve()),'--replay-jsonl',str(j.resolve())]
        if manifest:command+=['--seed-manifest',str(manifest)]
        if args.steps: command+=['--audit-max-steps',str(args.steps)]
        start=time.monotonic()
        with log.open('w') as handle: proc=subprocess.run(command,stdout=handle,stderr=subprocess.STDOUT)
        result={'seed_u64':str(args.seed),'rng_seed_u64':str(rng),'command':command,'exit_code':proc.returncode,'wall_seconds':time.monotonic()-start,'executable_sha256':sha(executable),'manifest_sha256':sha(manifest) if manifest else None,'assisted':bool(args.rng_help),'status':'failed'}
        if j.exists():
            try:
                evidence=audit(load(j));result['audit']=evidence
                terminal=evidence.get('terminal')
                if proc.returncode==0 and terminal and terminal['completed'] and not any(f['severity']=='bug' for f in evidence['findings']):result['status']='completed'
                elif proc.returncode==1 and terminal and terminal['censored']:result['status']='right_censored'
                elif proc.returncode==1 and terminal: result['status']='incomplete'
            except ValueError as exc:result['error']=str(exc)
        records.append(result)
        (root/'runs.json').write_text(json.dumps(records,indent=2)+'\n')
        print(f'{name}: {result["status"]}',flush=True)
    completed=[r['audit']['terminal']['time_years'] for r in records if r['status']=='completed']
    summary={'n':len(records),'status_counts':{s:sum(r['status']==s for r in records) for s in ('completed','right_censored','incomplete','failed')},'assisted':bool(args.rng_help),'completion_fraction':len(completed)/len(records), 'completion_fraction_wilson_95':wilson(len(completed),len(records)), 'completed_times_only_median_model_years':statistics.median(completed) if completed else None,
      'interpretation':'Completion fraction is for this computing budget, conditional seed and model. Wall-time censoring depends on event workload; completed-only times and this interval do not estimate the unconditional vanilla completion-time distribution. Distinct user-supplied RNG seeds are required, but independence is a modeling assumption.'}
    (root/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--executable',default=str(Path(__file__).parent/'bin/mcmacro'));p.add_argument('--manifest');p.add_argument('--seed',type=int,required=True);p.add_argument('--rng-seeds',type=int,nargs='+',required=True);p.add_argument('--rng-help',type=int,choices=range(101),default=0);p.add_argument('--steps',type=int,default=0);p.add_argument('--seconds',type=float,default=30);p.add_argument('--output',required=True);args=p.parse_args()
    if args.steps<0 or args.seconds<=0 or not 0<=args.seed<2**64 or any(not 0<=x<2**64 for x in args.rng_seeds) or len(set(args.rng_seeds))!=len(args.rng_seeds):p.error('Require positive seconds, uint64 seeds and distinct RNG seeds')
    run(args)
