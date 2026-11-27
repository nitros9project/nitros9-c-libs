# Shared native OS-9 calls

`lib/*.as` is the source of OS-9 call implementations for CMOC, C3 and LLVM.
CMOC assembles the stack-argument bodies directly. C3's existing selector
places the first word/pointer in D. `os9/build.py` selects LLVM entries with
that argument and integer results in X, and U as the program data base.
Selection happens at build time: no foreign-ABI call, runtime adapter or
register-block staging is inserted around an ordinary OS call.

The generic `_os_syscall` remains available when a caller explicitly needs a
register block. Unix interfaces (`open`, `creat`, `read`, etc.) retain their
policy layer above the native calls. In particular `_os_create` and
`n9_create` issue raw I$Create and report E$CEF for an existing file; Unix
`creat` retains overwrite/truncate behavior.

`include/os9raw.h` declares services needed by compiler runtimes, including
32-bit X:U status/seek operations and module link/load results. Their original
LLVM assembly now lives in `lib/os9raw.as`, with its license attribution.
`os9/include/os9.h` owns LLVM's compatible public API, constants and aliases.
It must be installed alongside `os9raw.h`; do not put the entire CMOC include
directory before picolibc's standard headers in an LLVM application's search
path. LLVM compatibility names alias the same native symbols without code.

## Build

Python 3, lwasm and an LLVM MC6809 compiler/archiver are required:

```sh
python3 os9/build.py --clang /path/to/clang --ar /path/to/llvm-ar \
  --lwasm /path/to/lwasm --out os9/out/native
```

The output contains one archive member per independently reachable assembly
body and `sources.json` with source hashes. LLVM's compiler-rt invokes this
selector and adds startup/POSIX objects to `libclang_rt.os9.a`. The LLVM
compatibility library invokes the same selector. Neither consumer vendors
its own OS-call implementations.

## Validation

```sh
python3 -m unittest discover -s os9/tests -p 'test_*.py'
make -C llvm test
python3 os9/tests/check.py --help
```

`check.py` builds the same probe with all three compilers and runs it on a
NitrOS-9 kernel under USIM. It requires ToolShed `os9`, lwasm, CMOC, built C3,
an installed OS-9 LLVM/picolibc sysroot, and a Pico-Thing boot disk/firmware.
It checks success and error results, errno, raw create semantics, zero/EOF
I/O, 32-bit positions, module operations, process identity/memory, fork,
wait and chain. A positive output marker is required for each compiler.
