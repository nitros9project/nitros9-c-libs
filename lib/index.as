                    section code
_strchr             EXPORT
_index              EXPORT
_strrchr            EXPORT
_rindex             EXPORT

_strchr:
_index:
stk_strchr_ret      equ 0
stk_strchr_string   equ 2
stk_strchr_char     equ 4
stk_strchr_char_byte equ 5
                    ldx stk_strchr_string,s
strchr_scan         ldb ,x+
                    cmpb stk_strchr_char_byte,s
                    beq strchr_found
                    tstb
                    bne strchr_scan
                    clra
                    rts
strchr_found        leax -1,x
                    tfr x,d
                    rts

_strrchr:
_rindex:
stk_strrchr_ret     equ 0
stk_strrchr_string  equ 2
stk_strrchr_char    equ 4
stk_strrchr_char_byte equ 5
                    pshs u
                    ldx stk_strrchr_string+2,s
                    ldu #0
strrchr_scan        ldb ,x+
                    cmpb stk_strrchr_char_byte+2,s
                    bne strrchr_next
                    leau -1,x
strrchr_next        tstb
                    bne strrchr_scan
                    tfr u,d
                    puls u,pc
                    endsect
