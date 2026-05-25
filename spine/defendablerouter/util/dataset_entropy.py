#!/usr/bin/env python3
"""
dataset-entropy — Measure training data diversity before you ship.

Zero dependencies. One file. Instant report.

Measures 4 dimensions of dataset health:
    1. Vocabulary entropy     (Shannon entropy of word distribution, normalized 0-1)
    2. Structural diversity   (unique sentence structure fingerprints)
    3. Bigram diversity       (unique word pairs / total word pairs)
    4. Opening diversity      (unique first-N-token patterns — catches template rot)

The most important metric: top-10 structure concentration.
    - < 15%  = healthy (diverse outputs)
    - 15-30% = warning (some template patterns emerging)
    - > 30%  = critical (model will learn to parrot structures)

Supports:
    - OpenAI chat format  {"messages": [{"role": "user", ...}, {"role": "assistant", ...}]}
    - Alpaca format       {"instruction": "...", "output": "..."}
    - Simple Q/A format   {"question": "...", "answer": "..."}
    - Raw text format     {"text": "..."}

Usage:
    python3 dataset_entropy.py train.jsonl
    python3 dataset_entropy.py train.jsonl --top-repeats 20
    python3 dataset_entropy.py train.jsonl --json
    python3 dataset_entropy.py train.jsonl --compare other.jsonl

Built by Swarm & Bee (https://swarmandbee.ai)
"""

import json
import math
import re
from collections import Counter
from pathlib import Path


__version__ = "1.0.0"


# ═══════════════════════════════════════════════════════════════════════
# Text extraction — supports multiple JSONL formats
# ═══════════════════════════════════════════════════════════════════════

def _extract_text(record: dict) -> tuple[str, str]:
    """
    Extract (input, output) text from a training record.
    Supports: OpenAI chat, Alpaca, Q/A, raw text formats.
    """
    # OpenAI chat format: {"messages": [...]}
    messages = record.get("messages", [])
    if messages:
        question = ""
        answer = ""
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "user":
                question = content
            elif role == "assistant":
                answer = content
        if answer:
            return question, answer

    # Alpaca format: {"instruction": "...", "input": "...", "output": "..."}
    if "instruction" in record and "output" in record:
        inp = record.get("instruction", "")
        if record.get("input"):
            inp = inp + " " + record["input"]
        return inp, record["output"]

    # Simple Q/A: {"question": "...", "answer": "..."}
    if "question" in record and "answer" in record:
        return record["question"], record["answer"]

    # Prompt/completion: {"prompt": "...", "completion": "..."}
    if "prompt" in record and "completion" in record:
        return record["prompt"], record["completion"]

    # Raw text: {"text": "..."}
    if "text" in record:
        return "", record["text"]

    return "", ""


def _tokenize(text: str) -> list[str]:
    """Simple whitespace + punctuation tokenizer. No dependencies."""
    return re.findall(r"[a-zA-Z0-9]+(?:'[a-zA-Z]+)?", text.lower())


# ═══════════════════════════════════════════════════════════════════════
# Structural fingerprinting
# ═══════════════════════════════════════════════════════════════════════

_NUM_PAT = re.compile(r'^[\d,$%.]+$')
_STOP = frozenset([
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
    'should', 'may', 'might', 'shall', 'can', 'to', 'of', 'in', 'for',
    'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through', 'during',
    'before', 'after', 'above', 'below', 'between', 'and', 'but', 'or',
    'not', 'no', 'if', 'then', 'than', 'that', 'this', 'it', 'its',
    'they', 'their', 'them', 'we', 'our', 'you', 'your', 'he', 'she',
])


def _tag(word: str) -> str:
    """Cheap POS-like tag for structural fingerprinting."""
    if _NUM_PAT.match(word):
        return 'NUM'
    if word in _STOP:
        return 'STOP'
    if len(word) <= 2:
        return 'SHORT'
    return 'WORD'


def _structural_fingerprint(text: str) -> str:
    """
    Sentence structure fingerprint.
    Split into sentences, take first 3, tag each word, join.
    Two outputs with the same structure fingerprint are structurally identical
    even if the words are different.
    """
    sentences = re.split(r'[.!?]\s+', text[:500])[:3]
    parts = []
    for sent in sentences:
        tokens = _tokenize(sent)[:12]
        tags = [_tag(t) for t in tokens]
        parts.append('-'.join(tags))
    return ' | '.join(parts)


def _opening_fingerprint(text: str, n: int = 10) -> str:
    """First n tokens, lowercased. Catches repetitive openings."""
    tokens = _tokenize(text)[:n]
    return ' '.join(tokens)


# ═══════════════════════════════════════════════════════════════════════
# Entropy calculation
# ═══════════════════════════════════════════════════════════════════════

def _shannon_entropy(counter: Counter) -> float:
    """Shannon entropy, normalized to [0, 1]. 1.0 = perfectly uniform distribution."""
    total = sum(counter.values())
    if total == 0:
        return 0.0
    n_unique = len(counter)
    if n_unique <= 1:
        return 0.0
    max_entropy = math.log2(n_unique)
    if max_entropy == 0:
        return 0.0
    entropy = -sum(
        (count / total) * math.log2(count / total)
        for count in counter.values()
        if count > 0
    )
    return entropy / max_entropy


# ═══════════════════════════════════════════════════════════════════════
# Main report
# ═══════════════════════════════════════════════════════════════════════

def entropy_report(input_path: str, top_repeats: int = 10) -> dict:
    """
    Run full entropy analysis on a JSONL dataset.

    Args:
        input_path: Path to JSONL file
        top_repeats: Number of top repeated patterns to return

    Returns:
        Dict with all metrics, health indicators, and top patterns.
    """
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    word_counter = Counter()
    bigram_counter = Counter()
    structure_counter = Counter()
    opening_counter_q = Counter()
    opening_counter_a = Counter()

    total_pairs = 0
    total_words_q = 0
    total_words_a = 0
    total_bigrams = 0
    parse_errors = 0

    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                parse_errors += 1
                continue

            question, answer = _extract_text(record)
            if not answer:
                continue

            total_pairs += 1

            # Tokenize
            q_tokens = _tokenize(question)
            a_tokens = _tokenize(answer)
            all_tokens = q_tokens + a_tokens

            total_words_q += len(q_tokens)
            total_words_a += len(a_tokens)

            # Word frequency
            word_counter.update(all_tokens)

            # Bigrams (answer only — that's what the model learns to generate)
            for i in range(len(a_tokens) - 1):
                bg = (a_tokens[i], a_tokens[i + 1])
                bigram_counter[bg] += 1
                total_bigrams += 1

            # Structural fingerprint (answer)
            fp = _structural_fingerprint(answer)
            structure_counter[fp] += 1

            # Opening patterns
            if question:
                opening_counter_q[_opening_fingerprint(question)] += 1
            opening_counter_a[_opening_fingerprint(answer)] += 1

    # Compute metrics
    vocab_entropy = _shannon_entropy(word_counter)
    bigram_entropy = _shannon_entropy(bigram_counter)
    structure_entropy = _shannon_entropy(structure_counter)

    unique_structures = len(structure_counter)
    unique_vocab = len(word_counter)
    unique_bigrams = len(bigram_counter)
    unique_openings_q = len(opening_counter_q)
    unique_openings_a = len(opening_counter_a)

    # Bigram diversity ratio
    bigram_diversity = unique_bigrams / total_bigrams if total_bigrams > 0 else 0

    # Top repeated patterns
    top_q_openings = opening_counter_q.most_common(top_repeats)
    top_a_openings = opening_counter_a.most_common(top_repeats)
    top_structures = structure_counter.most_common(top_repeats)

    # Repetition concentration: what % of pairs use the top 10 structures?
    top10_structure_count = sum(c for _, c in structure_counter.most_common(10))
    structure_concentration = top10_structure_count / total_pairs if total_pairs > 0 else 0

    # Health grades
    def _grade_entropy(val, healthy, warning):
        if val >= healthy:
            return "HEALTHY"
        elif val >= warning:
            return "WARNING"
        return "CRITICAL"

    def _grade_concentration(val):
        if val <= 0.15:
            return "HEALTHY"
        elif val <= 0.30:
            return "WARNING"
        return "CRITICAL"

    # ── Combined health score (0-100) ──
    # Weighted: vocab 25%, structure 25%, concentration 30%, bigram 20%
    # Concentration is inverted (lower = better)
    conc_score = max(0, 1.0 - (structure_concentration / 0.60))  # 0% = 1.0, 60% = 0.0
    health_score = round(
        vocab_entropy * 25
        + structure_entropy * 25
        + conc_score * 30
        + bigram_entropy * 20
    )
    health_score = max(0, min(100, health_score))

    if health_score >= 80:
        health_grade = "EXCELLENT"
    elif health_score >= 60:
        health_grade = "HEALTHY"
    elif health_score >= 40:
        health_grade = "WEAK"
    else:
        health_grade = "CRITICAL"

    return {
        "file": str(path),
        "pairs": total_pairs,
        "parse_errors": parse_errors,
        "health_score": health_score,
        "health_grade": health_grade,
        "total_words": total_words_q + total_words_a,
        "total_words_input": total_words_q,
        "total_words_output": total_words_a,
        "avg_input_len": round(total_words_q / total_pairs, 1) if total_pairs > 0 else 0,
        "avg_output_len": round(total_words_a / total_pairs, 1) if total_pairs > 0 else 0,
        "unique_vocab": unique_vocab,
        "vocab_entropy": round(vocab_entropy, 4),
        "vocab_health": _grade_entropy(vocab_entropy, 0.80, 0.65),
        "unique_bigrams": unique_bigrams,
        "bigram_entropy": round(bigram_entropy, 4),
        "bigram_diversity": round(bigram_diversity, 4),
        "unique_structures": unique_structures,
        "structure_entropy": round(structure_entropy, 4),
        "structure_health": _grade_entropy(structure_entropy, 0.75, 0.55),
        "structure_concentration_top10": round(structure_concentration, 4),
        "concentration_health": _grade_concentration(structure_concentration),
        "unique_openings_input": unique_openings_q,
        "unique_openings_output": unique_openings_a,
        "top_input_openings": top_q_openings,
        "top_output_openings": top_a_openings,
        "top_structures": top_structures,
    }


# ═══════════════════════════════════════════════════════════════════════
# Pretty printing
# ═══════════════════════════════════════════════════════════════════════

_HEALTH_COLORS = {
    "EXCELLENT": "\033[92m", # green
    "HEALTHY": "\033[92m",   # green
    "WARNING": "\033[93m",   # yellow
    "WEAK": "\033[93m",      # yellow
    "CRITICAL": "\033[91m",  # red
}
_RESET = "\033[0m"


def _health_str(grade: str, use_color: bool = True) -> str:
    if use_color and grade in _HEALTH_COLORS:
        return f"{_HEALTH_COLORS[grade]}{grade}{_RESET}"
    return grade


def print_report(report: dict, use_color: bool = True) -> None:
    """Pretty-print entropy report to stdout."""
    print()
    print("=" * 64)
    print("  DATASET ENTROPY REPORT")
    print("=" * 64)
    hs = report['health_score']
    hg = report['health_grade']
    print(f"  health score: {hs}/100  {_health_str(hg, use_color)}")
    print(f"  file:  {report['file']}")
    print(f"  pairs: {report['pairs']:,}")
    if report['parse_errors']:
        print(f"  parse errors: {report['parse_errors']:,}")
    print()
    print("  DIVERSITY METRICS")
    print("  " + "-" * 44)
    print(f"  vocabulary entropy:        {report['vocab_entropy']:.4f}   {_health_str(report['vocab_health'], use_color)}")
    print(f"  bigram entropy:            {report['bigram_entropy']:.4f}")
    print(f"  structure entropy:          {report['structure_entropy']:.4f}   {_health_str(report['structure_health'], use_color)}")
    print(f"  bigram diversity ratio:     {report['bigram_diversity']:.4f}")
    print()
    print(f"  unique vocab:               {report['unique_vocab']:,}")
    print(f"  unique bigrams:             {report['unique_bigrams']:,}")
    print(f"  unique sentence structures: {report['unique_structures']:,}")
    print(f"  unique input openings:      {report['unique_openings_input']:,}")
    print(f"  unique output openings:     {report['unique_openings_output']:,}")
    print()
    sc = report['structure_concentration_top10']
    print(f"  top-10 structure concentration: {sc:.1%}   {_health_str(report['concentration_health'], use_color)}")
    print(f"  avg input length:          {report['avg_input_len']:.0f} words")
    print(f"  avg output length:         {report['avg_output_len']:.0f} words")
    print()

    # Thresholds reference
    print("  THRESHOLDS")
    print("  " + "-" * 44)
    print("  vocab entropy:     >= 0.80 healthy  |  < 0.65 critical")
    print("  structure entropy: >= 0.75 healthy  |  < 0.55 critical")
    print("  concentration:     <= 15%  healthy  |  > 30%  critical")
    print()

    print("  TOP REPEATED OUTPUT OPENINGS")
    print("  " + "-" * 44)
    for opening, count in report['top_output_openings'][:10]:
        pct = count / report['pairs'] * 100 if report['pairs'] > 0 else 0
        bar = "#" * min(int(pct), 40)
        print(f"  {count:6,} ({pct:5.1f}%) {bar} {opening[:48]}")

    print()
    print("=" * 64)
    print()


def print_comparison(reports: list[dict], use_color: bool = True) -> None:
    """Print side-by-side comparison of multiple datasets."""
    print()
    print("=" * 80)
    print("  DATASET ENTROPY COMPARISON")
    print("=" * 80)
    print()

    # Header
    names = [Path(r['file']).name for r in reports]
    header = f"  {'Metric':<30}"
    for name in names:
        header += f" {name[:18]:>18}"
    print(header)
    print("  " + "-" * (30 + 19 * len(reports)))

    # Rows
    metrics = [
        ("HEALTH SCORE", "health_score", "{}/100"),
        ("pairs", "pairs", "{:,}"),
        ("vocab entropy", "vocab_entropy", "{:.4f}"),
        ("bigram entropy", "bigram_entropy", "{:.4f}"),
        ("structure entropy", "structure_entropy", "{:.4f}"),
        ("bigram diversity", "bigram_diversity", "{:.4f}"),
        ("unique structures", "unique_structures", "{:,}"),
        ("unique vocab", "unique_vocab", "{:,}"),
        ("top-10 concentration", "structure_concentration_top10", "{:.1%}"),
        ("avg output len (words)", "avg_output_len", "{:.0f}"),
    ]

    for label, key, fmt in metrics:
        row = f"  {label:<30}"
        for r in reports:
            val = r.get(key, 0)
            row += f" {fmt.format(val):>18}"
        print(row)

    # Health row
    print()
    health_row = f"  {'overall health':<30}"
    for r in reports:
        grades = [r.get('vocab_health', ''), r.get('structure_health', ''), r.get('concentration_health', '')]
        if all(g == 'HEALTHY' for g in grades):
            health_row += f" {_health_str('HEALTHY', use_color):>18}"
        elif any(g == 'CRITICAL' for g in grades):
            health_row += f" {_health_str('CRITICAL', use_color):>18}"
        else:
            health_row += f" {_health_str('WARNING', use_color):>18}"
    print(health_row)

    print()
    print("=" * 80)
    print()


# ═══════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Measure training dataset diversity. Zero dependencies.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  python3 dataset_entropy.py train.jsonl
  python3 dataset_entropy.py train.jsonl --json
  python3 dataset_entropy.py train.jsonl --compare val.jsonl other.jsonl
  python3 dataset_entropy.py train.jsonl --top-repeats 20 --no-color
        """,
    )
    parser.add_argument("input", help="Path to JSONL training file")
    parser.add_argument("--compare", nargs="+", metavar="FILE",
                        help="Compare against additional JSONL files")
    parser.add_argument("--top-repeats", type=int, default=10,
                        help="Number of top repeated patterns to show (default: 10)")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON (for piping)")
    parser.add_argument("--no-color", action="store_true",
                        help="Disable ANSI color codes")
    args = parser.parse_args()

    use_color = not args.no_color

    report = entropy_report(args.input, top_repeats=args.top_repeats)

    if args.json:
        # Convert tuples for JSON serialization
        for key in ("top_input_openings", "top_output_openings", "top_structures"):
            report[key] = [{"pattern": p, "count": c} for p, c in report[key]]
        print(json.dumps(report, indent=2))
        return

    if args.compare:
        reports = [report]
        for path in args.compare:
            reports.append(entropy_report(path, top_repeats=args.top_repeats))
        print_comparison(reports, use_color=use_color)
        # Also print individual reports
        for r in reports:
            print_report(r, use_color=use_color)
    else:
        print_report(report, use_color=use_color)


if __name__ == "__main__":
    main()
