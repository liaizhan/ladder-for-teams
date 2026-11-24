import unittest

from ladder_teams import service
from ladder_teams.store import Store
from ladder_teams.themes import theme_of

BLOCKS = [
    "Manager: you are not ready to lead",
    "No time, too many tickets this sprint",
    "I don't know how to run a planning meeting",
]


class ServiceTest(unittest.TestCase):
    def setUp(self):
        service.use_store(Store(":memory:"))

    def build(self, member, blocks=BLOCKS, **extra):
        return service.build_member_ladder(
            team="payments", member=member, goal="Lead the Q1 release",
            me="Senior engineer, never led a release", blocks=blocks, **extra)

    def test_questions(self):
        sheet = service.get_questions()
        self.assertEqual([q["field"] for q in sheet["questions"]], ["goal", "me", "blocks", "fears"])

    def test_reading_starts_from_nearest_block(self):
        reading = self.build("m1", fears=["Others will expect more from me"])
        self.assertEqual(reading["kind"], "reading")
        self.assertEqual([s["zone"] for s in reading["steps"]], ["me", "block", "block", "block", "goal", "fear"])
        self.assertEqual(reading["nearest_block"], BLOCKS[0])
        self.assertEqual(reading["this_week"]["theme"], "approval")

    def test_too_few_blocks(self):
        reading = self.build("m1", blocks=BLOCKS[:2])
        self.assertEqual(reading["kind"], "error")

    def test_crisis_is_not_analysed_or_saved(self):
        reading = self.build("m1", blocks=BLOCKS[:2] + ["I don't want to live like this"])
        self.assertEqual(reading["kind"], "notice")
        self.assertEqual(reading["reason"], "crisis")
        self.assertEqual(service.weekly_step_for("payments", "m1")["kind"], "error")

    def test_themes(self):
        self.assertEqual(theme_of("No budget for this, too expensive"), "money")
        self.assertEqual(theme_of("I'm not good enough"), "confidence")
        self.assertEqual(theme_of("Waiting for approval from security"), "approval")
        self.assertEqual(theme_of("Others are smarter than me"), "confidence")
        self.assertEqual(theme_of("Something odd"), "other")

    def test_report_needs_three_people_and_hides_words(self):
        self.build("m1")
        self.build("m2")
        self.assertEqual(service.team_report("payments")["kind"], "error")
        self.build("m3")
        service.check_in("payments", "m1", True)
        service.check_in("payments", "m2", False)
        report = service.team_report("payments")
        self.assertEqual(report["kind"], "report")
        self.assertEqual(report["members"], 3)
        self.assertEqual(report["steps_done"], 1)
        self.assertNotIn("Manager", str(report))
        self.assertEqual(report["shared_blocks"][0]["members"], 3)
        self.assertTrue(all(b["members"] >= 2 for b in report["shared_blocks"]))


if __name__ == "__main__":
    unittest.main()
