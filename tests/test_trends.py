import unittest
from pathlib import Path
from pipeline.trends import parse_trends_rss, parse_traffic, parse_news_rss
from pipeline.classify import classify, load_config

ROOT = Path(__file__).resolve().parents[1]
CFG = load_config(ROOT / "config" / "channels.json")


class TrendsTest(unittest.TestCase):
    def setUp(self):
        self.trends = {t.query: classify(t, CFG) for t in parse_trends_rss((ROOT / "tests/fixtures/trends_ua.xml").read_bytes())}

    def test_traffic(self):
        self.assertEqual(parse_traffic("10K+"), 10000)
        self.assertEqual(parse_traffic("2 тис.+"), 2000)
        self.assertEqual(parse_traffic("1M+"), 1000000)

    def test_channels(self):
        expect = {"13 листопада": "dim", "кернел": "ekonomika", "масло": "yizha", "кушнер": "polityka",
                  "мозес ітаума": "sport", "молодіжна збірна u-21 україни з футболу": "sport",
                  "spacex starshield": "svit", "євро": "ekonomika", "безробіття": "ekonomika"}
        for q, ch in expect.items():
            self.assertEqual(self.trends[q].channel, ch, q)

    def test_skips(self):
        self.assertIsNone(self.trends["злочин"].channel)
        self.assertIn("негативна", self.trends["злочин"].skipped_reason)
        self.assertIsNone(self.trends["outlook"].channel)

    def test_prefix_rules(self):
        from pipeline.trends import Trend
        self.assertNotEqual(classify(Trend("голова сільради"), CFG).channel, "sport")
        self.assertNotEqual(classify(Trend("цікаві факти"), CFG).channel, "yizha")

    def test_news_rss(self):
        xml = b'<rss><channel><item><title>T</title><link>https://a</link><source url="x">Src</source></item></channel></rss>'
        n = parse_news_rss(xml)
        self.assertEqual((n[0].title, n[0].source), ("T", "Src"))


if __name__ == "__main__":
    unittest.main()
