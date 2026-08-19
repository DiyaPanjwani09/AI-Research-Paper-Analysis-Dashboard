import fitz  # PyMuPDF
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class PageContent:
    page_number: int
    text: str


@dataclass
class PaperSection:
    name: str
    content: str
    page_start: int = 0
    page_end: int = 0
    order_index: int = 0


@dataclass
class PaperMetadata:
    title: str = ""
    authors: List[str] = field(default_factory=list)
    abstract: str = ""
    keywords: List[str] = field(default_factory=list)
    year: Optional[int] = None
    venue: str = ""
    doi: Optional[str] = None
    sections: Dict[str, str] = field(default_factory=dict)
    section_list: List[PaperSection] = field(default_factory=list)
    full_text: str = ""
    page_count: int = 0
    word_count: int = 0
    references: List[str] = field(default_factory=list)
    pages: List[PageContent] = field(default_factory=list)


SECTION_PATTERNS = [
    re.compile(r'^\s*(\d+\.?\s*)?(abstract)\s*$', re.IGNORECASE | re.MULTILINE),
    re.compile(r'^\s*(\d+\.?\s*)?(introduction)\s*$', re.IGNORECASE | re.MULTILINE),
    re.compile(r'^\s*(\d+\.?\s*)?(related\s+work|background)\s*$', re.IGNORECASE | re.MULTILINE),
    re.compile(r'^\s*(\d+\.?\s*)?(methodology|methods?|approach|proposed\s+method)\s*$', re.IGNORECASE | re.MULTILINE),
    re.compile(r'^\s*(\d+\.?\s*)?(experiment(?:s|al)?(?:\s+(?:setup|design|evaluation))?|evaluation)\s*$', re.IGNORECASE | re.MULTILINE),
    re.compile(r'^\s*(\d+\.?\s*)?(results?|findings?)\s*$', re.IGNORECASE | re.MULTILINE),
    re.compile(r'^\s*(\d+\.?\s*)?(discussion)\s*$', re.IGNORECASE | re.MULTILINE),
    re.compile(r'^\s*(\d+\.?\s*)?(conclusions?)\s*$', re.IGNORECASE | re.MULTILINE),
    re.compile(r'^\s*(\d+\.?\s*)?(future\s+work)\s*$', re.IGNORECASE | re.MULTILINE),
    re.compile(r'^\s*(\d+\.?\s*)?(references?|bibliography)\s*$', re.IGNORECASE | re.MULTILINE),
]

SECTION_ALIASES = {
    "methods": "methodology",
    "method": "methodology",
    "approach": "methodology",
    "proposed method": "methodology",
    "experiments": "experiments",
    "experimental": "experiments",
    "experiment setup": "experiments",
    "experiment design": "experiments",
    "experiment evaluation": "experiments",
    "evaluation": "experiments",
    "result": "results",
    "findings": "results",
    "conclusion": "conclusion",
    "future work": "future_work",
    "references": "references",
    "bibliography": "references",
    "related work": "related_work",
    "background": "related_work",
}


def normalize_section_name(name: str) -> str:
    name = name.strip().lower()
    return SECTION_ALIASES.get(name, name)


class PDFParser:
    def __init__(self):
        self.section_header_re = re.compile(
            r'^\s*(?:\d+\.?\s*)?('
            r'abstract|introduction|related\s+work|background|'
            r'methodology|methods?|approach|proposed\s+method|'
            r'experiment(?:s|al)?(?:\s+(?:setup|design|evaluation))?|evaluation|'
            r'results?|findings?|discussion|conclusions?|future\s+work|'
            r'references?|bibliography'
            r')\s*$',
            re.IGNORECASE | re.MULTILINE
        )

    def parse_pdf(self, file_path: str) -> PaperMetadata:
        doc = fitz.open(file_path)
        pages = []
        full_text = ""

        for i, page in enumerate(doc):
            text = page.get_text()
            pages.append(PageContent(page_number=i + 1, text=text))
            full_text += text + "\n"

        page_count = len(doc)
        doc.close()

        first_page_text = pages[0].text if pages else ""

        title = self._extract_title(first_page_text)
        authors = self._extract_authors(first_page_text)
        abstract = self._extract_abstract(full_text)
        keywords = self._extract_keywords(full_text)
        year = self._extract_year(full_text)
        venue = self._extract_venue(full_text)
        doi = self._extract_doi(full_text)
        sections, section_list = self._extract_sections(full_text, pages)
        references = self._extract_references(full_text)

        return PaperMetadata(
            title=title,
            authors=authors,
            abstract=abstract,
            keywords=keywords,
            year=year,
            venue=venue,
            doi=doi,
            sections=sections,
            section_list=section_list,
            full_text=full_text.strip(),
            page_count=page_count,
            word_count=len(full_text.split()),
            references=references,
            pages=pages,
        )

    def _extract_title(self, first_page: str) -> str:
        lines = first_page.strip().split('\n')
        for line in lines[:10]:
            line = line.strip()
            if len(line) > 10 and not line.isdigit() and 'abstract' not in line.lower():
                return line
        return ""

    def _extract_authors(self, first_page: str) -> List[str]:
        lines = first_page.strip().split('\n')
        authors = []
        capture = False
        for i, line in enumerate(lines):
            line = line.strip()
            if 'abstract' in line.lower():
                break
            if i == 0 or not capture:
                if any(c.isalpha() for c in line) and len(line) > 3 and not line.isdigit():
                    if capture or (1 < i < 6):
                        parts = re.split(r',|\band\b', line)
                        for part in parts:
                            part = part.strip()
                            if part and len(part) > 2 and not part.isdigit():
                                authors.append(part)
                        capture = True
        return authors

    def _extract_abstract(self, text: str) -> str:
        patterns = [
            re.compile(r'(?i)\babstract\b[\s\n:–\-]*\n?(.*?)(?=\n\s*\n|\n\s*(?:introduction|keywords?\b|1\.?\s))', re.DOTALL),
            re.compile(r'(?i)\babstract\b[\s\n:–\-]*(.{100,1500}?)(?=\n\s*\n)', re.DOTALL),
        ]
        for pattern in patterns:
            match = pattern.search(text)
            if match:
                abstract = match.group(1).strip()
                abstract = re.sub(r'\s+', ' ', abstract)
                if len(abstract) > 50:
                    return abstract
        return ""

    def _extract_keywords(self, text: str) -> List[str]:
        match = re.search(r'(?i)\bkeywords?\b[\s\n:–\-]*([^\n]+)', text)
        if match:
            kw_text = match.group(1)
            kws = re.split(r'[,;]', kw_text)
            return [kw.strip() for kw in kws if kw.strip() and len(kw.strip()) > 1]
        return []

    def _extract_year(self, text: str) -> Optional[int]:
        match = re.search(r'(?:©|copyright|published|submitted|accepted)\s*(?:in\s+)?(\d{4})', text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        years = re.findall(r'\b(20[0-2]\d)\b', text)
        if years:
            from collections import Counter
            most_common = Counter(years).most_common(1)
            if most_common:
                return int(most_common[0][0])
        return None

    def _extract_venue(self, text: str) -> str:
        patterns = [
            re.compile(r'(?i)(?:proceedings|journal|conference|workshop)\s+of\s+(?:the\s+)?(.+?)(?:\s+20\d{2}|\s*$)', re.MULTILINE),
            re.compile(r'(?i)(?:presented|published)\s+(?:at|in)\s+(?:the\s+)?(.+?)(?:\s+20\d{2}|\s*$)', re.MULTILINE),
        ]
        for pattern in patterns:
            match = pattern.search(text)
            if match:
                venue = match.group(1).strip()
                if len(venue) > 5:
                    return venue[:200]
        return ""

    def _extract_doi(self, text: str) -> Optional[str]:
        match = re.search(r'(?i)(?:doi|DOI)[:\s]*(10\.\d{4,}/[^\s,;]+)', text)
        if match:
            return match.group(1).strip()
        return None

    def _is_section_header(self, line: str) -> Optional[str]:
        line = line.strip()
        if len(line) > 100:
            return None
        match = self.section_header_re.match(line)
        if match:
            return normalize_section_name(match.group(1))
        return None

    def _extract_sections(self, text: str, pages: List[PageContent]) -> Tuple[Dict[str, str], List[PaperSection]]:
        sections = {}
        section_list = []
        lines = text.split('\n')

        current_section = "front_matter"
        section_content = []
        section_page = 1
        section_idx = 0

        for line in lines:
            stripped = line.strip()
            section_name = self._is_section_header(stripped) if stripped else None

            if section_name and section_name != current_section:
                if section_content and current_section != "front_matter":
                    content = ' '.join(section_content)
                    sections[current_section] = content
                    section_list.append(PaperSection(
                        name=current_section,
                        content=content,
                        page_start=section_page,
                        order_index=section_idx,
                    ))
                    section_idx += 1

                current_section = section_name
                section_content = []
                section_page = 1
            elif stripped:
                section_content.append(stripped)

        if section_content and current_section != "front_matter":
            content = ' '.join(section_content)
            sections[current_section] = content
            section_list.append(PaperSection(
                name=current_section,
                content=content,
                page_start=section_page,
                order_index=section_idx,
            ))

        return sections, section_list

    def _extract_references(self, text: str) -> List[str]:
        ref_match = re.search(r'(?i)\n\s*(?:references?|bibliography)\s*\n', text)
        if not ref_match:
            return []
        ref_text = text[ref_match.end():]
        ref_lines = ref_text.strip().split('\n')
        references = []
        current_ref = ""
        for line in ref_lines:
            line = line.strip()
            if not line:
                if current_ref:
                    references.append(current_ref.strip())
                    current_ref = ""
                continue
            if re.match(r'^\[?\d+\]?\s', line) or re.match(r'^[A-Z][a-z]+,', line):
                if current_ref:
                    references.append(current_ref.strip())
                current_ref = line
            else:
                current_ref += " " + line
        if current_ref:
            references.append(current_ref.strip())
        return references[:200]
