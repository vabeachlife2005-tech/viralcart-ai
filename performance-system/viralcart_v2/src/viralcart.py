"""ViralCart evidence-first local scoreboard. Python 3.10+, stdlib only."""
import argparse,csv,json,os,sys,hashlib
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
EVENTS=DATA/'events.jsonl'
AUDIT=DATA/'audit.jsonl'
KINDS={'lead','outreach_approved','email_sent','email_bounced','email_optout','reply_auto','reply_human','conversation_qualified','order_paid','creative_accepted','repeat_order','worker_run','experiment'}
WORKERS={'lead','creative','systems','website','growth'}
SENSITIVE={'email_sent','outreach_approved','order_paid','repeat_order'}
REQUIRED={'event_id','occurred_at','kind','source','evidence','status'}

def now(): return datetime.now(timezone.utc).isoformat()
def read_events():
    if not EVENTS.exists(): return []
    with EVENTS.open() as f:return [json.loads(x) for x in f if x.strip()]
def append(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('a',encoding='utf8') as f:f.write(json.dumps(obj,sort_keys=True,ensure_ascii=False)+'\n')
def validate(e, existing=None):
    if not isinstance(e,dict):raise ValueError('event must be object')
    missing=REQUIRED-set(e)
    if missing:raise ValueError('missing '+','.join(sorted(missing)))
    if e['kind'] not in KINDS:raise ValueError('unknown kind')
    if e['status'] not in ('verified','estimated','hypothesis','blocked'):raise ValueError('invalid status')
    if not e['evidence'] or not e['source']:raise ValueError('source and evidence required')
    try:datetime.fromisoformat(e['occurred_at'].replace('Z','+00:00'))
    except Exception:raise ValueError('invalid timestamp')
    if existing and e['event_id'] in {x['event_id'] for x in existing}:raise ValueError('duplicate event_id')
    if e['kind'] in SENSITIVE and e['status']=='verified' and not e.get('approval_ref') and e['kind'] in {'outreach_approved','email_sent'}:raise ValueError('approval_ref required')
    if e['kind']=='worker_run':
        if e.get('worker') not in WORKERS:raise ValueError('invalid worker')
        for k in ('deliverable','next_action','owner'): 
            if not e.get(k):raise ValueError('worker_run requires '+k)
    if e['kind'] in {'order_paid','repeat_order'} and e['status']=='verified':
        if not isinstance(e.get('amount_usd'),(int,float)) or e['amount_usd']<0:raise ValueError('verified order needs nonnegative amount_usd')
    return e

def record(e):
    existing=read_events();validate(e,existing)
    append(EVENTS,e)
    append(AUDIT,{'at':now(),'action':'record','event_id':e['event_id'],'sha256':hashlib.sha256(json.dumps(e,sort_keys=True).encode()).hexdigest()})

def summarize(events):
    v=[e for e in events if e['status']=='verified']
    count=lambda kind:sum(e['kind']==kind for e in v)
    revenue=sum(e.get('amount_usd',0) for e in v if e['kind'] in ('order_paid','repeat_order'))
    sent=count('email_sent');human=count('reply_human');orders=count('order_paid')+count('repeat_order')
    return {'verified_emails_sent':sent,'verified_bounces':count('email_bounced'),'verified_optouts':count('email_optout'),'verified_auto_replies':count('reply_auto'),'verified_human_replies':human,'verified_qualified_conversations':count('conversation_qualified'),'verified_paid_orders':orders,'verified_revenue_usd':round(revenue,2),'human_reply_rate':round(human/sent,4) if sent else None,'paid_conversion_rate':round(orders/sent,4) if sent else None,'worker_runs':count('worker_run'),'event_count':len(events)}

def score(e):
    if e['kind']!='worker_run':raise ValueError('score only worker_run')
    if e['status']!='verified':return None
    rubric=e.get('rubric',{})
    maxima={'evidence':30,'accuracy':25,'impact':20,'completion':15,'next_experiment':10}
    if not rubric:return None
    for k,m in maxima.items():
        if k not in rubric or not isinstance(rubric[k],(int,float)) or not 0<=rubric[k]<=m:raise ValueError('invalid rubric '+k)
    return sum(rubric.values())

def report():
    ev=read_events();s=summarize(ev);runs=[x for x in ev if x['kind']=='worker_run'];rows=[]
    for worker in sorted(WORKERS):
        r=sorted((x for x in runs if x.get('worker')==worker),key=lambda x:x['occurred_at'],reverse=True)
        latest=r[0] if r else None
        rows.append({'worker':worker,'last_run':latest['occurred_at'] if latest else None,'status':latest['status'] if latest else 'not_recorded','score':score(latest) if latest else None,'deliverable':latest.get('deliverable') if latest else None,'evidence':latest.get('evidence') if latest else None,'blocker':latest.get('blocker') if latest else None})
    out={'generated_at':now(),'kpis':s,'workers':rows,'note':'Only manually/imported verified events count; automation results are not automatically synced.'}
    (ROOT/'reports').mkdir(exist_ok=True)
    (ROOT/'reports'/'latest.json').write_text(json.dumps(out,indent=2)+'\n')
    with (ROOT/'reports'/'workers.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
    return out

def main():
    p=argparse.ArgumentParser();sp=p.add_subparsers(dest='cmd',required=True)
    r=sp.add_parser('record');r.add_argument('file')
    sp.add_parser('report');sp.add_parser('validate')
    a=p.parse_args()
    if a.cmd=='record':
        e=json.loads(Path(a.file).read_text());record(e);print('recorded',e['event_id'])
    elif a.cmd=='report':print(json.dumps(report(),indent=2))
    else:
        es=read_events();seen=[]
        for e in es:validate(e,seen);seen.append(e)
        print('validated',len(es),'events')
if __name__=='__main__':main()
