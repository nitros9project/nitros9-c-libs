* Binary search with a zero-based lower bound and remaining element count.
* Keep comparator arguments balanced and preserve both U and Y across callbacks.

                    section code
_bsearch            EXPORT
ccmult              EXTERNAL

_bsearch:
                    pshs d,x,y,u
                    leas -8,s
bs_low              equ 0
bs_count            equ 2
bs_mid              equ 4
bs_candidate        equ 6
                    ifdef NITROS9_C3
bs_base             equ 18
bs_nel              equ 20
bs_width            equ 22
bs_compare          equ 24
                    ldu 8,s             ; key saved from native first argument D
                    else
bs_base             equ 20
bs_nel              equ 22
bs_width            equ 24
bs_compare          equ 26
                    ldu 18,s            ; stacked key
                    endc
                    clra
                    clrb
                    std bs_low,s
                    ldd bs_nel,s
                    std bs_count,s
bs_loop             ldd bs_count,s
                    beq bs_missing
                    lsra
                    rorb
                    addd bs_low,s
                    std bs_mid,s        ; midpoint index in the original array
                    pshs d              ; ccmult consumes this index word
                    ldd bs_width+2,s
                    lbsr ccmult
                    addd bs_base,s      ; element address uses base, never key
                    std bs_candidate,s
                    pshs d              ; comparator's second argument
                    ifdef NITROS9_C3
                    tfr u,d             ; comparator's first argument
                    jsr [bs_compare+2,s]
                    leas 2,s
                    else
                    pshs u
                    jsr [bs_compare+4,s]
                    leas 4,s
                    endc
                    cmpd #0             ; LEAS does not set the comparison flags
                    beq bs_found
                    blt bs_lower
                    ldd bs_mid,s
                    subd bs_low,s       ; number of elements through midpoint
                    addd #1
                    pshs d
                    ldd bs_count+2,s
                    subd ,s++
                    std bs_count,s
                    ldd bs_mid,s
                    addd #1
                    std bs_low,s
                    bra bs_loop
bs_lower            ldd bs_mid,s
                    subd bs_low,s
                    std bs_count,s
                    bra bs_loop
bs_found            ldd bs_candidate,s
                    bra bs_return
bs_missing          clra
                    clrb
bs_return           leas 12,s           ; locals and saved scratch D/X
                    puls y,u,pc
                    endsect
