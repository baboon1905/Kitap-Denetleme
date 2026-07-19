"""Example Sprint 9A Event Reconstruction Output

Demonstrates event extraction from actual Turkish book evidence
"""
import json
from runtime_v7.event_reconstructor import reconstruct_events


# Sample evidence from Turkish book analysis
example_evidence = {
    'setup': [
        {
            'text': 'Kristof Kolomb çocukluk yıllarında harita ve denizle ilgili efsanelerle meraklandı.',
            'source_sentence_id': 'p1:s1'
        },
        {
            'text': 'Genç yaşında denizci olma hayali kurmaya başladı.',
            'source_sentence_id': 'p2:s3'
        }
    ],
    'conflict': [
        {
            'text': 'Coğrafya bilginleri Kızıl Deniz\'in bulunması hakkında ters fikirler taşıdılar.',
            'source_sentence_id': 'p5:s2'
        },
        {
            'text': 'Kolomb\'un batı yoluyla Hindistan\'a ulaşma planı çoğu insan tarafından imkansız sayılıyordu.',
            'source_sentence_id': 'p8:s1'
        },
        {
            'text': 'Para ve gemi bulma konusunda büyük engeller vardı.',
            'source_sentence_id': 'p10:s4'
        }
    ],
    'events': [
        {
            'text': 'Üç gemiyle yolculuğa çıktı ve okyanusu geçti.',
            'source_sentence_id': 'p15:s1'
        },
        {
            'text': 'Uzun ve tehlikeli bir deniz yolculuğu yaşadı, fırtınalarla karşılaştı.',
            'source_sentence_id': 'p18:s3'
        },
        {
            'text': 'Nihayet yeni bir kıtaya ulaştı ve büyük bir keşif yaptı.',
            'source_sentence_id': 'p22:s2'
        }
    ],
    'resolution': [
        {
            'text': 'Kolomb\'un keşfi Avrupa ve Yeni Dünya arasındaki ilişkileri tamamen değiştirdi.',
            'source_sentence_id': 'p28:s1'
        },
        {
            'text': 'Harita ve coğrafya bilimi yeni verilerle zenginleşti ve insan tarihine yeni bir sayfa açıldı.',
            'source_sentence_id': 'p30:s2'
        }
    ]
}

# Known characters for actor extraction
known_characters = ['Kristof Kolomb', 'Kolomb', 'Columbus']

# Run event reconstruction
result = reconstruct_events(example_evidence, characters=known_characters)

# Display formatted output
print("=" * 80)
print("SPRINT 9A — EVENT RECONSTRUCTION LAYER")
print("RC4 — Book Event Analysis Example")
print("=" * 80)
print()

print(f"📊 RECONSTRUCTION SUMMARY")
print(f"   Total Events Extracted: {len(result['events'])}")
print(f"   Event Sequence Length: {len(result['event_sequence'])}")
print(f"   Reconstruction Quality Score: {result['event_reconstruction_quality']:.3f}")
print()

print(f"🎯 MAIN NARRATIVE ELEMENTS")
print(f"   Main Conflict: {result['main_conflict'][:60]}..." if len(result['main_conflict']) > 60 else f"   Main Conflict: {result['main_conflict']}")
print(f"   Resolution: {result['resolution'][:60]}..." if len(result['resolution']) > 60 else f"   Resolution: {result['resolution']}")
print()

print("📋 EVENTS EXTRACTED")
print("-" * 80)
for i, event in enumerate(result['events'], 1):
    print(f"\n[Event {i}] {event['event_id']}")
    print(f"   Actors:              {', '.join(event['actors']) if event['actors'] else 'None'}")
    print(f"   Action:              {event['action'][:50]}..." if len(event['action']) > 50 else f"   Action:              {event['action']}")
    print(f"   Conflict:            {event['conflict']}")
    print(f"   Importance:          {event['importance']:.3f}")
    print(f"   Source IDs:          {', '.join(event['source_sentence_ids'])}")

print("\n" + "=" * 80)
print("JSON OUTPUT FORMAT")
print("=" * 80)
print(json.dumps(result, indent=2))
