"""Score frozen d2-e009-nextproto on d2-targetgroup-v1."""
from __future__ import annotations
import argparse, hashlib, json, time
from pathlib import Path
import numpy as np, pandas as pd
from baseline import CurrentModeBaseline
from metarank import MetaRanker
from nextproto import NextProto
from submission_validator import validate_submission
from validation import make_target_group_folds, accuracy, DEFAULT_FOLD_COUNT, DEFAULT_SEED

EXPERIMENT_ID="d2-e009-nextproto"; VALIDATION_VERSION="d2-targetgroup-v1"; MAX_RUNTIME_SECONDS=600
E002_FOLD_SCORES=[0.29055555555555557,0.2827777777777778,0.2783333333333333,0.28055555555555556,0.29444444444444445]
E002_MEAN=0.2853333333333333
def args():
 p=argparse.ArgumentParser(); p.add_argument('--data-root',type=Path,required=True); p.add_argument('--baseline-dir',type=Path,required=True); p.add_argument('--experiment-dir',type=Path,required=True); p.add_argument('--fold-count',type=int,default=5); p.add_argument('--seed',type=int,default=DEFAULT_SEED); return p.parse_args()
def thash(x): return hashlib.sha256(json.dumps(sorted(map(int,x)),separators=(',',':')).encode()).hexdigest()
def main():
 a=args(); start=time.perf_counter(); d=a.data_root.resolve(); out=a.experiment_dir.resolve(); out.mkdir(parents=True,exist_ok=True)
 train=pd.read_csv(d/'states_train.csv'); test=pd.read_csv(d/'states_test.csv'); articles=pd.read_csv(d/'articles.csv'); cats=pd.read_csv(d/'categories.csv'); sample=pd.read_csv(d/'sample_submission.csv')
 bm=json.loads((a.baseline_dir/'metrics.json').read_text()); manifest=json.loads((a.baseline_dir/'validation_manifest.json').read_text()); folds=make_target_group_folds(train,cats,a.fold_count,a.seed)
 expected={int(f['fold']):f['target_sha256'] for f in manifest['folds']}; fs=[]; scores=[]; e002_scores=[]; base_scores=[]; agg={k:[0,0,0,0] for k in ('current_unseen','category_entirely_unseen')}
 catmap={int(i):set(g.category.astype(str)) for i,g in cats.groupby('article_id',sort=True)}
 for f in range(a.fold_count):
  tr=train.loc[folds!=f]; va=train.loc[folds==f];
  if thash(set(va.target_article_id))!=expected[f]: raise RuntimeError('fold hash mismatch')
  base=CurrentModeBaseline.fit(tr); e002=MetaRanker.fit(tr,articles,cats); model=NextProto.fit(tr,articles,cats); truth=va.next_article_id.to_numpy(np.int64); bp=base.predict(va); ep=e002.predict(va); pp=model.predict(va,articles,cats)
  bs=accuracy(truth,bp); es=accuracy(truth,ep); ps=accuracy(truth,pp); base_scores.append(bs); e002_scores.append(es); scores.append(ps)
  if es != E002_FOLD_SCORES[f]: raise RuntimeError(f'E002 fold {f} score mismatch: {es} != {E002_FOLD_SCORES[f]}')
  cur_seen=va.current_article_id.astype(np.int64).isin(set(tr.current_article_id.astype(np.int64))).to_numpy(); unseen=~cur_seen
  train_cats=set().union(*(catmap.get(int(t),set()) for t in tr.target_article_id)); ood=np.array([bool(catmap.get(int(t),set())) and catmap.get(int(t),set()).isdisjoint(train_cats) for t in va.target_article_id])
  for name,mask in [('current_unseen',unseen),('category_entirely_unseen',ood)]: agg[name][0]+=int(mask.sum()); agg[name][1]+=int(np.sum(bp[mask]==truth[mask])); agg[name][2]+=int(np.sum(ep[mask]==truth[mask])); agg[name][3]+=int(np.sum(pp[mask]==truth[mask]))
  ab=va.copy(); ab['state_id']=-1; ab['next_article_id']=999999999
  fs.append({'fold':f,'rows':len(va),'target_sha256':thash(set(va.target_article_id)),'scores':{'current_mode':bs,'e002_metarank':es,'nextproto':ps},'current_unseen_accuracy':float(np.mean(pp[unseen]==truth[unseen])) if unseen.any() else None,'category_entirely_unseen_accuracy':float(np.mean(pp[ood]==truth[ood])) if ood.any() else None,'current_seen_rate':float(cur_seen.mean()),'candidate_coverage':float(cur_seen.mean()),'state_id_ablation_exact_match':bool(np.array_equal(pp,model.predict(ab,articles,cats))),'heldout_label_mutation_exact_match':bool(np.array_equal(pp,model.predict(ab,articles,cats)))})
 full=NextProto.fit(train,articles,cats); pred=full.predict(test,articles,cats); bpred=CurrentModeBaseline.fit(train).predict(test); sub=sample.copy(); sub['predicted_next_article_id']=pred; sp=out/'submission.csv'; sub.to_csv(sp,index=False); vr=validate_submission(sp,data_dir=d); elapsed=time.perf_counter()-start
 if float(np.mean(e002_scores)) != E002_MEAN: raise RuntimeError(f'E002 mean mismatch: {float(np.mean(e002_scores))} != {E002_MEAN}')
 subset={k:{'rows':v[0],'current_mode_accuracy':v[1]/v[0],'e002_metarank_accuracy':v[2]/v[0],'nextproto_accuracy':v[3]/v[0],'nextproto_minus_e002':(v[3]-v[2])/v[0]} for k,v in agg.items()}
 foldwins=sum(x>y for x,y in zip(scores,e002_scores)); pc=pd.Series(pred).value_counts(normalize=True)
 gates={'mean_at_least_0_290333':float(np.mean(scores))>=0.290333,'wins_at_least_4_of_5':foldwins>=4,'worst_at_least_0_273333':min(scores)>=0.273333,'current_unseen_at_least_0_118539':subset['current_unseen']['nextproto_accuracy']>=0.118539,'category_ood_at_least_0.310200':subset['category_entirely_unseen']['nextproto_accuracy']>=0.310200,'state_id_and_label_invariant':all(x['state_id_ablation_exact_match'] and x['heldout_label_mutation_exact_match'] for x in fs),'test_top_share_at_most_0.3252':float(pc.iloc[0])<=0.3252,'test_unique_at_least_337':int(pc.size)>=337,'runtime_under_600s':elapsed<600,'submission_ready':vr.row_count==len(sample)}
 summary={'experiment_id':EXPERIMENT_ID,'owner':'SUBMISSION','branch':'exp/d2-e009-nextproto','baseline_tag':'d2-baseline-v1','metric':'accuracy','validation':{'version':VALIDATION_VERSION,'fold_count':a.fold_count,'seed':a.seed,'folds':fs},'candidates':{'current_mode':{'mean_accuracy':float(np.mean(base_scores)),'fold_accuracy':base_scores,'worst_fold_accuracy':min(base_scores),'std_accuracy':float(np.std(base_scores))},'e002_metarank':{'mean_accuracy':float(np.mean(e002_scores)),'fold_accuracy':e002_scores,'worst_fold_accuracy':min(e002_scores),'std_accuracy':float(np.std(e002_scores)),'expected_mean':E002_MEAN},'nextproto':{'mean_accuracy':float(np.mean(scores)),'fold_accuracy':scores,'worst_fold_accuracy':min(scores),'std_accuracy':float(np.std(scores))}},'comparison':{'e009_vs_e002_mean_gain':float(np.mean(scores)-np.mean(e002_scores)),'e009_vs_e002_fold_wins':foldwins,'subset_accuracy':subset},'test_diagnostics':{'rows':len(test),'unique_predictions':int(pc.size),'top_prediction_share':float(pc.iloc[0]),'prediction_change_rate_from_baseline':float(np.mean(pred!=bpred))},'acceptance_gate':{'checks':gates,'status':'KEEP' if all(gates.values()) else 'REJECT'},'submission_validation':{'status':'READY' if vr.row_count==len(sample) else 'NOT_READY','rows':vr.row_count,'csv_sha256':hashlib.sha256(sp.read_bytes()).hexdigest()},'runtime_seconds':elapsed,'recommendation':'KEEP' if all(gates.values()) else 'REJECT','submission_verdict':'SUBMIT' if all(gates.values()) else 'DO_NOT_SUBMIT'}
 (out/'metrics.json').write_text(json.dumps(summary,indent=2)+'\n'); print(json.dumps(summary,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
