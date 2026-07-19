import json

p='rc4_sprint8c_mapping_integration_results.json'
data=json.load(open(p,encoding='utf-8'))
print(type(data).__name__)
print(list(data.keys()))
books=data.get('books',[])
print('books', len(books))
if books:
    b=books[0]
    print('book keys', list(b.keys()))
    for k in ['file','title','summary_ir','builder_output','evaluation','synthesized_trace']:
        if k in b:
            v=b[k]
            print(k, type(v).__name__)
            if isinstance(v, dict):
                print('  keys', list(v.keys())[:20])
            if isinstance(v, list):
                print('  list len', len(v), 'first type', type(v[0]).__name__ if v else None)
    if 'synthesized_trace' in b and b['synthesized_trace']:
        print('first trace item keys', list(b['synthesized_trace'][0].keys()))
        print('first trace item', b['synthesized_trace'][0])
