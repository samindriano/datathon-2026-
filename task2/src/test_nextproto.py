import numpy as np, pandas as pd
from nextproto import NextProto, state_document

def fixtures():
    articles=pd.DataFrame({'article_id':[1,2,3,4],'title':['Alpha News','Beta Sport','Gamma News','Delta Sport']})
    cats=pd.DataFrame({'article_id':[1,2,3,4],'category':['subject.News.Main','subject.Sport.Main','subject.News.Main','subject.Sport.Main']})
    states=pd.DataFrame({'state_id':[1,2,3,4],'current_article_id':[1,1,2,2],'target_article_id':[3,4,3,4],'next_article_id':[3,4,3,4]})
    return states,articles,cats

def test_state_documents_are_prefixed():
    s,a,c=fixtures(); d=state_document(1,3,dict(zip(a.article_id,a.title)),{i:[x] for i,x in zip(c.article_id,c.category)})
    assert 'current_title_alpha' in d and 'target_title_gamma' in d and 'current_category_subject' in d

def test_fit_predict_and_mutation_invariance():
    s,a,c=fixtures(); m=NextProto.fit(s,a,c); p=m.predict(s,a,c); x=s.copy(); x['state_id']=-99; x['next_article_id']=999
    assert p.dtype==np.int64 and np.array_equal(p,m.predict(x,a,c))
    assert m.vectorizer.get_params()['ngram_range']==(1,2) and m.vectorizer.get_params()['sublinear_tf']
