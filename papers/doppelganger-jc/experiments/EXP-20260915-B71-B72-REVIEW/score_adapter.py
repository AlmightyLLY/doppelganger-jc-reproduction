"""Same legacy JSON adapter as B63. Does not modify prompts or raw outputs."""
from scoring_b62 import score as frozen_score

def score_record(text, reference):
    return frozen_score(text, dict(reference, arm='J_UA', format_arm='JSON'))
