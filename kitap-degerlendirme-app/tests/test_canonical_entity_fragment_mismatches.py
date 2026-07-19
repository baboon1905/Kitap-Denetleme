import sys
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from theme_gain_analysis import _canonical_entity_fragment_mismatches


class TestCanonicalEntityFragmentMismatches(unittest.TestCase):
    def test_independent_canonical_place_suppresses_fragment_mismatch(self):
        payload = {
            "canonical_entity_store": {
                "PLACE:aradigim hindistan": {
                    "entity_type": "PLACE",
                    "canonical_form": "Aradığım Hindistan",
                },
                "PLACE:hindistan": {
                    "entity_type": "PLACE",
                    "canonical_form": "Hindistan",
                },
            }
        }

        self.assertEqual(
            [],
            _canonical_entity_fragment_mismatches(
                "Hindistan rotası anlatılır.", payload, "PLACE"
            ),
        )

    def test_missing_full_canonical_place_keeps_fragment_mismatch(self):
        payload = {
            "canonical_entity_store": {
                "PLACE:new york": {
                    "entity_type": "PLACE",
                    "canonical_form": "New York",
                }
            }
        }

        self.assertEqual(
            ["York"],
            _canonical_entity_fragment_mismatches(
                "York limanı anlatılır.", payload, "PLACE"
            ),
        )

    def test_independent_name_suppression_is_place_only(self):
        payload = {
            "canonical_entity_store": {
                "PERSON:new york": {
                    "entity_type": "PERSON",
                    "canonical_form": "New York",
                },
                "PERSON:york": {
                    "entity_type": "PERSON",
                    "canonical_form": "York",
                },
            }
        }

        self.assertEqual(
            ["York"],
            _canonical_entity_fragment_mismatches(
                "York konuşur.", payload, "PERSON"
            ),
        )


if __name__ == "__main__":
    unittest.main()
