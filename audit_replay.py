#!/usr/bin/env python3
"""Validate replay evidence without treating sampled records as a full inventory."""
import argparse, json, math
from collections import Counter
from pathlib import Path

def load(path):
    rows=[]
    for line_no,line in enumerate(Path(path).read_text(encoding='utf-8-sig').splitlines(),1):
        if not line.strip(): continue
        try: row=json.loads(line,parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
        except ValueError as exc: raise ValueError(f'{path}:{line_no}: {exc}') from exc
        if not isinstance(row,dict) or not isinstance(row.get('kind'),str):
            raise ValueError(f'{path}:{line_no}: expected a record object with kind')
        if 'time_years' in row and (not isinstance(row['time_years'],(int,float)) or isinstance(row['time_years'],bool) or not math.isfinite(row['time_years']) or row['time_years']<0):
            raise ValueError(f'{path}:{line_no}: invalid time_years')
        rows.append(row)
    if sum(x['kind']=='world_manifest' for x in rows)!=1:
        raise ValueError(f'{path}: expected exactly one world_manifest')
    return rows

def audit(rows):
    milestones=[x for x in rows if x['kind']=='milestone' and x.get('event')=='dragon_damage']
    resources=[x for x in rows if x.get('event')=='golem_damaged_dragon']
    findings=[]
    pairs=[]
    if resources and len(resources)==len(milestones) and all((a.get('value_a'),a.get('value_b'))==(b.get('value'),b.get('remaining')) for a,b in zip(milestones,resources)):
        pairs=list(zip(milestones,resources))
        mismatches=sum(abs(a['time_years']-b['time_years'])>1e-5 for a,b in pairs)
        if mismatches: findings.append({'severity':'bug','code':'damage_clock_mismatch','count':mismatches})
    elif resources: findings.append({'severity':'review','code':'damage_resource_pairing_incomplete'})
    hp=200
    for i,x in enumerate(milestones):
        if x.get('value_b')!=max(0,hp-x.get('value_a',0)):
            findings.append({'severity':'bug','code':'health_transition_inconsistent','damage_index':i})
        hp=x.get('value_b',hp)
    true_damage=resources if pairs else milestones
    true_damage=sorted(true_damage,key=lambda x:x['time_years'])
    stale=0
    for x in rows:
        if x['kind']!='counter_keyframe' or 'dragon_health' not in x: continue
        preceding=[y for y in true_damage if y['time_years']<=x['time_years']]
        if preceding:
            expected=preceding[-1].get('remaining',preceding[-1].get('value_b'))
            if x['dragon_health']>expected: stale+=1
    if stale: findings.append({'severity':'bug','code':'counter_health_regression','count':stale})
    timed=[x['time_years'] for x in rows if 'time_years' in x]
    manifest=next(x for x in rows if x['kind']=='world_manifest')
    terminal=next((x for x in reversed(rows) if x['kind']=='run_summary'),None)
    completed=any(x['kind']=='milestone' and x.get('event')=='dragon_dead' for x in rows)
    if terminal:
        if terminal['completed']!=completed: findings.append({'severity':'bug','code':'terminal_completion_mismatch'})
        for key in ('golem_accounting_delta','skeleton_accounting_delta','creeper_accounting_delta'):
            if terminal.get(key)!=0: findings.append({'severity':'bug','code':'resource_accounting_nonzero','field':key})
    return {'records':len(rows),'kinds':dict(Counter(x['kind'] for x in rows)),
        'seed_u64':str(manifest.get('seed_u64',manifest['seed'])),
        'rng_seed_u64':str(manifest.get('rng_seed_u64',manifest['rng_seed'])),
        'damage_events':len(milestones),'damage_sum':sum(x['value_a'] for x in milestones),
        'last_damage_health':hp if milestones else None,'completed':completed,
        'terminal':terminal,'adjacent_time_reversals':sum(b<a for a,b in zip(timed,timed[1:])),
        'time_reversal_note':'Emission order can backfill carrier histories; this count alone is not proof of a bug.',
        'damage_time_range': [min(x['time_years'] for x in true_damage),max(x['time_years'] for x in true_damage)] if true_damage else None,
        'findings':findings,'full_inventory_certified':False}

def reconcile_damage(rows):
    """Explicit derivative: only repair an unambiguous, exact damage/health pairing."""
    import copy
    rows=copy.deepcopy(rows)
    a=[x for x in rows if x['kind']=='milestone' and x.get('event')=='dragon_damage']
    b=[x for x in rows if x.get('event')=='golem_damaged_dragon']
    if not b or len(a)!=len(b) or not all((x['value_a'],x['value_b'])==(y['value'],y['remaining']) for x,y in zip(a,b)):
        raise ValueError('No complete, exact damage/health pairing; refusing to infer timestamps')
    for x,y in zip(a,b):
        x['audit_original_time_years']=x['time_years'];x['time_years']=y['time_years']
        x['audit_correction']='Timestamp copied from matching resource event; original evidence preserved separately.'
    return rows

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('replay');p.add_argument('--output');p.add_argument('--reconcile-damage')
    args=p.parse_args();rows=load(args.replay); report=audit(rows)
    text=json.dumps(report,indent=2,allow_nan=False)
    if args.output: Path(args.output).write_text(text+'\n')
    else: print(text)
    if args.reconcile_damage: Path(args.reconcile_damage).write_text(''.join(json.dumps(x,allow_nan=False)+'\n' for x in reconcile_damage(rows)))
