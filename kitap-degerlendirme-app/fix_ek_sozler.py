# ADIM 2'ye ek_sozler kontrolleri ekle
with open('evaluator_maarif.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Search for the location to insert
marker = "# ⭐ ADIM 3: Harmonic (ses uyumu)"
if marker in content:
    insert_code = '''
                # ek_sozler kontrolü - SADECE FALSE_POSITIVE'ler (bölüm, büyükbaba, defalarca, yayınevi, etc.)
                if "ek_sozler" in kelime_filter and kelime_filter["ek_sozler"]:
                    for sozcu in kelime_filter["ek_sozler"]:
                        sozcu_lower = sozcu.lower()
                        kelime_lower = kelime.lower()
                        metin_lower = metin_normalized.lower()
                        
                        # Sözcük kelime içinde geçiyor mu?
                        if (len(sozcu) > len(kelime) and 
                            kelime_lower in sozcu_lower and
                            sozcu_lower in metin_lower):
                            # Sözcüğün pozisyonunu kontrol et
                            search_pos = 0
                            while True:
                                sozcu_pos = metin_lower.find(sozcu_lower, search_pos)
                                if sozcu_pos == -1:
                                    break
                                
                                # Kelimenin bu sözcük içinde mi?
                                if sozcu_pos <= basla and basla < sozcu_pos + len(sozcu):
                                    return {
                                        "bagimsiz": False,
                                        "yapan_kelime": sozcu,
                                        "neden": f"'{sozcu}' sözcüğünün parçası"
                                    }
                                
                                search_pos = sozcu_pos + 1
        
'''
    content = content.replace(marker, insert_code + marker)
    
    with open('evaluator_maarif.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print('ek_sozler kontrolleri ADIM 2 ye eklendi')
else:
    print('Marker bulunamadı')
