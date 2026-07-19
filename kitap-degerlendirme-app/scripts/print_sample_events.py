import json
import sys
import os

# Ensure project root is on sys.path so runtime_v7 can be imported when
# running this script directly.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from runtime_v7.event_reconstructor import reconstruct_events

evidence = {
    'setup': [
        'Kolomb, Atlas Okyanusu üzerinde batıya doğru yelken açtı.',
    ],
    'conflict': [
        'Fırtına nedeniyle mürettebat umudunu kaybetti.',
    ],
    'events': [
        'Karaya ulaştık ve yeni bir dünya keşfettik.',
    ],
    'resolution': [
        'Yolculuk başarıyla sonuçlandı.',
    ],
}

res = reconstruct_events(evidence, payload_file='test_payload', book_index=1)
print(json.dumps(res.get('events', [])[:4], ensure_ascii=False, indent=2))
