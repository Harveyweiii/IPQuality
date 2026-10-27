import base64
import re
import shutil
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "ip.sh").read_text(encoding="utf-8")
BASH = shutil.which("bash") or str(Path(shutil.which("git")).parents[1] / "bin" / "bash.exe")
HELPER = re.search(r"^youtube_content_region\(\)\{[^\n]*\}", SOURCE, re.MULTILINE)


class YouTubeContentRegionTests(unittest.TestCase):
    def extract_region(self, html):
        self.assertIsNotNone(HELPER, "production YouTube region helper must exist")
        encoded = base64.b64encode(html.encode()).decode()
        script = f'{HELPER.group(0)}; youtube_content_region "$(printf %s {encoded}|base64 -d)"'
        return subprocess.check_output([BASH, "-c", script], text=True)

    def test_google_cn_reference_does_not_override_us_content_region(self):
        html = '<script>"contentRegion":"US"</script><a href="https://www.google.cn">Google</a> ad-free'
        region = self.extract_region(html)
        self.assertEqual(region, "US")
        self.assertNotEqual(region, "CN")

    def test_cn_content_region_is_still_detected(self):
        html = '<script>"contentRegion":"CN"</script> ad-free'
        self.assertEqual(self.extract_region(html), "CN")


if __name__ == "__main__":
    unittest.main()
