"""
OCR Document Processor for GovGuide AI.

Pipeline:
1. Preprocess image (grayscale → denoise → threshold → deskew)
2. OCR with pytesseract
3. Extract fields via regex + NLP
4. Validate extracted data
5. Mask sensitive data (Aadhaar digits)

Supports: JPG, PNG, PDF
Document types: aadhaar, income_certificate, community_certificate,
                marksheet, ration_card, bank_passbook
"""

import io
import logging
import re
import unicodedata
from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Lazy imports for optional heavy dependencies
try:
    import cv2
    import numpy as np
    _cv2_available = True
except ImportError:
    _cv2_available = False
    logger.warning("OpenCV not available. Image preprocessing will be skipped.")

try:
    import pytesseract
    from PIL import Image
    _tesseract_available = True
except ImportError:
    _tesseract_available = False
    logger.warning("pytesseract/Pillow not available. OCR will return dummy data.")

try:
    from pdf2image import convert_from_bytes
    _pdf2image_available = True
except ImportError:
    _pdf2image_available = False
    logger.warning("pdf2image not available. PDF processing will be limited.")

try:
    from fuzzywuzzy import fuzz
    _fuzz_available = True
except ImportError:
    _fuzz_available = False


# ── Image Preprocessing ──────────────────────────────────────────────────────

def _deskew(image: "np.ndarray") -> "np.ndarray":
    """Correct image skew using Hough lines."""
    try:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=10)
        if lines is None:
            return image
        angles = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if x2 != x1:
                angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
                if abs(angle) < 45:
                    angles.append(angle)
        if not angles:
            return image
        median_angle = np.median(angles)
        if abs(median_angle) < 1:
            return image
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
        return cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    except Exception:
        return image


def preprocess_image(image_bytes: bytes) -> Optional["Image.Image"]:
    """
    Full preprocessing pipeline for OCR quality improvement:
    grayscale → CLAHE → Gaussian blur → adaptive threshold → deskew
    """
    if not _cv2_available or not _tesseract_available:
        # Return raw PIL image
        try:
            return Image.open(io.BytesIO(image_bytes))
        except Exception:
            return None

    try:
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is None:
            return None

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply CLAHE for contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)

        # Denoise
        gray = cv2.fastNlMeansDenoising(gray, h=10)

        # Adaptive thresholding
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2
        )

        # Deskew
        deskewed = _deskew(binary)

        # Convert back to PIL
        pil_image = Image.fromarray(deskewed)
        return pil_image
    except Exception as e:
        logger.error(f"Image preprocessing failed: {e}")
        return None


# ── OCR Extraction ───────────────────────────────────────────────────────────

def run_ocr(pil_image: "Image.Image") -> str:
    """Run Tesseract OCR on a preprocessed PIL image."""
    if not _tesseract_available:
        return "[OCR not available - please install pytesseract and Tesseract]"
    try:
        # Configure Tesseract for Indian documents (English + Tamil/Devanagari)
        custom_config = r"--oem 3 --psm 6 -l eng"
        text = pytesseract.image_to_string(pil_image, config=custom_config)
        return text.strip()
    except Exception as e:
        logger.error(f"OCR failed: {e}")
        return ""


def pdf_to_images(pdf_bytes: bytes) -> List["Image.Image"]:
    """Convert PDF bytes to list of PIL images."""
    if not _pdf2image_available:
        logger.warning("pdf2image not available")
        return []
    try:
        return convert_from_bytes(pdf_bytes, dpi=300)
    except Exception as e:
        logger.error(f"PDF conversion failed: {e}")
        return []


# ── Field Extraction ─────────────────────────────────────────────────────────

def _clean_text(text: str) -> str:
    """Normalize unicode and remove extra whitespace."""
    text = unicodedata.normalize("NFKC", text)
    return re.sub(r"\s+", " ", text).strip()


def extract_aadhaar_fields(text: str) -> Dict[str, Any]:
    """Extract fields from Aadhaar card text."""
    fields: Dict[str, Any] = {}

    # Aadhaar number (12 digits, may have spaces)
    aadhaar_match = re.search(r"\b(\d{4}[\s-]?\d{4}[\s-]?\d{4})\b", text)
    if aadhaar_match:
        raw = re.sub(r"[\s-]", "", aadhaar_match.group(1))
        # MASK: show only last 4 digits (XXXX XXXX 1234)
        fields["aadhaar_number"] = f"XXXX XXXX {raw[-4:]}"
        fields["aadhaar_detected"] = True

    # Name (look for "Name:" or capitalized words after DOB)
    name_match = re.search(r"(?:Name|नाम|பெயர்)[:\s]+([A-Z][a-zA-Z\s]{2,40})", text)
    if name_match:
        fields["name"] = _clean_text(name_match.group(1))

    # DOB
    dob_match = re.search(r"(?:DOB|Date of Birth|जन्म तिथि)[:\s]+(\d{2}[/-]\d{2}[/-]\d{4})", text)
    if dob_match:
        fields["dob"] = dob_match.group(1)

    # Gender
    if re.search(r"\b(Male|MALE|पुरुष)\b", text):
        fields["gender"] = "male"
    elif re.search(r"\b(Female|FEMALE|महिला|பெண்)\b", text):
        fields["gender"] = "female"

    # Address
    addr_match = re.search(r"(?:Address|पता|முகவரி)[:\s]+(.{10,200}?)(?:\n\n|\Z)", text, re.DOTALL)
    if addr_match:
        fields["address"] = _clean_text(addr_match.group(1))[:200]

    return fields


def extract_income_certificate_fields(text: str) -> Dict[str, Any]:
    """Extract fields from income certificate."""
    fields: Dict[str, Any] = {}

    # Income amount
    income_match = re.search(
        r"(?:annual income|income|वार्षिक आय|ஆண்டு வருமானம்)(?:\s+of)?[:\s]*(?:Rs\.?|₹|INR)?\s*([\d,]+)",
        text, re.IGNORECASE
    )
    if income_match:
        income_str = re.sub(r",", "", income_match.group(1))
        try:
            fields["annual_income"] = int(income_str)
        except ValueError:
            pass

    # Certificate number
    cert_match = re.search(r"(?:Certificate No|Cert\.?\s*No)[\.:\s]+([A-Z0-9/-]{5,20})", text, re.IGNORECASE)
    if cert_match:
        fields["certificate_number"] = cert_match.group(1)

    # Name
    name_match = re.search(r"(?:This is to certify that|certified that)\s+(?:Thiru|Tmt\.?|Mr\.?|Mrs\.?|Ms\.?)?\s*([A-Z][a-zA-Z\s]{2,40})", text, re.IGNORECASE)
    if name_match:
        fields["name"] = _clean_text(name_match.group(1))

    # Issue date
    date_match = re.search(r"(?:issued on|date)[:\s]+(\d{2}[/-]\d{2}[/-]\d{4})", text, re.IGNORECASE)
    if date_match:
        fields["issue_date"] = date_match.group(1)

    # Issuing authority
    auth_match = re.search(r"(?:Tahsildar|Revenue Divisional Officer|District Collector|Block Development Officer)", text, re.IGNORECASE)
    if auth_match:
        fields["issuing_authority"] = auth_match.group(0)

    return fields


def extract_community_certificate_fields(text: str) -> Dict[str, Any]:
    """Extract fields from community/caste certificate."""
    fields: Dict[str, Any] = {}

    # Community/Caste
    for community in ["Scheduled Caste", "SC", "Scheduled Tribe", "ST",
                       "Other Backward Class", "OBC", "Backward Class", "BC",
                       "Most Backward Class", "MBC"]:
        if re.search(rf"\b{re.escape(community)}\b", text, re.IGNORECASE):
            fields["community"] = community
            break

    # Name
    name_match = re.search(
        r"(?:This is to certify that|Name)[:\s]+(?:Thiru|Tmt\.?|Mr\.?|Mrs\.?|Ms\.?)?\s*([A-Z][a-zA-Z\s]{2,40})",
        text, re.IGNORECASE
    )
    if name_match:
        fields["name"] = _clean_text(name_match.group(1))

    # Certificate number
    cert_match = re.search(r"(?:Certificate No|Cert\.?\s*No)[\.:\s]+([A-Z0-9/-]{5,20})", text, re.IGNORECASE)
    if cert_match:
        fields["certificate_number"] = cert_match.group(1)

    # Issue date
    date_match = re.search(r"(\d{2}[/-]\d{2}[/-]\d{4})", text)
    if date_match:
        fields["issue_date"] = date_match.group(1)

    return fields


def extract_marksheet_fields(text: str) -> Dict[str, Any]:
    """Extract fields from educational marksheet."""
    fields: Dict[str, Any] = {}

    # Roll number
    roll_match = re.search(r"(?:Roll No|Registration No|Exam No)[\.:\s]+([A-Z0-9]{5,15})", text, re.IGNORECASE)
    if roll_match:
        fields["roll_number"] = roll_match.group(1)

    # Name
    name_match = re.search(r"(?:Name of Candidate|Student Name|Name)[:\s]+([A-Z][a-zA-Z\s]{2,50})", text, re.IGNORECASE)
    if name_match:
        fields["name"] = _clean_text(name_match.group(1))

    # Percentage
    pct_match = re.search(r"(?:Percentage|Total Marks)[:\s]+(\d{2,3}\.?\d*)\s*%?", text, re.IGNORECASE)
    if pct_match:
        try:
            fields["percentage"] = float(pct_match.group(1))
        except ValueError:
            pass

    # Year of passing
    year_match = re.search(r"(?:Year of Passing|Passed in)[:\s]+(\d{4})", text, re.IGNORECASE)
    if year_match:
        fields["year_of_passing"] = int(year_match.group(1))

    # Class/Grade
    class_match = re.search(r"(?:Class|Standard|Grade)\s+(?:X|XII|10|12|8|9)", text, re.IGNORECASE)
    if class_match:
        fields["class"] = class_match.group(0)

    return fields


def extract_ration_card_fields(text: str) -> Dict[str, Any]:
    """Extract fields from ration card."""
    fields: Dict[str, Any] = {}

    # Ration card number
    rc_match = re.search(r"(?:Ration Card No|Card No)[\.:\s]+([A-Z0-9/-]+)", text, re.IGNORECASE) or re.search(r"\b([A-Z]{2,3}[\s/-]?\d{6,12})\b", text)
    if rc_match:
        fields["ration_card_number"] = rc_match.group(1).strip()

    # Family head name
    name_match = re.search(r"(?:Head of Family|Name)[:\s]+([A-Z][a-zA-Z\s]{2,40})", text, re.IGNORECASE)
    if name_match:
        fields["head_of_family"] = _clean_text(name_match.group(1))

    # Card type (APL/BPL/AAY)
    for card_type in ["AAY", "BPL", "APL", "PHH", "NPHH"]:
        if card_type in text.upper():
            fields["card_type"] = card_type
            break

    # Member count
    members_match = re.search(r"(?:Members|Total Members)[:\s]+(\d+)", text, re.IGNORECASE)
    if members_match:
        fields["members"] = int(members_match.group(1))

    return fields


def extract_bank_passbook_fields(text: str) -> Dict[str, Any]:
    """Extract fields from bank passbook."""
    fields: Dict[str, Any] = {}

    # Account number (mask middle digits)
    acc_match = re.search(r"\b(\d{9,18})\b", text)
    if acc_match:
        raw = acc_match.group(1)
        fields["account_number"] = f"XXXX{raw[-4:]}"

    # Account holder name
    name_match = re.search(r"(?:Account Holder|Name|A/C Name)[:\s]+([A-Z][a-zA-Z\s]{2,40})", text, re.IGNORECASE)
    if name_match:
        fields["account_holder"] = _clean_text(name_match.group(1))

    # IFSC code
    ifsc_match = re.search(r"\b([A-Z]{4}0[A-Z0-9]{6})\b", text)
    if ifsc_match:
        fields["ifsc_code"] = ifsc_match.group(1)

    # Bank name
    bank_patterns = ["State Bank", "Bank of Baroda", "Punjab National", "Canara Bank",
                     "Union Bank", "Indian Bank", "UCO Bank", "Bank of India",
                     "HDFC Bank", "ICICI Bank", "Axis Bank", "Indian Overseas"]
    for bank in bank_patterns:
        if re.search(bank, text, re.IGNORECASE):
            fields["bank_name"] = bank
            break

    return fields


# ── Field Extractor Dispatcher ───────────────────────────────────────────────

EXTRACTORS = {
    "aadhaar": extract_aadhaar_fields,
    "income_certificate": extract_income_certificate_fields,
    "community_certificate": extract_community_certificate_fields,
    "marksheet": extract_marksheet_fields,
    "ration_card": extract_ration_card_fields,
    "bank_passbook": extract_bank_passbook_fields,
}


def extract_fields(text: str, doc_type: str) -> Dict[str, Any]:
    """Route to the appropriate field extractor based on document type."""
    extractor = EXTRACTORS.get(doc_type)
    if extractor is None:
        logger.warning(f"No extractor for doc_type: {doc_type}")
        return {}
    return extractor(text)


# ── Validation ───────────────────────────────────────────────────────────────

def validate_document(
    doc_type: str,
    fields: Dict[str, Any],
    user_profile: Optional[Dict] = None,
) -> Tuple[str, Dict[str, Any], Dict[str, Any], float]:
    """
    Validate extracted fields against rules and user profile.

    Returns: (status, errors_dict, suggested_fixes_dict, confidence_score)
    Status: "Valid" | "Warning" | "Invalid"
    """
    errors: Dict[str, Any] = {}
    fixes: Dict[str, Any] = {}
    warnings: List[str] = []

    # Check mandatory fields per doc type
    mandatory: Dict[str, List[str]] = {
        "aadhaar": ["name", "aadhaar_detected"],
        "income_certificate": ["name", "annual_income"],
        "community_certificate": ["name", "community"],
        "marksheet": ["name"],
        "ration_card": ["ration_card_number"],
        "bank_passbook": ["account_number"],
    }

    for field in mandatory.get(doc_type, []):
        if field not in fields or fields[field] is None:
            errors[f"missing_{field}"] = f"Could not extract '{field}' from document"
            fixes[f"missing_{field}"] = f"Ensure '{field}' is clearly visible and re-upload"

    # Check expiry for income/community certificates
    if doc_type in ("income_certificate", "community_certificate"):
        issue_date_str = fields.get("issue_date")
        if issue_date_str:
            try:
                # Try parsing common date formats
                for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
                    try:
                        issue_date = datetime.strptime(issue_date_str, fmt).date()
                        age_months = (date.today() - issue_date).days / 30
                        if age_months > 12:
                            warnings.append(f"Certificate is more than 12 months old ({int(age_months)} months)")
                            fixes["expiry"] = "Obtain a fresh certificate issued within the last 12 months"
                        break
                    except ValueError:
                        continue
            except Exception:
                pass

    # Cross-validate income with user profile
    if doc_type == "income_certificate" and user_profile:
        doc_income = fields.get("annual_income")
        profile_income = user_profile.get("annual_income")
        if doc_income and profile_income:
            if abs(doc_income - profile_income) / max(profile_income, 1) > 0.2:
                warnings.append(
                    f"Income in certificate (₹{doc_income:,}) differs significantly "
                    f"from your profile (₹{profile_income:,})"
                )
                fixes["income_mismatch"] = "Update your profile income or use the correct income certificate"

    # Name fuzzy match against profile
    if user_profile and "name" in fields:
        profile_name = user_profile.get("full_name", "")
        doc_name = fields.get("name", "")
        if profile_name and doc_name:
            if _fuzz_available:
                score = fuzz.token_sort_ratio(profile_name.lower(), doc_name.lower())
                if score < 70:
                    warnings.append(
                        f"Name in document ('{doc_name}') may not match profile ('{profile_name}'). "
                        f"Similarity: {score}%"
                    )
                    fixes["name_mismatch"] = "Ensure document name matches your registered name, or provide explanation"
            else:
                # Simple check
                if profile_name.lower().split()[0] not in doc_name.lower():
                    warnings.append(f"Name in document may not match profile name")

    # Compute confidence score
    expected_fields = len(mandatory.get(doc_type, ["name"]))
    found_fields = len([k for k in mandatory.get(doc_type, ["name"]) if k in fields])
    confidence = round(found_fields / max(expected_fields, 1) * 0.8 + (0.2 if not errors else 0.0), 2)

    # Determine status
    if errors:
        status = "Invalid"
    elif warnings:
        status = "Warning"
        errors["warnings"] = warnings
    else:
        status = "Valid"

    return status, errors, fixes, confidence


# ── Main Processing Function ─────────────────────────────────────────────────

async def process_document(
    file_bytes: bytes,
    filename: str,
    doc_type: str,
    user_profile: Optional[Dict] = None,
) -> Dict[str, Any]:
    """
    Full OCR pipeline: preprocess → OCR → extract → validate.

    Returns a result dict compatible with the Document ORM model.
    """
    # Determine file type
    mime_type = "image/jpeg"
    lower_name = filename.lower()
    if lower_name.endswith(".pdf"):
        mime_type = "application/pdf"
    elif lower_name.endswith(".png"):
        mime_type = "image/png"

    raw_text = ""

    # Extract text
    if mime_type == "application/pdf":
        images = pdf_to_images(file_bytes)
        if images:
            for img in images[:2]:  # Process first 2 pages max
                raw_text += run_ocr(img) + "\n"
        else:
            raw_text = "[PDF processing failed - ensure poppler is installed]"
    else:
        pil_img = preprocess_image(file_bytes)
        if pil_img:
            raw_text = run_ocr(pil_img)
        else:
            raw_text = "[Image processing failed]"

    # Extract structured fields
    fields = extract_fields(raw_text, doc_type)

    # Validate
    status, errors, fixes, confidence = validate_document(doc_type, fields, user_profile)

    return {
        "mime_type": mime_type,
        "extracted_fields": fields,
        "raw_text_excerpt": raw_text[:500],  # Privacy: store only excerpt
        "status": status,
        "validation_errors": errors,
        "suggested_fixes": fixes,
        "confidence_score": confidence,
        "issue_date": fields.get("issue_date"),
        "expiry_date": fields.get("expiry_date"),
    }
