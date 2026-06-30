import re

def clean_content(text: str) -> str:
    toc_line = re.compile(
        r'^\s*[\*\+\-]\s+\[.+?\]\(#[^)]+\)\s*$'
    )

    lines = text.splitlines(keepends=True)
    result_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]

        if toc_line.match(line):
            block_start = i
            j = i
            while j < len(lines) and (
                toc_line.match(lines[j]) or lines[j].strip() == ''
            ):
                if lines[j].strip() == '':
                    k = j + 1
                    while k < len(lines) and lines[k].strip() == '':
                        k += 1
                    if k >= len(lines) or not toc_line.match(lines[k]):
                        break
                j += 1

            block_lines = lines[block_start:j]
            toc_items = [l for l in block_lines if toc_line.match(l)]
            if len(toc_items) >= 2:
                i = j
                while i < len(lines) and lines[i].strip() == '':
                    i += 1
                continue

        result_lines.append(line)
        i += 1

    text = ''.join(result_lines)

    text = re.sub(
        r'^[ \t]*[\*\+\-][ \t]+.*?optisigns\.com/pricing.*?\n',
        '',
        text,
        flags=re.MULTILINE | re.IGNORECASE
    )

    def remove_blockquote_if_pricing(m):
        if 'optisigns.com/pricing' in m.group(0).lower():
            return ''
        return m.group(0)

    text = re.sub(
        r'(?:^>[ \t]?.*\n)+',
        remove_blockquote_if_pricing,
        text,
        flags=re.MULTILINE
    )

    def remove_table_note_if_pricing(m):
        if 'optisigns.com/pricing' in m.group(0).lower():
            return ''
        return m.group(0)

    text = re.sub(
        r'(\|.*?\|\n)+',
        remove_table_note_if_pricing,
        text,
        flags=re.MULTILINE
    )

    FREE_TRIAL_URL = re.compile(
        r'\[([^\]]+)\]'
        r'\(https?://(?:app\.optisigns\.com(?:/signUp)?|www\.optisigns\.com/free-trial)[^)]*\)'
        r'[^\n]*',
        re.IGNORECASE
    )
    text = FREE_TRIAL_URL.sub('', text)

    text = re.sub(
        r'^([ \t]*[\*\+\-][ \t]+)[\s—–-]*\n',
        '',
        text,
        flags=re.MULTILINE
    )

    ADS_SECTION_HEADING = re.compile(
        r'^##\s+(Pricing|Licensing|Sign\s+Up|Free\s+Trial|Get\s+started)\b',
        re.IGNORECASE | re.MULTILINE
    )

    def remove_ads_section(text):
        while True:
            m = ADS_SECTION_HEADING.search(text)
            if not m:
                break
            start = m.start()

            before = text[:start]
            sep_match = re.search(r'\n---[ \t]*\n\s*$', before)
            if sep_match:
                start = before.rfind('\n---') + 1

            after = text[m.end():]
            end_match = re.search(r'\n(?:---|##)', after)
            if end_match:
                end = m.end() + end_match.start() + 1
            else:
                end = len(text)

            text = text[:start] + text[end:]
        return text

    text = remove_ads_section(text)

    CROSSSELL_DOMAINS = re.compile(
        r'[^\n]*(?:shop\.optisigns\.com|amzn\.to)[^\n]*\n?',
        re.IGNORECASE
    )
    text = CROSSSELL_DOMAINS.sub('', text)

    text = re.sub(
        r'OptiSigns is the leader in digital signage software\.?[^\n]*\n?',
        '',
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r'^[ \t]*\[.*?\]\(https?://www\.optisigns\.com/?\)[ \t]*\n',
        '',
        text,
        flags=re.MULTILINE | re.IGNORECASE
    )

    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip() + '\n'
