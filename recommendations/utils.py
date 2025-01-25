from rapidfuzz import process, fuzz

def extract_list_from_query(query: str, song_list: list[str]) -> tuple[str, int]:
    best_match, score, index = process.extractOne(query, song_list, scorer=fuzz.ratio, return_indices=True)
    return best_match, index
