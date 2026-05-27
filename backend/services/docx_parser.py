import re
from docx import Document


# Common section header patterns
SECTION_PATTERNS = {
    "summary": re.compile(
        r"(professional\s+)?summary|profile|objective|about\s+me|career\s+overview",
        re.IGNORECASE,
    ),
    "skills": re.compile(
        r"skills|technical\s+skills|core\s+competencies|technologies|tools\s*(&|and)\s*technologies|tech\s+stack",
        re.IGNORECASE,
    ),
    "experience": re.compile(
        r"experience|work\s+history|employment|projects|professional\s+experience|work\s+experience",
        re.IGNORECASE,
    ),
    "education": re.compile(
        r"education|academic|qualifications|certifications|degrees",
        re.IGNORECASE,
    ),
}

BULLET_CHARS = ("•", "-", "●", "○", "▪", "*", "►", "→", "»", "■", "·")
DATE_RE = re.compile(
    r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|january|february|march|april|may|june|july|august|september|october|november|december|"
    r"20\d{2}|19\d{2})"
    r"\s*[-–—/to\s]+"
    r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|january|february|march|april|may|june|july|august|september|october|november|december|"
    r"20\d{2}|19\d{2}|present|current|till\s+date|ongoing)",
    re.IGNORECASE,
)


def _is_heading(paragraph) -> bool:
    """Check if a paragraph is a heading by style or formatting."""
    style_name = (paragraph.style.name or "").lower()
    if "heading" in style_name or "title" in style_name:
        return True
    # Check if entire paragraph is bold and short
    if paragraph.runs and len(paragraph.text.strip()) < 60:
        non_empty_runs = [r for r in paragraph.runs if r.text.strip()]
        if non_empty_runs and all(r.bold for r in non_empty_runs):
            return True
    return False


def _detect_section(text: str) -> str | None:
    """Detect which section a heading belongs to."""
    clean = text.strip().rstrip(":").strip()
    if not clean or len(clean) > 80:
        return None
    for section, pattern in SECTION_PATTERNS.items():
        if pattern.search(clean):
            return section
    return None


def _is_bullet(text: str) -> bool:
    """Check if text starts with a bullet character."""
    stripped = text.strip()
    return stripped.startswith(BULLET_CHARS)


def _clean_bullet(text: str) -> str:
    """Remove bullet prefix from text."""
    stripped = text.strip()
    for char in BULLET_CHARS:
        if stripped.startswith(char):
            return stripped[len(char):].strip()
    return stripped


def _has_date(text: str) -> bool:
    """Check if text contains a date range (company/role header indicator)."""
    return bool(DATE_RE.search(text))


def _extract_text_from_tables(doc: Document) -> list[str]:
    """Extract all text from tables in the document."""
    lines = []
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    text = para.text.strip()
                    if text:
                        lines.append(text)
    return lines


def _parse_experience_block(lines: list[str]) -> list[dict]:
    """Parse experience lines into structured client entries."""
    clients = []
    current_client = None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        is_bullet = _is_bullet(stripped)
        has_date = _has_date(stripped)

        # Lines with dates that aren't bullets = new client/role header
        if has_date and not is_bullet:
            if current_client:
                clients.append(current_client)
            # Extract date from the line
            date_match = DATE_RE.search(stripped)
            current_client = {
                "client": stripped,
                "role": "",
                "duration": date_match.group(0) if date_match else "",
                "points": [],
            }
        elif is_bullet:
            clean_point = _clean_bullet(stripped)
            if clean_point:
                if current_client:
                    current_client["points"].append(clean_point)
                else:
                    # Bullet before any client header — create a generic one
                    current_client = {"client": "General", "role": "", "duration": "", "points": [clean_point]}
        elif current_client and not current_client["points"]:
            # Non-bullet, non-date line right after client header = role/title
            if current_client["role"]:
                current_client["role"] += " | " + stripped
            else:
                current_client["role"] = stripped
        elif current_client:
            # Non-bullet text under a client with points — treat as a point
            current_client["points"].append(stripped)
        else:
            # First non-date, non-bullet line — likely a company name without date
            current_client = {"client": stripped, "role": "", "duration": "", "points": []}

    if current_client:
        clients.append(current_client)

    return clients


def parse_resume(file_path: str) -> dict:
    """Parse a DOCX resume into structured sections."""
    doc = Document(file_path)

    sections: dict[str, list[str]] = {
        "summary": [],
        "skills": [],
        "experience": [],
        "education": [],
    }
    current_section = None

    # --- Parse paragraphs ---
    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if not text:
            continue

        # Check if this paragraph is a section header
        is_header = False
        if _is_heading(paragraph):
            detected = _detect_section(text)
            if detected:
                current_section = detected
                is_header = True

        # Also check short ALL-CAPS or colon-ending lines as headers
        if not is_header and len(text) < 60:
            clean = text.rstrip(":")
            if clean.isupper() or (clean.endswith(":") and len(clean) < 40):
                detected = _detect_section(clean)
                if detected:
                    current_section = detected
                    is_header = True

        if not is_header and current_section:
            sections[current_section].append(text)

    # --- Also extract text from tables (many resumes use tables for layout) ---
    table_lines = _extract_text_from_tables(doc)
    if table_lines:
        table_section = None
        for line in table_lines:
            detected = _detect_section(line)
            if detected:
                table_section = detected
                continue
            if table_section and line not in sections[table_section]:
                sections[table_section].append(line)

    # --- Structure the output ---
    result = {
        "summary": "\n".join(sections["summary"]),
        "skills": [],
        "experience": [],
        "education": "\n".join(sections["education"]),
    }

    # Parse skills: split by commas, pipes, bullets, semicolons, newlines
    skills_text = " ".join(sections["skills"])
    if skills_text:
        result["skills"] = [
            s.strip()
            for s in re.split(r"[,|•●○▪;/\n]", skills_text)
            if s.strip() and len(s.strip()) < 60
        ]

    # Parse experience into client blocks
    result["experience"] = _parse_experience_block(sections["experience"])

    # If parser found nothing useful, store raw text as fallback
    if not result["experience"] and not result["skills"] and not result["summary"]:
        all_text = "\n".join(p.text.strip() for p in doc.paragraphs if p.text.strip())
        all_text += "\n" + "\n".join(table_lines)
        result["raw_text"] = all_text.strip()

    return result
