# C3 application sizes and byte accounting

Run: 2026-11-26. All seven applications are now smaller than the existing C3
builds, with both optimizer settings. All 114 C3 application fixtures pass
(57 per setting). All 114 CMOC fixtures also pass after the shared assembly changes.

Complete optimized OS-9 modules, in bytes:

| Application | Existing C3 | Previous PR | Current PR | vs. existing C3 | Saved from PR |
| --- | ---: | ---: | ---: | ---: | ---: |
| uniq | 5695 | 5912 | 5595 | -100 | 317 |
| dgrep | 10707 | 10903 | 10601 | -106 | 302 |
| ed | 15999 | 16285 | 15971 | -28 | 314 |
| cb | 8637 | 8754 | 8497 | -140 | 257 |
| lb | 6212 | 6481 | 6182 | -30 | 299 |
| ppc | 5438 | 5651 | 5339 | -99 | 312 |
| MicroEMACS | 19553 | 19841 | 19509 | -44 | 332 |

Optimizer off:

| Application | Existing C3 | Current PR | Change |
| --- | ---: | ---: | ---: |
| uniq | 5809 | 5709 | -100 |
| dgrep | 10286 | 10180 | -106 |
| ed | 17682 | 17654 | -28 |
| cb | 7540 | 7400 | -140 |
| lb | 6299 | 6269 | -30 |
| ppc | 5349 | 5250 | -99 |
| MicroEMACS | 21858 | 21814 | -44 |

## Costs removed

The earlier increase was partly port/build overhead, not simply improved stdio.
The audit removed:

- Private stdio calls pushing a FILE pointer already held in U, plus the matching
  callee frame and cleanup. Both helpers now use U directly in the C3 profile.
- Hidden-result copies from `_flacc` back onto itself and redundant reloads of
  the native long-result pointer. Pointer-returning routines return saved D
  directly instead of reloading D and discarding its saved value into X.
- An extra file-creation frame word and retry branch; native retries restore the
  pathname in D. `rewind` keeps its native FILE argument in D while staging zeros.
- Fourteen initialized zero bytes introduced when optx merged printf's BSS with
  its initialized data. Data-only units bypass the instruction optimizer.
- The unused duplicate `_rpterr` hook already supplied by the compiler's CRT.
- Unused status-call bodies and error-return families bundled into archive members.
  Splitting existing bodies creates linkable objects, not new runtime wrappers.
  Character-class functions are optimized separately to retain archive independence.
- Duplicated open-function tails, a redundant descriptor reload, and excess
  formatter setup/long branches. `fclose`, `putc`, and `fflush` reuse traditional
  close/write/writeln rather than pulling a second I/O API into stdio.
- An unused seek-offset scratch copy and its branch. The real seek already uses
  the stacked offset argument, including its SEEK_CUR correction.

The expanded tests also exposed a pre-existing SEEK_END bug: buffered input was
incorrectly subtracted from an EOF-relative offset. The shared assembly now
applies that correction only to SEEK_CUR. Both compiler profiles test seeks
within buffered input, SEEK_END, rewind, append after repositioning, fdopen,
freopen, and file-creation retry.

## Every remaining byte difference

The following are **net loaded-byte changes against existing C3**, grouped from
individual archive members. Positive rows show larger implementations; negative
rows show savings. Each column sums exactly to the complete module difference.
There are zero unaccounted bytes.

| Source family | uniq | dgrep | ed | cb | lb | ppc | MicroEMACS |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Open/create | +53 | +53 | +53 | 0 | +53 | +53 | +53 |
| Seek/tell | +26 | +26 | +26 | +26 | +26 | +26 | +26 |
| Input | +4 | +4 | +4 | +16 | +16 | +4 | +16 |
| Output/close | -25 | -31 | -46 | -31 | -25 | -31 | -31 |
| Buffer setup | +13 | +13 | +13 | +13 | +13 | +13 | +13 |
| Formatting | +41 | +41 | +41 | +41 | +41 | +41 | 0 |
| Status calls | -106 | -106 | -106 | -106 | -106 | -106 | -106 |
| Status return helpers | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Heap | -120 | -120 | -36 | -120 | -120 | -120 | -36 |
| Exit/profiling | +20 | +20 | +20 | +20 | +20 | +20 | +20 |
| Character case | -7 | -7 | 0 | 0 | 0 | 0 | 0 |
| Other routines | +1 | +1 | +3 | +1 | +52 | +1 | +1 |
| **Complete module** | **-100** | **-106** | **-28** | **-140** | **-30** | **-99** | **-44** |

Specific larger bodies account for the positive rows:

- `fopen` family: +53 = invalid-mode validation (+18), sticky append state (+12),
  read/write creation for w+ (+24), append-call staging (+1), and smaller entry
  layout (-2). These differences are in the shared implementation, not wrappers.
- `fseek`/`ftell`: +26 = the canonical long fseek result (+8), explicit null checks
  (+8), flush-error checking (+8), and reloading flags before the written-state
  test (+2). Existing C3 fseek returns an int; the canonical API returns a long.
- Formatter family: +41 = printf's character count (+33), zero-extending the
  character passed to putc (+1), long formatter layout (+6), and float-stub
  cursor implementation (+1). The data image and copy-record lengths now match.
- Buffer setup: explicit stdout-unbuffered policy costs 14 bytes; the native
  helper's shorter return saves one, for +13. Exit cleanup is +21, offset by
  eliminating the one-byte profiling stub, for +20.
- Input members: getc/getw/ungetc are +16; separately built fgets saves 12 bytes
  compared with the old gets/fgets member when linked, giving +4 in those apps.
- The other-routine row is strlen (+1) everywhere, signal (+2) in ed, and canonical
  C fread/fwrite (+27/+24) in lb. Those are existing canonical C sources; none
  was converted from assembly in this PR. Saved-pointer returns now make the
  shared string-copy and memset members match existing C3's lengths.

The status reduction is 173 -> 67 bytes: only traditional getstat and its existing
helper are needed. The prior PR pulled all 185 bytes. Heap use is 164 -> 44 bytes
when only ibrk is needed; applications also using malloc need 398 versus 434 bytes
across ibrk/sbrk/memory. These are archive/source differences, not padding.

The restored `utime`, `ltoa`, `dirseek`, and `bsearch` assembly units are absent
from all seven application maps and contribute zero bytes to these differences.
The application objects, compiler startup, FP primitive support, integer/long
math members, initialized FILE table, module names, headers, and CRC lengths
have unchanged loaded-byte totals.

## Reproduce the accounting

Both builds use C3 revision `a6d5154d680965d57dc4ae6c30103e4d44afca2d`, identical
prepared application sources, flags, and six-character module names. Existing C3
application headers isolate the library change; the ABI probes separately use the
generated canonical headers. The old and new map-linked modules have the same
SHA-256 hashes as their corresponding bakeoff binaries.

[SIZE-ACCOUNTING.json](SIZE-ACCOUNTING.json) records the compiler/library hashes,
prepared-source hashes, all three module hashes and sizes, and each changed
archive member's old/previous/current loaded-byte counts. Unchanged member totals
plus changed members plus the 22-byte header/name/CRC overhead reconcile exactly.
BSS and stack sizes are excluded from ROM/module sizes.

To audit a pair of modules, link with `lwlink -m program.map` and run:

```sh
python3 c3/size_report.py \
  --old-map old/program.map --old-module old/program \
  --new-map new/program.map --new-module new/program \
  --json comparison.json
```

The tool rejects unknown sections and any unexplained header/name/CRC remainder.
No padding, benchmark-specific library selection, or speed improvement is claimed.
