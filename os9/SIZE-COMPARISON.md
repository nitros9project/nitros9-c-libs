# LLVM application module sizes

Measured 2026-11-27. Values are complete OS-9 module bytes, including headers,
with the same six-character module name (`appmod`) for both builds.

Both sides use LLVM MC6809 1.1.0-rc2 (`19fc4dc208be`), CPU mc6809,
the same prepared bakeoff application sources, and picolibc `f0f6a76c83`
configured `debug=false`, integer stdio, `-Os`. The application optimization
varies as shown. The baseline uses the released LLVM runtime; the shared
build replaces only the runtime/header provider and rebuilds picolibc.
Neither links the optional Kreider LLVM compatibility archive.

| Application | -Os old → shared | Saved | -Oz old → shared | Saved | -O2 old → shared | Saved |
|---|---:|---:|---:|---:|---:|---:|
| uniq | 13,554 → 13,472 | 82 | 13,518 → 13,438 | 80 | 14,460 → 14,380 | 80 |
| dgrep | 17,833 → 17,753 | 80 | 17,551 → 17,471 | 80 | 19,137 → 19,055 | 82 |
| ed | 23,687 → 23,605 | 82 | 23,219 → 23,139 | 80 | 24,605 → 24,523 | 82 |
| cb | 12,971 → 12,941 | 30 | 12,333 → 12,303 | 30 | 14,497 → 14,467 | 30 |
| lb | 13,236 → 13,154 | 82 | 13,102 → 13,020 | 82 | 13,968 → 13,886 | 82 |
| ppc | 12,636 → 12,556 | 80 | 12,614 → 12,532 | 82 | 12,694 → 12,614 | 80 |
| uemacs | 27,010 → 26,930 | 80 | 25,524 → 25,442 | 82 | 30,454 → 30,374 | 80 |

All 21 modules shrink by 30–82 bytes. These are size measurements, not a
timing comparison or a published bakeoff rerun. The released compiler still
emits LF for `\n`; these builds do not claim validation of the unpublished
compiler line-ending change. Kernel-call correctness is tested separately
with explicit OS-9 line endings.

To repeat, build/install the same picolibc revision against the released
runtime and the shared runtime, then run:

```sh
python3 os9/tests/compare_sizes.py --prepared /path/to/prepared/llos \
  --old-clang /path/to/released/clang --shared-clang /path/to/shared/clang \
  --old-sysroot /path/to/old/stage/usr/local \
  --shared-sysroot /path/to/shared/stage/usr/local --out os9/out/sizes
```

The script retains linker maps, build logs, modules, exact compiler versions
and a SHA-256 manifest of prepared sources alongside its JSON size table.
The prepared-source manifest for this run hashes to:
`3b462060c06947b86d49b1dbc09c4db20a8565b6aa203ddb6a73224e9fea38f6`.
