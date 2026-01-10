# backend/app/services/target_match.py
import re
from difflib import get_close_matches

def normalize(text: str) -> str:
    # Keep it simple: lowercase and strip whitespace
    return text.lower().strip()

def suggest_target_columns(user_input: str, columns: list[str], cutoff: float = 0.4):
    """
    Returns a list of suggested column names based on fuzzy matching.
    Lowered cutoff to 0.4 to catch more misspellings.
    """
    if not user_input:
        return []

    # Map normalized names back to original column names
    normalized_map = {normalize(col): col for col in columns}

    # Get close matches from the normalized keys
    matches = get_close_matches(
        normalize(user_input), 
        list(normalized_map.keys()), 
        n=3, 
        cutoff=cutoff
    )

    # Return original column names for the matches found
    return [normalized_map[m] for m in matches]