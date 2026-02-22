#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures as cf
import logging
import os
import re
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from deep_translator import GoogleTranslator

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SRC_FILES = [ROOT / "index.qmd", *sorted((ROOT / "vol-1").glob("*.md"))]
PROTECTED_RE = re.compile(r"(`[^`]*`|\$[^$]*\$)")

GLOSSARY: dict[str, dict[str, str]] = {
    "zh-CN": {
        r"\bAlgorithm(s)?\b": "算法",
        r"\bPermutation(s)?\b": "置换",
        r"\bBinomial coefficient(s)?\b": "二项式系数",
        r"\bHarmonic numbers\b": "调和数",
        r"\bFibonacci numbers\b": "斐波那契数",
        r"\bGenerating functions\b": "生成函数",
        r"\bSubroutine(s)?\b": "子程序",
        r"\bCoroutine(s)?\b": "协程",
    }
}


@dataclass
class RateLimiter:
    interval_s: float
    _lock: threading.Lock = threading.Lock()
    _next_ts: float = 0.0

    def wait(self) -> None:
        with self._lock:
            now = time.monotonic()
            if now < self._next_ts:
                time.sleep(self._next_ts - now)
                now = time.monotonic()
            self._next_ts = now + self.interval_s


def setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-5s | %(message)s",
        datefmt="%H:%M:%S",
    )
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Translate book markdown/qmd files into target language")
    p.add_argument("--source-lang", default="en", help="Source language code (default: en)")
    p.add_argument("--target-lang", default="zh-CN", help="Target language code (e.g., zh-CN, ja, fr)")
    p.add_argument("--output-dir", default="", help="Output language dir (default derived from target, e.g. zh)")
    p.add_argument("--files", default=os.environ.get("TRANSLATE_FILES", ""), help="Comma-separated relative files to translate")
    p.add_argument("--chunk-size", type=int, default=2200, help="Chunk size for translation requests")
    p.add_argument("--max-workers", type=int, default=4, help="Parallel workers for chunks")
    p.add_argument("--rate-limit", type=float, default=5.0, help="Max requests per second across all workers")
    p.add_argument("--verbose", action="store_true", help="Enable debug logs")
    return p.parse_args()


def resolve_files(files_arg: str) -> list[Path]:
    if files_arg.strip():
        files = [ROOT / x.strip() for x in files_arg.split(",") if x.strip()]
    else:
        files = DEFAULT_SRC_FILES
    return files


def chunk_text(s: str, n: int) -> list[str]:
    out: list[str] = []
    i = 0
    while i < len(s):
        j = min(len(s), i + n)
        if j < len(s):
            k = s.rfind("\n", i, j)
            if k > i + 120:
                j = k + 1
        out.append(s[i:j])
        i = j
    return out


def apply_glossary(text: str, target_lang: str) -> str:
    mapping = GLOSSARY.get(target_lang, {})
    out = text
    for pattern, replacement in mapping.items():
        out = re.sub(pattern, replacement, out, flags=re.IGNORECASE)
    return out


def translate_chunk(
    idx: int,
    chunk: str,
    translator: GoogleTranslator,
    limiter: RateLimiter,
    target_lang: str,
) -> tuple[int, str]:
    if not chunk.strip() or re.fullmatch(r"[\s\d#>*\-`~:;,.!\[\](){}+=_/\\|]+", chunk):
        return idx, chunk
    limiter.wait()
    try:
        translated = translator.translate(chunk) or chunk
        translated = apply_glossary(translated, target_lang)
        return idx, translated
    except Exception as exc:
        logging.warning("chunk %s failed: %s", idx, exc)
        return idx, chunk


def translate_segment_parallel(
    segment: str,
    translator: GoogleTranslator,
    limiter: RateLimiter,
    target_lang: str,
    chunk_size: int,
    max_workers: int,
) -> str:
    chunks = chunk_text(segment, chunk_size)
    if len(chunks) == 1:
        return translate_chunk(0, chunks[0], translator, limiter, target_lang)[1]

    logging.debug("Translating segment with %d chunks", len(chunks))
    results: list[str] = [""] * len(chunks)
    with cf.ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = [
            ex.submit(translate_chunk, i, c, translator, limiter, target_lang)
            for i, c in enumerate(chunks)
        ]
        for f in cf.as_completed(futures):
            i, translated = f.result()
            results[i] = translated
    return "".join(results)


def translate_line(
    line: str,
    translator: GoogleTranslator,
    limiter: RateLimiter,
    target_lang: str,
    chunk_size: int,
    max_workers: int,
) -> str:
    parts = PROTECTED_RE.split(line)
    out: list[str] = []
    for p in parts:
        if not p:
            continue
        if (p.startswith("`") and p.endswith("`")) or (p.startswith("$") and p.endswith("$")):
            out.append(p)
        else:
            out.append(
                translate_segment_parallel(
                    p, translator, limiter, target_lang, chunk_size, max_workers
                )
            )
    return "".join(out)


def translate_file(
    src: Path,
    dst: Path,
    translator: GoogleTranslator,
    limiter: RateLimiter,
    target_lang: str,
    chunk_size: int,
    max_workers: int,
) -> None:
    t0 = time.time()
    lines = src.read_text(encoding="utf-8").splitlines(True)
    out: list[str] = []
    in_code = False
    in_math = False

    for idx, line in enumerate(lines, start=1):
        s = line.strip()
        if s.startswith("```"):
            in_code = not in_code
            out.append(line)
            continue
        if s == "$$":
            in_math = not in_math
            out.append(line)
            continue
        if in_code or in_math:
            out.append(line)
            continue

        out.append(
            translate_line(line, translator, limiter, target_lang, chunk_size, max_workers)
        )
        if idx % 200 == 0:
            logging.info("%s: %d/%d lines", src.relative_to(ROOT), idx, len(lines))

    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text("".join(out), encoding="utf-8")
    logging.info(
        "DONE %s -> %s (%.2fs, %d lines)",
        src.relative_to(ROOT),
        dst.relative_to(ROOT),
        time.time() - t0,
        len(lines),
    )


def main() -> None:
    args = parse_args()
    setup_logging(args.verbose)

    output_dir = args.output_dir.strip() or args.target_lang.split("-")[0].lower()
    dst_root = ROOT / output_dir

    files = resolve_files(args.files)
    logging.info(
        "Starting translation: %d files | %s -> %s | workers=%d | rate=%.2f req/s",
        len(files),
        args.source_lang,
        args.target_lang,
        args.max_workers,
        args.rate_limit,
    )

    translator = GoogleTranslator(source=args.source_lang, target=args.target_lang)
    limiter = RateLimiter(interval_s=1.0 / max(args.rate_limit, 0.2))

    total_start = time.time()
    for i, src in enumerate(files, start=1):
        rel = src.relative_to(ROOT)
        dst = dst_root / rel
        logging.info("[%d/%d] Translating %s", i, len(files), rel)
        translate_file(src, dst, translator, limiter, args.target_lang, args.chunk_size, args.max_workers)

    logging.info("All done in %.2fs", time.time() - total_start)


if __name__ == "__main__":
    main()
