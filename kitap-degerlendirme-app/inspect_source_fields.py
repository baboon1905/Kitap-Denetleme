import json

p='rc4_sprint8c_mapping_integration_results.json'
data=json.load(open(p,encoding='utf-8'))
books=data.get('books',[])
keys=['source_sentence_id','sentence_id','id','page','source','evidence_id','index']
counts={k:0 for k in keys}
samples={k:[] for k in keys}

for book in books:
    for item in book.get('synthesized_trace', []):
        if isinstance(item, dict):
            for k in keys:
                if k in item:
                    counts[k]+=1
                    if len(samples[k]) < 3:
                        samples[k].append(item.get(k))

print('books', len(books))
print('counts', counts)
print('samples', samples)
