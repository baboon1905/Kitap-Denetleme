from pathlib import Path


APP_TSX = Path(__file__).with_name("App.tsx").read_text(encoding="utf-8")


def assert_contains(fragment: str) -> None:
    assert fragment in APP_TSX, f"App.tsx PDF payload is missing: {fragment}"


assert_contains("const visibleSummary = (")
assert_contains("analiz_sonucu?.canonical_summary")
assert_contains("kitap_ozeti: visibleSummary")
assert_contains("analiz_sonucu: reportPayload")
assert_contains("payload.hata || payload.detay || message")
assert_contains("const [reportLoading, setReportLoading]")
assert_contains("setReportLoading(format)")
assert_contains("PDF hazÄ±rlanÄ±yor...")
assert_contains("disabled={Boolean(reportLoading)}")
