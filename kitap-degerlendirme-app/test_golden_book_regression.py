from quality_build_regression import run_build_regression
from quality_regression_dataset import GOLDEN_BOOKS


assert len(GOLDEN_BOOKS) >= 6
report = run_build_regression(write_report=False)
assert report["passed"] is True, report
assert report["failures"] == [], report
