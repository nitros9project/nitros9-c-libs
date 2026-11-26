                    section code
_strspn             EXPORT
_strcspn            EXPORT
_strspn:
stk_strspn_ret      equ 0
stk_strspn_string   equ 2
stk_strspn_accept   equ 4
                    pshs y,u
                    ldu stk_strspn_string+4,s
                    ldx stk_strspn_accept+4,s
                    pshs u
span_next           ldb ,u+
                    beq span_done
                    tfr x,y
span_find           lda ,y+
                    beq span_done
                    cmpb -1,y
                    bne span_find
                    bra span_next
_strcspn:
stk_strcspn_ret     equ 0
stk_strcspn_string  equ 2
stk_strcspn_reject  equ 4
                    pshs y,u
                    ldu stk_strcspn_string+4,s
                    ldx stk_strcspn_reject+4,s
                    pshs u
cspan_next          ldb ,u+
                    beq span_done
                    tfr x,y
cspan_find          lda ,y+
                    beq cspan_next
                    cmpb -1,y
                    bne cspan_find
span_done           leau -1,u
                    tfr u,d
                    subd ,s++
                    puls y,u,pc
                    endsect
