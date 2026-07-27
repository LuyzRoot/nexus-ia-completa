from typing import List

# Default metrics to compute for generation
DEFAULT_GENERATION_METRICS: List[str] = ["rouge", "bleu", "sacrebleu", "bertscore"]

# Retriever evaluation defaults
DEFAULT_RETRIEVER_KS = [1, 3, 5, 10]

# Plotting defaults
PLOT_DPI = 120