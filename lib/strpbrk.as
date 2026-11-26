                    section code
_strpbrk            EXPORT
_strpbrk:
stk_strpbrk_ret     equ 0
stk_strpbrk_string  equ 2
stk_strpbrk_accept  equ 4
                    pshs y,u
                    ldu stk_strpbrk_string+4,s
                    ldx stk_strpbrk_accept+4,s
pbrk_next           ldb ,u+
                    beq pbrk_absent
                    tfr x,y
pbrk_find           lda ,y+
                    beq pbrk_next
                    cmpb -1,y
                    bne pbrk_find
                    leau -1,u
                    tfr u,d
                    puls y,u,pc
pbrk_absent         clra
                    clrb
                    puls y,u,pc
                    endsect
