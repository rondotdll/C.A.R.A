import re
from flexmatch.cmap import GARBAGE_CHAR_MAP

def substr_match(target: str, values: list[str]) -> str:
    results = []
    for v in values:
        if target in v:
            results.append(v)
    return results

# normalizes ASCII strings
def normalize(input: str, prioritize_numerical=False) -> str:
    return "".join([
        GARBAGE_CHAR_MAP[c] if c in GARBAGE_CHAR_MAP # substitute out garbage characters using our map
        else c for c in (
            re.sub(r"[\u0300-\u036f]", "", input) # remove the "glitch text" effect
        )
    ])