                    IFDEF NITROS9_C3
                    use ../include/os9.d
                    use ../include/stdio.d
                    section code
_exit               EXPORT
__exit              EXPORT
__iob               EXTERNAL
_fclose             EXTERNAL
_exit:
                    pshs d,u
                    leau __iob,y
close_next:
                    ldd FILE_FLAG,u
                    bitb #_READ|_WRITE
                    beq close_skip
                    tfr u,d
                    lbsr _fclose
close_skip:
                    leau FILE_SIZE,u
                    leax __iob+FILE_SIZE*16,y
                    pshs u
                    cmpx ,s++
                    bne close_next
                    puls d,u
__exit:
                    os9 F_Exit
                    endsect
                    ELSE
                    use       ../include/os9.d ; shared OS-9 service constants

__exit              EXPORT    ;         export exit wrapper with cleanup
_exit               EXPORT    ;         export raw process-exit entry point

__tidyup            EXTERNAL  ;         stdio/runtime cleanup hook

                    section   code      ; begin code section

__exit:
                    lbsr      __tidyup  ; flush and close runtime-managed resources
                    bra       _exit     ; tail into the raw exit path

_exit:
stk_exit_ret        equ       0         ; caller return address, unused because F$Exit does not return
stk_exit_status     equ       2         ; process exit status argument
                    ldd       stk_exit_status,s ; pass caller-supplied status to F$Exit
                    os9       F_Exit    ; terminate the current process

                    endsect   ;         end code section

                    ENDC
