# C Library support for OS-9/NitrOS-9

This project provides C libraries for CMOC and LLVM targeting OS-9/NitrOS-9
on the MC6809. The C library is based on the Kreider C library; the CMOC
CGFX library is based on Mike Sweet's CGFX7 library.

| Toolchain | Libraries | Build |
| --- | --- | --- |
| CMOC | `libc.a`, floating-point `libcf.a`, and `libcgfx.a` | `make libs` |
| LLVM with picolibc | `libcmoc_os9_compat.a` and optional `libcmoc_os9_float.a` | `make -C llvm` |

[CMOC](https://perso.b2b2c.ca/~sarrazip/dev/cmoc.html) is Pierre Sarrazin's
ANSI C cross-compiler. The LLVM port uses the MC6809 LLVM toolchain and an
OS-9 picolibc sysroot, with native implementations of the Kreider and OS-9
extensions. See [Building with LLVM](#building-with-llvm) below.

## Building with CMOC

You will need CMOC, LWTOOLS, and ToolShed to build the libraries and programs.
Run the following commands from the repository root.

To make both the default non-floating-point `libc.a` and the floating-point
`libcf.a` C libraries, plus `libcgfx.a`, type:

```
make libs
```

To make just the default non-floating-point `libc.a`, type:

```
make -C lib clean libc.a
```

To make just the floating-point `libcf.a`, type:

```
make -C lib clean libcf.a
```

The default `libc.a` build uses a small dummy `pffloat` implementation so the
library can be built and linked for integer/string-only programs without
pulling in the MC6839 floating-point path. The `libcf.a` build enables
the MC6839 floating-point configuration and includes the real formatting and
parsing support.

From there, you can build the CoCo 3 NitrOS-9 test disk:
```
make dsk
```

This will create a disk image called `l2_coco3_cmoc_os9.dsk` under
`recipes/coco3/`. The recipe uses the local repository sources and a
nearby NitrOS-9 checkout for OS modules, commands, libraries, and disk tools.
Set `NITROS9DIR` if your NitrOS-9 checkout is not a sibling of this repository.

You can also build the smaller standalone unit-test disk:
```
make unittest-dsk
```

This will create a disk image called `test.dsk` which you can mount in an
emulator and run under NitrOS-9. A convenient script named `go` is placed in
the root folder of the disk. You can run this script to execute the
non-graphical runtime and regression tests. The CoCo 3-specific graphics
programs such as `wintest` and `maze` are built onto the disk as separate
manual tests; both are under `graphictest/`.

## Differences from the original Microware C Library

The original Microware C library worked within the limitations of the Microware K&R C compiler (e.g. the first 8 characters of a variable or function name were significant.) CMOC eliminates many of those limitations since it's a cross-compiler that runs on modern platforms.

Because of this, we have more freedom to be verbose with function names that were horribly abbreviated, and use calling conventions that are more uniform across the library.

An example of this are the low level C functions for opening and manipulating files in OS-9. Here's the way you would do this in Microware's K&R C compiler:

```
	int p = open("file", S_IREAD | S_IWRITE); // open file for reading and writing
	if (p != -1) {
		// success - valid path
		char buf[10];
		
		int c = read(p, buf, 10);
		if (c == -1) {
			// failure - print the error
			printf("error reading: %d\n", errno);
		}
	} else {
		// failure - print the error
		printf("error opening: %d\n", errno);
	}
```

While this code works and is certainly readable, it tends to fall in the trap of using the return value for one thing or another, complicating error handling.

In the case of open(), the return value is a path... unless -1 is returned, indicated an error occurred.

In the case of read(), a return value is the number of bytes read... unless -1 is returned, indicating an error occurred.

In both cases, we end up having to fetch the error in the global errno variable.

Microware moved to a more uniform method of function usage in [their Ultra C compiler](http://rab.ict.pwr.wroc.pl/dydaktyka/supwa/os9/MWARE/pdf/ultrac_lib_ref.pdf), which reserved the return value strictly for the error code. Here's the same code above rewritten with this new paradigm:

```
	pathid p;
	error_code result = _os_open("file", FAM_READ | FAM_WRITE, &p); // open file for reading and writing
	if (result == 0) {
		// success - valid path
		char buf[10];
		
		int size = 10;
		result = _os_read(p, buf, &size);
		if (result != 0) {
			// failure - print the error
			printf("error reading: %d\n", result);
		}
	} else {
		// failure - print the error
		printf("error opening: %d\n", result);
	}
```

There are several differences in this code:

1. Types are declared with more formal names (e.g. pathid instead of int)
2. The functions are prepended with '_os_'
3. The return value for the functions are reserved for the error -- no needing to pull the error out of errno.
4. The sane values that were being returned in the result of the function are now passed by reference.

While passing parameters by reference may be a bit more typing, this is arguably a cleaner, more consistent approach to using the low-level I/O and other system calls, and is the path being pursued in the creation of this library.

## Work to be done

- More unit tests are needed, especially around the low-level OS-9 I/O layer,
  stdio compatibility, and floating-point formatting/parsing behavior.

The core library is already usable, but it is not yet a complete port of all
historical Kreider and CGFX components.

## Building with LLVM

The `llvm/` directory provides an LLVM-native compatibility library alongside
picolibc, covering all 280 callable declarations in the active C library
headers. It includes OS-9 extensions, IEEE float/double math, numeric conversion,
and an optional floating stdio profile. CGFX remains CMOC-only.

You need a Clang build supporting `mc6809-unknown-os9`, LLVM archive/link tools,
and an installed OS-9 picolibc sysroot. After building picolibc, install it into
its staging directory (run this from the picolibc checkout):

```sh
meson install -C builddir-mc6809-os9-Os --destdir stage --no-rebuild
```

The installed path is `builddir-mc6809-os9-Os/stage/<prefix>`, where `<prefix>`
is Meson's configured installation prefix without the leading `/`: `usr/local`
for the default `/usr/local`, or `opt/homebrew` for `/opt/homebrew`.
Set and export the paths for your checkouts, adjusting the prefix as needed;
the remaining commands run from this repository's root:

```sh
export LLVM_BIN=/path/to/llvm-mc6809/build/bin
export OS9_SYSROOT=/path/to/picolibc/builddir-mc6809-os9-Os/stage/usr/local
make -C llvm -j4
```

Alternatively, set `PROJECTS=/path/to/projects` when `llvm-mc6809` and
`picolibc` are under that directory; its default sysroot assumes the
`/usr/local` prefix, so override `OS9_SYSROOT` for another prefix.
Outputs go in `llvm/out/Os/`; use `OPT=Oz` for a separate size-optimized build.

New code includes `cmoc_os9.h`. Existing Kreider code can force-include
`cmoc_os9_legacy.h` when compiling:

```sh
"$LLVM_BIN/clang" --target=mc6809-unknown-os9 \
  --sysroot="$OS9_SYSROOT" \
  -Os -Illvm/include -include llvm/include/cmoc_os9_legacy.h program.c \
  llvm/out/Os/libcmoc_os9_compat.a -o program
```

For floating `printf` output, place `llvm/out/Os/libcmoc_os9_float.a` before
`libcmoc_os9_compat.a` in the link command. LLVM programs use native picolibc
types and the LLVM calling convention; do not link the CMOC archives or add
the original CMOC `include/` directory to their include path.

Run the seven host test suites and cross-build checks from the repository root.
`test` needs only a host C compiler (`HOST_CC`, default `/usr/bin/clang`); the
cross-build checks use the exported toolchain and sysroot paths:

```sh
make -C llvm test
make -C llvm -j4 audit link-check smoke
```

The cross-build checks audit API coverage, link each callable archive symbol
with its dependencies, and validate two OS-9 smoke modules. They do not execute
the modules. Runtime validation uses picolibc's `scripts/run-mc6809-os9`;
set `OS9_RUNNER` to that script for an independent checkout. It needs ToolShed
`os9` on `PATH` and `usim09pt` on `PATH` (or set `NITROS9_USIM09PT` to the
emulator executable). Supply a Pico-Thing flat IDE boot image with a `/J0`
descriptor and its `rel_picothing.srec` firmware through `NITROS9_BOOT_DSK`
and `NITROS9_FIRMWARE`. Alternatively, set `NITROS9_RECIPES` to the NitrOS-9
`recipes/picothing` directory; the runner discovers both artifacts from the
selected recipe (`NITROS9_LEVEL=2` by default).

`floatsmoke` also requires clang's `FPO9` floating-point module. Set
`MC6809_FP_MODULE` to `lib/clang/<version>/lib/mc6809-unknown-os9/FPO9` in the
LLVM build; `-print-resource-dir` locates the versioned directory:

```sh
export MC6809_FP_MODULE="$("$LLVM_BIN/clang" --target=mc6809-unknown-os9 -print-resource-dir)/lib/mc6809-unknown-os9/FPO9"
NITROS9_BOOT_DSK=/path/to/boot.dsk \
  NITROS9_FIRMWARE=/path/to/rel_picothing.srec \
  make -C llvm run-smoke OS9_RUNNER=/path/to/picolibc/scripts/run-mc6809-os9
```

Cross compilation, host tests, API coverage, linkage, and module structure have
been verified. [Mark Murray reported](https://github.com/nitros9project/nitros9-c-libs/pull/36#issuecomment-6833594213)
that both `os9smoke` (identity and readln) and `floatsmoke` passed on NitrOS-9
Level 2 for Pico-Thing under `usim09pt`, with `FPO9` supplied through
`MC6809_FP_MODULE`. See [llvm/README.md](llvm/README.md) for ABI differences,
runner settings, licensing, and UUCPbb integration.
