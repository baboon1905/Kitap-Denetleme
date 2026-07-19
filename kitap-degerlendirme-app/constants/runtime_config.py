"""
Runtime configuration constants for report generation and output handling.

These constants define file names, MIME types, output paths, and internal
instrumentation keys used throughout the Flask application.
"""

# Debug and instrumentation output files
DEBUG_FLASK_VERSION_TXT = "debug_flask_version.txt"
API_RESPONSE_PATH = "api_response"

# Report output filename suffixes (used in send_file with kitap_adi prefix)
TEACHER_REPORT_FILENAME_SUFFIX = "_ogretmen_raporu.pdf"
THEME_REPORT_FILENAME_SUFFIX = "_tema_kazanim.pdf"
THEME_REPORT_WORD_FILENAME_SUFFIX = "_tema_kazanim.doc"
MAARIF_REPORT_FILENAME_SUFFIX = "_maarif_rapor.pdf"

# MIME types for send_file responses
APPLICATION_JSON = "application/json"
APPLICATION_PDF = "application/pdf"
APPLICATION_MSWORD = "application/msword"
APPLICATION_VND_OPENXMLFORMATS_OFFICEDOCUMENT_SPREADSHEETML_SHEET = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

# Visual content analysis field key
VISUAL_CONTENT_ANALYSIS_COMPLETED_FIELD = "gorsel_icerik_analizi_yapildi"

# Runtime status constants (used for structured runtime decisions)
STATUS_UNRELIABLE_SUMMARY = "UNRELIABLE_SUMMARY"
REPORT_STATUS_MISSING_ANALYSIS = "MISSING_ANALYSIS"

# API route suffix constants
TEACHER_PDF_SUFFIX = "/teacher-pdf"

# Organization labels
ORG_MAARIF_MEB_LABEL = "Maarif/MEB"

# XLSX/XML template constants for Excel package generation
XLSX_XML_DECL = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
XLSX_WORKSHEET_OPEN = '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
XLSX_WORKBOOK_OPEN = '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
XLSX_RELS_OPEN = '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
XLSX_WORKBOOK_RELS_OPEN = '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
XLSX_CONTENT_TYPES = '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
XLSX_RELS_PATH = "_rels/.rels"
XLSX_WORKBOOK_PATH = "xl/workbook.xml"
XLSX_WORKBOOK_RELS_PATH = "xl/_rels/workbook.xml.rels"
XLSX_WORKSHEET_PATH = "xl/worksheets/sheet1.xml"


def normalize_summary_status(value: str) -> str:
	"""Normalize various summary-status payloads to structured status constants.

	Accepts existing user-facing Turkish messages and returns the internal
	status constant. Returns None if no mapping applies.
	"""
	if not value:
		return None
	v = str(value).strip().lower()
	if v in ("özet güvenilir üretilemedi.", "ozet guvenilir uretilemedi."):
		return STATUS_UNRELIABLE_SUMMARY
	return None


def normalize_report_status(value: str) -> str:
	"""Normalize report status textual values to structured constants.

	Maps 'Eksik Analiz' => REPORT_STATUS_MISSING_ANALYSIS for compatibility.
	"""
	if not value:
		return None
	v = str(value).strip().lower()
	if v in ("eksik analiz",):
		return REPORT_STATUS_MISSING_ANALYSIS
	return None
