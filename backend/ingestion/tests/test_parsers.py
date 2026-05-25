from django.test import SimpleTestCase
from ingestion import views

class ParserTests(SimpleTestCase):
    def test_parse_number_variants(self):
        self.assertEqual(views.parse_number('1,234.56'), 1234.56)
        self.assertEqual(views.parse_number('1.234,56'), 1234.56)
        self.assertEqual(views.parse_number('1234,56'), 1234.56)
        self.assertEqual(views.parse_number('1 234,56'), 1234.56)
        self.assertEqual(views.parse_number('-1.234,56'), -1234.56)
        self.assertIsNone(views.parse_number(''))
        self.assertIsNone(views.parse_number(None))

    def test_parse_date_formats(self):
        self.assertEqual(str(views.parse_date('2026-05-24')), '2026-05-24')
        self.assertEqual(str(views.parse_date('05/24/2026')), '2026-05-24')
        self.assertEqual(str(views.parse_date('24.05.2026')), '2026-05-24')
        self.assertIsNone(views.parse_date('not a date'))
