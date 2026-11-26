* Shared assembly directory seek helpers for CMOC and native C3.

                    section   code

_seekdir            EXPORT    ;         export this symbol
_telldir            EXPORT    ;         export this symbol

_lseek              EXTERNAL  ;         import C lseek wrapper
                    ifndef NITROS9_C3
copyDWordFromXToD   EXTERNAL  ;         import hidden-long return copier
push4ByteStruct     EXTERNAL  ;         import long-by-value stack helper
                    endc

SEEK_SET            equ       0         ; lseek origin: absolute file position
SEEK_CUR            equ       1         ; lseek origin: current file position

_seekdir:
stk_seekdir_saved_u equ       0         ; saved U after entry prologue
stk_seekdir_ret     equ       2         ; caller return address after entry prologue
stk_seekdir_dirp    equ       4         ; DIR * argument after entry prologue
stk_seekdir_loc     equ       6         ; long location argument after entry prologue
stk_seekdir_result  equ       -4        ; scratch hidden long return slot below U frame
                    ifdef NITROS9_C3
                    pshs      d,u       ; save native DIR pointer and caller U
                    else
                    pshs      u         ; preserve frame register
                    endc
                    leau      ,s        ; anchor a simple U-based frame
                    ifndef NITROS9_C3
                    leas      stk_seekdir_result,s ; reserve scratch long return slot for _lseek
                    endc
                    clra                ; high byte of SEEK_SET selector
                    clrb                ; low byte of SEEK_SET selector
                    pshs      d         ; argument 3 of _lseek(): whence
                    leax      stk_seekdir_loc,u ; address of loc argument
                    leas      -4,s      ; reserve by-value long argument
                    ifdef NITROS9_C3
                    ldd       ,x
                    std       ,s
                    ldd       2,x
                    std       2,s
                    else
                    lbsr      push4ByteStruct ; copy loc argument into reserved stack slot
                    endc
                    ifdef NITROS9_C3
                    ldd       [0,u]     ; DIR pointer saved from native D
                    else
                    ldd       [stk_seekdir_dirp,u] ; load dirp->dd_fd
                    pshs      d         ; argument 1 of _lseek(): path
                    leax      stk_seekdir_result,u ; hidden long return slot for _lseek()
                    pshs      x         ; pass hidden return pointer
                    endc
                    lbsr      _lseek    ; reposition directory path
                    ifdef NITROS9_C3
                    leas      6,s       ; discard long and whence
                    else
                    leas      10,s      ; discard hidden arg + path + long + whence
                    endc
                    ifdef NITROS9_C3
                    leas      2,u       ; release frame and saved DIR argument
                    else
                    leas      ,u        ; release local scratch
                    endc
                    puls      u,pc

_telldir:
stk_telldir_saved_u equ       0         ; saved U after entry prologue
stk_telldir_ret     equ       2         ; caller return address after entry prologue
stk_telldir_resultp equ       4         ; hidden long return pointer
stk_telldir_dirp    equ       6         ; DIR * argument after hidden return pointer
stk_telldir_result  equ       -4        ; scratch hidden long return slot below U frame
                    ifdef NITROS9_C3
                    pshs      d,u       ; save native DIR pointer and caller U
                    else
                    pshs      u         ; preserve frame register
                    endc
                    leau      ,s        ; anchor a simple U-based frame
                    ifndef NITROS9_C3
                    leas      stk_telldir_result,s ; reserve scratch long return slot for _lseek
                    endc
                    clra                ; high byte of SEEK_CUR selector
                    ldb       #SEEK_CUR ; low byte of SEEK_CUR selector
                    pshs      d         ; argument 3 of _lseek(): whence
                    leax      seek_zero_offset,pcr ; address of 32-bit zero offset
                    leas      -4,s      ; reserve by-value long zero argument
                    ifdef NITROS9_C3
                    clra
                    clrb
                    std       ,s
                    std       2,s
                    else
                    lbsr      push4ByteStruct ; copy zero offset into reserved stack slot
                    endc
                    ifdef NITROS9_C3
                    ldd       [0,u]     ; DIR pointer saved from native D
                    else
                    ldd       [stk_telldir_dirp,u] ; load dirp->dd_fd
                    pshs      d         ; argument 1 of _lseek(): path
                    leax      stk_telldir_result,u ; hidden long return slot for _lseek()
                    pshs      x         ; pass hidden return pointer
                    endc
                    lbsr      _lseek    ; query current directory path position
                    ifdef NITROS9_C3
                    leas      6,s       ; discard long and whence
                    else
                    leas      10,s      ; discard hidden arg + path + long + whence
                    endc
                    ifndef NITROS9_C3
                    leax      stk_telldir_result,u ; address of scratch long result
                    ldd       stk_telldir_resultp,u ; hidden return pointer for telldir()
                    lbsr      copyDWordFromXToD ; copy _lseek result to caller's return slot
                    endc
                    ifdef NITROS9_C3
                    leas      2,u       ; release frame and saved DIR argument
                    else
                    leas      ,u        ; release local scratch
                    endc
                    puls      u,pc

seek_zero_offset    fdb       $0000,$0000 ; constant 32-bit zero seek offset

                    endsect
