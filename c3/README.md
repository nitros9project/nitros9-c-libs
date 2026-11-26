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
declare a function returning a function-pointer typedef; the native ABI is unchanged. Its signed-byte
and signed-long restrictions require explicit byte masks and word-based unsigned
conversion arithmetic in the shared C sources. There is no second set of C bodies.

The compiler still owns its CRT and MC6839 floating arithmetic primitives.
`runtime.py` stages these from the compiler sources for tests; it does not build
`c3/lib/` or use an existing `libc3.a`. The default printf float stub emits no
floating text and advances past C3's eight-byte promoted argument, matching the
existing C3 non-floating stdio profile. This is not a C3 CGFX or full floating
stdio port.

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
