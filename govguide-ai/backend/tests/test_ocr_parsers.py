"""
Unit tests for the OCR field extractor parsers.

Tests regex-based extraction for each document type:
Aadhaar, income certificate, community certificate,
marksheet, ration card, bank passbook.
"""

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ocr.processor import (
    extract_aadhaar_fields,
    extract_income_certificate_fields,
    extract_community_certificate_fields,
    extract_marksheet_fields,
    extract_ration_card_fields,
    extract_bank_passbook_fields,
    validate_document,
)


# ── Sample OCR texts ──────────────────────────────────────────────────────────

AADHAAR_TEXT = """
Government of India
Unique Identification Authority of India
Name: RAVI KUMAR SHARMA
Date of Birth: 12/08/1990
Male
1234 5678 9012
Address: 45, Gandhi Nagar, Chennai, Tamil Nadu 600001
"""

INCOME_CERT_TEXT = """
Government of Tamil Nadu
Revenue Department
Certificate of Income

This is to certify that Thiru MURUGAN SURESH
residing at 12, Main Street, Coimbatore
has an annual income of Rs.1,50,000 (Rupees One Lakh Fifty Thousand Only)
from all sources combined.

Certificate No: TN/COI/2024/001234
Issued on: 15/01/2024
Tahsildar, Coimbatore North
"""

COMMUNITY_CERT_TEXT = """
Government of Tamil Nadu
Revenue Department
Community Certificate

This is to certify that LAKSHMI DEVI
daughter of RAJAMANI
belongs to the Scheduled Caste community (Pallar)
which is included in the Central/State List of Scheduled Castes.

Certificate No: CC/2024/56789
Date: 20/02/2024
"""

MARKSHEET_TEXT = """
Tamil Nadu Board of Secondary Education
Certificate of Secondary Education

Name of Candidate: PRIYA ANNAMALAI
Roll No: TN2024089765
Year of Passing: 2024
Class X

English: 95 | Tamil: 88 | Mathematics: 92 | Science: 87 | Social: 91
Total: 453/500
Percentage: 90.6%

Result: Pass
"""

RATION_CARD_TEXT = """
Government of Tamil Nadu
Civil Supplies and Consumer Protection Department

Ration Card No: TN/CBE/2019/456789
Head of Family: ARUMUGAM PILLAI
Card Type: BPL
Total Members: 4
Address: 78, Anna Nagar, Coimbatore 641001
"""

BANK_PASSBOOK_TEXT = """
State Bank of India
Branch: Chennai Anna Nagar
IFSC: SBIN0001234

Account Holder: SENTHIL KUMAR R
Account Number: 123456789012
Account Type: Savings

Balance as on 01/11/2024: Rs.12,456.00
"""


# ── Aadhaar Tests ────────────────────────────────────────────────────────────

class TestAadhaarExtraction:
    def test_detects_aadhaar_number(self):
        fields = extract_aadhaar_fields(AADHAAR_TEXT)
        assert fields.get("aadhaar_detected") is True

    def test_masks_aadhaar_number(self):
        fields = extract_aadhaar_fields(AADHAAR_TEXT)
        aadhaar = fields.get("aadhaar_number", "")
        assert "XXXX" in aadhaar
        # Only last 4 digits should be visible
        assert "9012" in aadhaar

    def test_extracts_name(self):
        fields = extract_aadhaar_fields(AADHAAR_TEXT)
        assert fields.get("name") is not None
        assert "RAVI" in fields["name"].upper() or "KUMAR" in fields["name"].upper()

    def test_extracts_dob(self):
        fields = extract_aadhaar_fields(AADHAAR_TEXT)
        assert fields.get("dob") == "12/08/1990"

    def test_extracts_gender(self):
        fields = extract_aadhaar_fields(AADHAAR_TEXT)
        assert fields.get("gender") == "male"

    def test_female_gender(self):
        text = AADHAAR_TEXT.replace("Male", "Female")
        fields = extract_aadhaar_fields(text)
        assert fields.get("gender") == "female"

    def test_no_false_aadhaar_on_empty(self):
        fields = extract_aadhaar_fields("")
        assert not fields.get("aadhaar_detected", False)


# ── Income Certificate Tests ──────────────────────────────────────────────────

class TestIncomeCertificateExtraction:
    def test_extracts_income(self):
        fields = extract_income_certificate_fields(INCOME_CERT_TEXT)
        assert fields.get("annual_income") == 150000

    def test_extracts_name(self):
        fields = extract_income_certificate_fields(INCOME_CERT_TEXT)
        assert fields.get("name") is not None

    def test_extracts_certificate_number(self):
        fields = extract_income_certificate_fields(INCOME_CERT_TEXT)
        assert fields.get("certificate_number") is not None

    def test_extracts_issue_date(self):
        fields = extract_income_certificate_fields(INCOME_CERT_TEXT)
        assert fields.get("issue_date") == "15/01/2024"

    def test_extracts_issuing_authority(self):
        fields = extract_income_certificate_fields(INCOME_CERT_TEXT)
        assert fields.get("issuing_authority") is not None
        assert "tahsildar" in fields["issuing_authority"].lower()

    def test_empty_text_returns_empty(self):
        fields = extract_income_certificate_fields("")
        assert fields == {}


# ── Community Certificate Tests ──────────────────────────────────────────────

class TestCommunityCertificateExtraction:
    def test_extracts_sc_community(self):
        fields = extract_community_certificate_fields(COMMUNITY_CERT_TEXT)
        assert fields.get("community") is not None
        assert "Scheduled Caste" in fields["community"] or "SC" in fields["community"]

    def test_extracts_name(self):
        fields = extract_community_certificate_fields(COMMUNITY_CERT_TEXT)
        assert fields.get("name") is not None

    def test_extracts_certificate_number(self):
        fields = extract_community_certificate_fields(COMMUNITY_CERT_TEXT)
        assert fields.get("certificate_number") is not None

    def test_obc_extraction(self):
        obc_text = COMMUNITY_CERT_TEXT.replace(
            "Scheduled Caste community (Pallar)",
            "Other Backward Class community"
        )
        fields = extract_community_certificate_fields(obc_text)
        assert "OBC" in fields.get("community", "") or "Other Backward Class" in fields.get("community", "")


# ── Marksheet Tests ──────────────────────────────────────────────────────────

class TestMarksheetExtraction:
    def test_extracts_name(self):
        fields = extract_marksheet_fields(MARKSHEET_TEXT)
        assert fields.get("name") is not None
        assert "PRIYA" in fields["name"].upper()

    def test_extracts_roll_number(self):
        fields = extract_marksheet_fields(MARKSHEET_TEXT)
        assert fields.get("roll_number") is not None

    def test_extracts_percentage(self):
        fields = extract_marksheet_fields(MARKSHEET_TEXT)
        assert fields.get("percentage") is not None
        assert abs(fields["percentage"] - 90.6) < 0.1

    def test_extracts_year(self):
        fields = extract_marksheet_fields(MARKSHEET_TEXT)
        assert fields.get("year_of_passing") == 2024


# ── Ration Card Tests ────────────────────────────────────────────────────────

class TestRationCardExtraction:
    def test_extracts_ration_card_number(self):
        fields = extract_ration_card_fields(RATION_CARD_TEXT)
        assert fields.get("ration_card_number") is not None

    def test_extracts_card_type(self):
        fields = extract_ration_card_fields(RATION_CARD_TEXT)
        assert fields.get("card_type") == "BPL"

    def test_extracts_members(self):
        fields = extract_ration_card_fields(RATION_CARD_TEXT)
        assert fields.get("members") == 4

    def test_extracts_head_name(self):
        fields = extract_ration_card_fields(RATION_CARD_TEXT)
        assert fields.get("head_of_family") is not None


# ── Bank Passbook Tests ──────────────────────────────────────────────────────

class TestBankPassbookExtraction:
    def test_extracts_account_number(self):
        fields = extract_bank_passbook_fields(BANK_PASSBOOK_TEXT)
        assert fields.get("account_number") is not None
        # Should be masked
        assert "XXXX" in fields["account_number"]

    def test_extracts_ifsc(self):
        fields = extract_bank_passbook_fields(BANK_PASSBOOK_TEXT)
        assert fields.get("ifsc_code") == "SBIN0001234"

    def test_extracts_bank_name(self):
        fields = extract_bank_passbook_fields(BANK_PASSBOOK_TEXT)
        assert fields.get("bank_name") is not None
        assert "State Bank" in fields["bank_name"]

    def test_extracts_account_holder(self):
        fields = extract_bank_passbook_fields(BANK_PASSBOOK_TEXT)
        assert fields.get("account_holder") is not None


# ── Validation Tests ─────────────────────────────────────────────────────────

class TestDocumentValidation:
    def test_valid_aadhaar(self):
        fields = extract_aadhaar_fields(AADHAAR_TEXT)
        status, errors, fixes, confidence = validate_document("aadhaar", fields)
        assert status in ("Valid", "Warning")
        assert confidence > 0.5

    def test_invalid_empty_aadhaar(self):
        status, errors, fixes, confidence = validate_document("aadhaar", {})
        assert status == "Invalid"
        assert "missing_aadhaar_detected" in errors

    def test_valid_income_cert(self):
        fields = extract_income_certificate_fields(INCOME_CERT_TEXT)
        status, errors, fixes, confidence = validate_document("income_certificate", fields)
        assert status in ("Valid", "Warning")

    def test_income_mismatch_warning(self):
        fields = extract_income_certificate_fields(INCOME_CERT_TEXT)
        profile = {"annual_income": 500000, "full_name": "Test User"}
        status, errors, fixes, confidence = validate_document("income_certificate", fields, profile)
        # Should produce a warning due to income mismatch
        assert status in ("Warning", "Invalid")

    def test_community_cert_valid(self):
        fields = extract_community_certificate_fields(COMMUNITY_CERT_TEXT)
        status, errors, fixes, confidence = validate_document("community_certificate", fields)
        assert status in ("Valid", "Warning")
        assert confidence > 0.0

    def test_validation_has_suggested_fixes_on_error(self):
        status, errors, fixes, confidence = validate_document("aadhaar", {})
        assert status == "Invalid"
        # Should provide suggested fixes for each error
        assert len(fixes) > 0
