import os
import json
import re
from typing import Dict, List, Set, Tuple
from app.services.text_preprocessor import TextPreprocessor
from app.core.exceptions import SkillExtractionError

class SkillExtractor:
    def __init__(self, skills_json_path: str = None):
        if not skills_json_path:
            # Resolve default path relative to this file
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            skills_json_path = os.path.join(base_dir, "data", "skills.json")
            
        self.skills_json_path = skills_json_path
        self.categories: Dict[str, List[str]] = {}
        self.aliases: Dict[str, str] = {}
        self.canonical_skills: Set[str] = set()
        self.skill_to_category: Dict[str, str] = {}
        self._load_skills_dictionary()
        self._build_regex_patterns()

    def _load_skills_dictionary(self):
        try:
            with open(self.skills_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.categories = data.get("categories", {})
                self.aliases = data.get("aliases", {})
        except Exception as e:
            raise SkillExtractionError(f"Failed to load skills dictionary from {self.skills_json_path}: {str(e)}")

        # Map each canonical skill to its category
        for category, skills in self.categories.items():
            for skill in skills:
                skill_lower = skill.lower()
                self.canonical_skills.add(skill_lower)
                self.skill_to_category[skill_lower] = category

    def _build_regex_patterns(self):
        """
        Builds compiled regex patterns for all canonical skills and aliases.
        Uses advanced boundaries to support special characters like C++, C#, .NET.
        """
        self.patterns: List[Tuple[str, re.Pattern, str]] = []  # List of (term, pattern, canonical_name)
        
        # 1. Add canonical skills
        for skill in self.canonical_skills:
            pattern = self._create_token_pattern(skill)
            self.patterns.append((skill, pattern, skill))
            
        # 2. Add aliases
        for alias, canonical in self.aliases.items():
            # If alias is already in pattern (e.g. alias equals canonical), skip to avoid duplication
            if alias == canonical:
                continue
            pattern = self._create_token_pattern(alias)
            self.patterns.append((alias, pattern, canonical))

    def _create_token_pattern(self, term: str) -> re.Pattern:
        """
        Creates a regular expression pattern for a term, supporting special chars.
        Assumes the search text is padded with spaces at the start and end.
        """
        escaped_term = re.escape(term)
        
        # Lookbehind for a space or common punctuation
        # Lookahead for a space or common punctuation
        pattern_str = r'(?<=[\s,.;:("])' + escaped_term + r'(?=[\s,.;:)"!])'
        return re.compile(pattern_str, re.IGNORECASE)

    def extract_skills(self, text: str) -> Dict[str, any]:
        """
        Extracts skills from text, resolves aliases, avoids duplicates, and categorizes them.
        """
        if not text:
            return {"skills": [], "categories": {}}

        normalized_text = TextPreprocessor.normalize_for_matching(text)
        # Pad text with spaces to make boundary matching work for start/end of string
        padded_text = f" {normalized_text} "
        detected_skills: Set[str] = set()

        for term, pattern, canonical in self.patterns:
            if pattern.search(padded_text):
                detected_skills.add(canonical)

        # Categorize detected skills
        categorized: Dict[str, List[str]] = {cat: [] for cat in self.categories.keys()}
        categorized["other"] = categorized.get("other", [])  # Ensure "other" exists

        for skill in detected_skills:
            category = self.skill_to_category.get(skill, "other")
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(skill)

        # Sort the results for consistency
        sorted_skills = sorted(list(detected_skills))
        for cat in categorized:
            categorized[cat] = sorted(categorized[cat])

        return {
            "skills": sorted_skills,
            "categories": categorized
        }
