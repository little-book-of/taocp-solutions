# How to Solve TAOCP Exercises in This Repository

This file describes the workflow used for adding new solved sections (e.g., `2.2.5`).

## 1) Pin down the exact exercise range first

Before writing anything:

1. identify section title and exercise count;
2. identify required start/end exercise labels;
3. verify numbering style (e.g., `### 1 [06]`).

This prevents writing the wrong section (a previous failure mode).

## 2) Preserve TAOCP representation conventions

For each section, lock in notation at top of chapter:

- data fields (`LINK`, `LLINK`, `RLINK`, etc.);
- pointer names (`TOP`, `F`, `R`, `AVAIL`, etc.);
- empty-state conventions (`Λ`, sentinels, or section-specific invariants).

A single notation block avoids confusion across exercises.

## 3) Solve by exercise type

### A) Data-structure operation exercises

Use this template:

1. representation invariant,
2. operation steps,
3. edge cases (empty/full/singleton),
4. complexity.

### B) Correctness/reasoning exercises

Use this template:

1. claim,
2. key invariant or counterexample,
3. concise argument.

### C) Program-design exercises

Use this template:

1. state layout,
2. control flow,
3. failure handling,
4. why algorithm is correct.

## 4) Keep style consistent with existing chapters

- one heading per exercise: `### k [score]`;
- short prose + concrete steps/pseudocode;
- no filler text or meta narration;
- keep solution self-contained.

## 5) Wire section into book navigation immediately

After adding `vol-1/<section>.md`, update `_quarto.yml` chapter list right away.

## 6) Run minimal structural checks

At minimum:

- count exercise headings with `rg`;
- verify chapter appears in `_quarto.yml`;
- inspect final file with `nl -ba`.

## 7) Commit discipline

- commit only relevant files for that section;
- write a precise commit title;
- create PR message listing scope, coverage, and checks.
