import unittest

from narrative_type_classifier import classify_narrative_type


class NarrativeTypeClassifierTests(unittest.TestCase):
    def test_core_types(self):
        self.assertEqual(
            classify_narrative_type(
                "Denizci haritayi inceledi, saraydan destek istedi ve seferde firtinayla mucadele etti.",
                book_type="tarihi biyografi",
            ).narrative_type,
            "historical_biography",
        )
        self.assertEqual(
            classify_narrative_type("Ali bir tavsan sahiplendi, onu besledi ve bakim sorumlulugunu ogrendi.").narrative_type,
            "animal_responsibility_story",
        )
        self.assertEqual(
            classify_narrative_type("Bilimsel deney ve gozlem kavrami orneklerle aciklanir.").narrative_type,
            "information_book",
        )
        self.assertEqual(
            classify_narrative_type("Ela sihirli tohumu buldu, buyulu bahcede sabirla bekledi.").narrative_type,
            "fairy_tale",
        )
        self.assertEqual(
            classify_narrative_type("Gizemli krallikta ejderha ve karabasan korkusu olaylari degistirdi.").narrative_type,
            "fantasy_story",
        )


if __name__ == "__main__":
    unittest.main()
