def score(text,ref):
 from score_adapter import score_record
 s=score_record(text,ref);a=s['answer'];g=ref['gold'];rev={'actor':g['undergoer'],'undergoer':g['actor']};bg=ref.get('background_gold')
 C=a==g;R=a==rev
 if C:category='C'
 elif R:category='R'
 elif a and any(v is None for v in a.values()):category='NULL'
 elif bg and a in [bg,{'actor':bg['undergoer'],'undergoer':bg['actor']}]:category='BACKGROUND'
 elif a and any(v in set((bg or {}).values()) for v in a.values()):category='MIXED_BACKGROUND'
 else:category='OTHER_U'
 return {'C':int(C),'R':int(R),'U':int(not(C or R)),'category':category,'legacy_score':s['score'],'legacy_U':int(s['score']=='U'),'answer':a,'format_ok':s['format_ok'],'null':s.get('raw_null',False),'object_as_actor':ref['stage']=='P1_OBJECT' and bool(a) and a.get('actor')==g['undergoer']}
