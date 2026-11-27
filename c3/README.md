# Native C3 library

The source of the C library is `../lib/`, shared with CMOC. This directory
contains build-time syntax/ABI selection and tests, not another libc source tree.

## Build

Build the host C3 frontend from `nitros9project/nitros9-languages` and put
`lwasm`, `lwar`, `lwlink`, `awk`, `sed`, `cpp`, and `make` on PATH. Python 3.9 or
later is required. No CMOC compiler or CMOC library is required.

```sh
make -C /path/to/nitros9-languages/c3/build/unix CPPFLAGS=-D_DEFAULT_SOURCE
python3 c3/build.py --c3 /path/to/nitros9-languages/c3
python3 -m unittest discover -s c3/tests -p 'test_*.py'
python3 c3/test.py --c3 /path/to/nitros9-languages/c3
```

`out/libc3.a` contains the non-floating stdio/core library. `out/include/` is a
C3-compatible view of the canonical headers. `out/BUILD.json` records compiler
and source hashes; `out/abi-report.json` records assembly entry/call selection.
`--out DIR` selects an isolated build directory for both scripts.

The C3 optimizer is enabled for library C functions. Data-only units skip it to
preserve BSS, and ctype leaves are optimized separately to prevent cross-function
return merging from tying independent archive members together. Stack-check calls are omitted
because the compiler's current cross-runtime stack checker is a no-op. The
application optimizer setting remains independent of the library build.

The shared headers retain inline `putchar`, `feof`, `fileno`, and character-classification
macros alongside their declared functions. This avoids pulling helper functions into
applications for ordinary calls. Use `#undef` for the corresponding macro before
taking a function address with C3, whose preprocessor requires macro arguments.
`toupper` and `tolower` remain functions to preserve non-letter input.

## ABI

The first word/pointer argument is in D; later arguments are on the stack.
A first by-value long stays on the stack. Word/pointer results are in D; long
results use X pointing at the compiler's `_flacc`. Y and U are preserved.

Assembly selection changes the bodies' entry frames and call sites. It does not
emit runtime ABI trampolines, CMOC-compiled bodies, or extra public wrappers.
`utime.as`, `ltoa.as`, `dirseek.as`, and `bsearch.as` remain canonical assembly
implementations. They select argument placement, long returns, and math/callback
contracts with `NITROS9_C3`; no C replacements are generated. The binary search
fix uses the array base, balances callback arguments, and preserves U/Y.
File creation and rewind also select register placement in the shared assembly.

Private stdio helpers use the FILE pointer already held in U in the C3 profile.
The compiler CRT supplies `_flacc` and `_rpterr`; the archive supplies neither.
Independent low-level I/O, status, status-return, and ctype bodies are separate
archive members. Cross-member calls to existing private bodies become ordinary
linker references; the split adds no executable instructions.

C3's 8-character symbol limit requires generated aliases for colliding long API
names. Use headers and objects from the same library revision. C3's header view
exposes signal handler results/constants as opaque words because its parser cannot
declare a function returning a function-pointer typedef; the native ABI is unchanged. The view omits the nonstandard stdio TRUE/FALSE
macros so existing C3 programs can define them without preprocessor diagnostics.
Dollar-name aliases that normalize to self-definitions are omitted as well. Its signed-byte
and signed-long restrictions require explicit byte masks and word-based unsigned
conversion arithmetic in the shared C sources. There is no second set of C bodies.

The compiler still owns its CRT and MC6839 floating arithmetic primitives.
`runtime.py` stages these from the compiler sources for tests; it does not build
`c3/lib/` or use an existing `libc3.a`. The default printf float stub emits no
floating text and advances past C3's eight-byte promoted argument, matching the
existing C3 non-floating stdio profile. Optional `libc3f.a` provides the full binary64 formatter.

## Kernel verification

Use a Pico-Thing Level 2 boot disk that runs `/dd/startup`, its firmware, ToolShed,
and USIM:

```sh
python3 c3/test.py --c3 /path/to/nitros9-languages/c3 \
  --boot-disk /path/to/bench.dsk --firmware /path/to/rel_picothing.srec \
  --emulator /path/to/usim09pt --os9 /path/to/os9
```

Both optimizer settings run in one boot. `out/tests/results.json` records module
hashes and exact stdout/stderr results. The probes cover strings, signed/unsigned
integer boundaries, long returns, callback sorting/search, non-local jumps,
sets, formatting/varargs, all 256 byte values, seek/tell, error returns, calendar
conversion, and exit-time stream flushing. Compile-only success is not a kernel
pass.

The application comparison uses the separate 6809-c-benchmarks suite, with
identical prepared application sources and compiler revision for the old and
new libraries. See [SIZE-COMPARISON.md](SIZE-COMPARISON.md) and its reproducible
`size_report.py` linker-map audit. The new modules are 28–140 bytes smaller; the report accounts for every byte.

## Migrated C3 features

The canonical source now includes the old C3 scanner and decimal conversion,
CORDIC transcendental math, CGFX assembly and window helpers, ttytype lookup and
termcap parameter expansion, register-ABI assembler utilities, and debug tracing.
`PORT-PARITY.json` records the baseline commit, source paths, and original hashes.
The unfinished FLEX termcap skeleton and archive-excluded alternate stat/allocator
files supplied no working archive feature in that baseline. Compiler startup and
integer/MC6839 arithmetic primitives remain compiler-owned.

| Archive | C3 linker argument | Purpose |
| --- | --- | --- |
| `libc3.a` | default | Core, scanf, atof, math; compact printf float stub |
| `libc3f.a` | `-l=fp.l` or `-l=clibf.l` | Full `%f`, `%e`, `%g`; MC6839 initialization |
| `libcgfx.a` | `-l=cgfx.l` | Native C3 CGFX and window helpers |
| `libtermcap.a` | `-l=termcap.l` | `tparam`, `tgoto`, `crtbynam`, `crtbypth` |
| `libalib.a` | `-l=alib.l` | Historical assembly register API, not C-callable |
| `libdbg.a` | `-l=dbg.l` | Historical interactive trace hooks |

Use the updated compiler linker from nitros9-languages PR #23. Floating execution
requires the MC6839 FPO9 module on the target. The default compact formatter does
not change. `pffinit()` remains a floating-profile link anchor. The math port keeps
the original algorithms and legacy domain/range behavior; binary64 boundaries do
not turn it into a new correctly-rounded IEEE libm.

Graphics C and assembly bodies share canonical files with CMOC. Native branches
adjust arguments in the existing routines, without ABI wrappers. Long modern API
names map to historical C3 entry names where their signatures agree; differing
GetStat/mapping contracts retain direct native assembly entries. Compatibility
headers share canonical declarations. The historical `stdio.a` assembler header
is generated from canonical FILE offsets and flags. C3 still has its existing global structure
member-name restriction: the historical WINDOW header and OBJECT declaration use
incompatible `border` members, so compile those interfaces in separate units.

The environment-file API retains `/dd/sys/env.file`, `_ENVFILE`, case-insensitive
names, and two-argument `putenv(name,value)`. Missing names return NULL; replacement
checks capacity, handles overlap, terminates the result, and truncates the file.
The register archive retains its original register contracts; the LWTOOLS syntax
view spells `DECTAB$` as `DECTAB_d` and dollar/dot OS-9 constants with underscores.
Native RMA packaging preserves the original register-archive symbol spellings.

Run the feature probes with both optimizer settings:

```sh
python3 c3/parity.py --c3 /path/to/c3
python3 c3/parity.py --c3 /path/to/c3 --boot-disk boot.dsk \
  --firmware rel_picothing.srec --emulator usim09pt --fpo9 Float09.bin
```

The kernel run checks real file scanning, binary64 conversions/math/formatting,
graphics command packets, overlapping copies, terminal parameter expansion,
environment-file persistence, legacy system calls, and register-ABI arithmetic.
These complement the existing core ABI probe and CMOC unit/graphics suites.
