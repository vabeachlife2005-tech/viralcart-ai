"""Idempotent, fail-closed import of worker events from an authorized JSONL export."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import viralcart

def import_file(path, dry_run=False):
    existing=viralcart.read_events()
    seen={e['event_id'] for e in existing}
    candidates=[];duplicates=0
    for line_no,line in enumerate(Path(path).read_text(encoding='utf8').splitlines(),1):
        if not line.strip():continue
        try:
            e=json.loads(line)
            if e.get('event_id') in seen:
                duplicates+=1;continue
            viralcart.validate(e,existing+candidates)
            candidates.append(e);seen.add(e['event_id'])
        except (ValueError,KeyError,TypeError,json.JSONDecodeError) as exc:
            raise ValueError(f'line {line_no}: {exc}') from exc
    if not dry_run:
        for e in candidates:viralcart.record(e)
        viralcart.report()
    return {'accepted':len(candidates),'duplicates_skipped':duplicates,'dry_run':dry_run}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('jsonl');p.add_argument('--dry-run',action='store_true');args=p.parse_args()
    print(json.dumps(import_file(args.jsonl,args.dry_run),indent=2))
