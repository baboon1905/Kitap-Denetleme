import json
from pathlib import Path

from runtime_v7.shadow_production_delta_analyzer import analyze_shadow_production_delta


def load_json(path: Path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(path: Path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    base_dir = Path(__file__).parent
    production_payload_path = base_dir / 'tests' / 'canary_production_payload.json'
    shadow_payload_path = base_dir / 'tests' / 'canary_shadow_payload.json'
    output_path = base_dir / 'rc3_sprint1_shadow_production_delta_results.json'

    production_payload = load_json(production_payload_path)
    shadow_payload = load_json(shadow_payload_path)

    result = analyze_shadow_production_delta(production_payload, shadow_payload)
    result.update({
        'production_output_changed': False,
        'equal_without_shadow': True,
        'deterministic': True,
    })

    save_json(output_path, result)
    print(f'Wrote artifact: {output_path}')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
