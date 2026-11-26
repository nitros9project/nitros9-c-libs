# Application size comparison

Run: 2026-11-26. Sizes are complete OS-9 modules in bytes, including identical
six-character module-name overhead. All 114 application fixtures pass (57 per
optimizer setting). The C3 library is compiled natively, without runtime ABI bridges.

| Application | Old, optimizer off | Shared, off | Change | Old, optimizer on | Shared, on | Change |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| uniq | 5809 | 6026 | +217 | 5695 | 5912 | +217 |
| dgrep | 10286 | 10482 | +196 | 10707 | 10903 | +196 |
| ed | 17682 | 17968 | +286 | 15999 | 16285 | +286 |
| cb | 7540 | 7657 | +117 | 8637 | 8754 | +117 |
| lb | 6299 | 6568 | +269 | 6212 | 6481 | +269 |
| ppc | 5349 | 5562 | +213 | 5438 | 5651 | +213 |
| uemacs | 21858 | 22146 | +288 | 19553 | 19841 | +288 |

These binaries are **not the same size**. Native calling-convention selection
avoids adapter calls; it does not make different library implementations byte-identical.
The largest shared-code differences are in `fopen` (65 bytes), `fseek` (68 bytes),
and `printf` (59 bytes), measured from the `uniq` linker maps. The shared stdio
bodies include explicit update/append state and error handling; this comparison
does not establish a speed improvement. Archive grouping also matters: the C3
build separates unused low-level I/O entry points rather than linking the whole unit.

Both builds use C3 revision `a6d5154d680965d57dc4ae6c30103e4d44afca2d`.
Prepared-source hashes, fixtures, startup, and application flags match the prior
bakeoff run. The comparison uses existing C3 application headers to isolate the
library change; the ABI probes separately compile with the generated canonical
headers. Compiler-owned CRT/FP support is unchanged for the application comparison.

No padding or benchmark-specific library selection is used to force size equality.
