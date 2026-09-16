import re

class TextPreprocessor:
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Cleans raw extracted text by:
        1. Replacing smart quotes, dashes, and other non-standard characters.
        2. Merging hyphenated words split across lines (PDF artifacts).
        3. Collapsing multiple spaces and tabs into a single space.
        4. Cleaning empty or near-empty lines while preserving paragraph spacing.
        """
        if not text:
            return ""

        # Normalize smart quotes and dashes
        text = text.replace("“", "\"").replace("”", "\"").replace("‘", "'").replace("’", "'")
        text = text.replace("–", "-").replace("—", "-")

        # Merge hyphenated words at line breaks (e.g., "deve-\nloper" -> "developer")
        text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)

        # Replace multiple spaces/tabs with a single space
        text = re.sub(r'[ \t]+', ' ', text)

        # Normalize line endings and remove empty lines
        lines = [line.strip() for line in text.splitlines()]
        non_empty_lines = [line for line in lines if line]
        text = "\n".join(non_empty_lines)

        return text

    @staticmethod
    def normalize_for_matching(text: str) -> str:
        """
        Normalizes text specifically for skill matching:
        1. Runs standard clean_text.
        2. Lowercases.
        3. Standardizes common compound technical terms/variations (e.g., spring-boot -> spring boot).
        4. Retains special characters like C++, C#, .NET, Node.js.
        """
        cleaned = TextPreprocessor.clean_text(text).replace("\n", " ")
        lowered = cleaned.lower()

        # Replace common variations to canonical forms
        # We use boundary or regex matching to avoid partial replacements (e.g., "ts" matching inside "its")
        replacements = {
            r'\bspring[- ]boot\b': 'spring boot',
            r'\bspringboot\b': 'spring boot',
            r'\bpostgresql\b': 'postgresql',
            r'\bpostgres\b': 'postgresql',
            r'\brestful[- ]api\b': 'rest api',
            r'\brest[- ]api\b': 'rest api',
            r'\brestful\b': 'rest api',
            r'\bnode[- ]js\b': 'nodejs',
            r'\bnode\.js\b': 'nodejs',
            r'\breact[- ]js\b': 'react',
            r'\breact\.js\b': 'react',
            r'\bvue[- ]js\b': 'vue',
            r'\bvue\.js\b': 'vue',
        }

        normalized = lowered
        for pattern, replacement in replacements.items():
            normalized = re.sub(pattern, replacement, normalized)

        return normalized
