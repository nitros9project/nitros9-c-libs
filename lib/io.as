                    use       ../include/os9.d ; shared OS-9 service constants
                    use       ../include/fcntl.d ; shared file access and permission constants
                    use       ../include/stdio.d ; shared seek-origin constants

__os_create         EXPORT    ;         export low-level create wrapper
__os_open           EXPORT    ;         export low-level open wrapper
__os_close          EXPORT    ;         export low-level close wrapper
__os_delete         EXPORT    ;         export low-level delete wrapper
__os_makdir         EXPORT    ;         export low-level make-directory wrapper
__os_read           EXPORT    ;         export low-level read wrapper
__os_readln         EXPORT    ;         export low-level readln wrapper
__os_write          EXPORT    ;         export low-level write wrapper
__os_writeln        EXPORT    ;         export low-level writeln wrapper
__os_seek           EXPORT    ;         export direct OS-9 seek wrapper
_lseek              EXPORT    ;         export stdio-style long seek helper

_oserr              EXTERNAL  ;         common OS-9 error-return helper
_osok               EXTERNAL  ; unconditional successful return
_osret              EXTERNAL  ;         common OS-9 success-return helper
_errno              EXTERNAL  ;         C errno storage
_flacc              EXTERNAL  ;         shared long return accumulator

                    section   code      ; begin code section

__os_create:
stk_os_create_ret       equ 0          ; caller return address
stk_os_create_path      equ 2          ; pathname argument
stk_os_create_mode      equ 4          ; exact OS-9 access mode
stk_os_create_outptr    equ 6          ; returned path descriptor
stk_os_create_perm      equ 8          ; exact OS-9 attributes
                    ldx       stk_os_create_path,s
                    lda       stk_os_create_mode+1,s
                    ldb       stk_os_create_perm+1,s
                    os9       I_Create  ; raw create: existing files are errors
                    bcs       os_create_done
                    tfr       a,b       ; widen returned path descriptor
                    clra
                    std       [stk_os_create_outptr,s]
os_create_done
                    lbra      _osret

__os_open:
stk_os_open_ret equ 0
stk_os_open_path equ 2
stk_os_open_mode equ 4
stk_os_open_outptr equ 6
                    ldx stk_os_open_path,s
                    lda stk_os_open_mode+1,s
                    os9 I_Open
                    bcs os_open_done
                    tfr a,b
                    clra
                    std [stk_os_open_outptr,s]
os_open_done        lbra _osret

__os_close:
stk_os_close_ret equ 0
stk_os_close_path equ 2
                    lda stk_os_close_path+1,s
                    os9 I_Close
                    lbra _osret

__os_delete:
stk_os_delete_ret equ 0
stk_os_delete_path equ 2
stk_os_delete_mode equ 4
                    ldx stk_os_delete_path,s
                    lda stk_os_delete_mode+1,s
                    os9 I_DeletX
                    lbra _osret

__os_makdir:
stk_os_makdir_ret equ 0
stk_os_makdir_path equ 2
stk_os_makdir_perm equ 4
                    ldx stk_os_makdir_path,s
                    ldb stk_os_makdir_perm+1,s
                    os9 I_MakDir
                    lbra _osret

__os_read:
stk_os_read_saved_y equ       0         ; saved Y register after pshs y
stk_os_read_ret     equ       2         ; caller return address after pshs y
stk_os_read_path_byte equ       5         ; low byte of path number argument
stk_os_read_buffer  equ       6         ; destination buffer pointer
stk_os_read_countp  equ       8         ; caller pointer to requested/actual byte count
                    pshs      y         ; preserve Y while staging count pointer
                    lda       stk_os_read_path_byte,s ; load path number
                    ldx       stk_os_read_buffer,s ; load destination buffer pointer
                    ldy       [stk_os_read_countp,s] ; load requested byte count from caller pointer
                    os9       I_Read    ; read bytes from the path
afterread
                    bcc       savecount ; continue if the read succeeded
                    cmpb      #E_EOF    ; treat EOF as a short read rather than hard error
                    bne       readerr   ; branch out for all other OS-9 errors
                    ldy       #0        ; report zero bytes read at end of file
                    bra       savecount ; write back zero count and return success
readerr
                    puls      y       ; restore caller's Y
                    lbra      _oserr    ; return OS-9 error through shared helper
savecount
                    sty       [stk_os_read_countp,s] ; store actual count through caller pointer
                    puls      y       ; restore caller's Y
                    lbra      _osok    ; return success through shared helper

__os_readln:
stk_os_readln_saved_y equ       0         ; saved Y register after pshs y
stk_os_readln_ret   equ       2         ; caller return address after pshs y
stk_os_readln_path_byte equ       5         ; low byte of path number argument
stk_os_readln_buffer equ       6         ; destination buffer pointer
stk_os_readln_countp equ       8         ; caller pointer to requested/actual byte count
                    pshs      y         ; preserve Y while staging count pointer
                    lda       stk_os_readln_path_byte,s ; load path number
                    ldx       stk_os_readln_buffer,s ; load destination buffer pointer
                    ldy       [stk_os_readln_countp,s] ; load requested byte count from caller pointer
                    os9       I_ReadLn  ; read one line from the path
                    bra       afterread ; share the count/error handling path

__os_write:
stk_os_write_saved_y equ       0         ; saved Y register after pshs y
stk_os_write_ret    equ       2         ; caller return address after pshs y
stk_os_write_path_byte equ       5         ; low byte of path number argument
stk_os_write_buffer equ       6         ; source buffer pointer
stk_os_write_countp equ       8         ; caller pointer to requested/actual byte count
                    pshs      y         ; preserve Y while using it as the count register
                    ldy       [stk_os_write_countp,s] ; load requested byte count from caller pointer
                    beq       writeex   ; treat zero-length write as immediate success
                    lda       stk_os_write_path_byte,s ; load path number
                    ldx       stk_os_write_buffer,s ; load source buffer pointer
                    os9       I_Write   ; write bytes to the path
write_status_check  bcc       store_writeex ; continue if the write succeeded
                    puls      y         ; restore caller's Y before error return
                    lbra      _oserr    ; return OS-9 error through shared helper
store_writeex
                    sty       [stk_os_write_countp,s] ; store actual byte count through caller pointer
writeex
                    puls      y         ; restore caller's Y register
                    lbra      _osok    ; return success through shared helper

__os_writeln:
stk_os_writeln_saved_y equ       0         ; saved Y register after pshs y
stk_os_writeln_ret  equ       2         ; caller return address after pshs y
stk_os_writeln_path_byte equ       5         ; low byte of path number argument
stk_os_writeln_buffer equ       6         ; source buffer pointer
stk_os_writeln_countp equ       8         ; caller pointer to requested/actual byte count
                    pshs      y         ; preserve Y while using it as the count register
                    ldy       [stk_os_writeln_countp,s] ; load requested byte count from caller pointer
                    beq       writeex   ; treat zero-length write as immediate success
                    lda       stk_os_writeln_path_byte,s ; load path number
                    ldx       stk_os_writeln_buffer,s ; load source buffer pointer
                    os9       I_WritLn  ; write bytes followed by line termination
                    bra       write_status_check ; share the count/error handling path

__os_seek:
stk_os_seek_ret equ 0
stk_os_seek_path equ 2
stk_os_seek_pos_hi equ 4
stk_os_seek_pos_lo equ 6
                    pshs u
                    lda stk_os_seek_path+3,s
                    ldx stk_os_seek_pos_hi+2,s
                    ldu stk_os_seek_pos_lo+2,s
                    os9 I_Seek
                    puls u
                    lbra _osret

_lseek:
stk_lseek_saved_u   equ       0         ; saved U register after pshs u
stk_lseek_ret       equ       2         ; caller return address after pshs u
stk_lseek_resultp   equ       4         ; hidden pointer receiving 32-bit return value
stk_lseek_path_byte equ       7         ; low byte of path number argument
stk_lseek_offset_hi equ       8         ; high word of signed 32-bit offset
stk_lseek_offset_lo equ       10        ; low word of signed 32-bit offset
stk_lseek_whence    equ       12        ; seek-origin selector
                    pshs      u         ; preserve caller's U register
                    ldd       stk_lseek_whence,s ; load whence selector
                    bne       lseek10   ; branch for SEEK_CUR/SEEK_END cases
                    ldu       #0        ; SEEK_SET starts from absolute zero low word
                    ldx       #0        ; SEEK_SET starts from absolute zero high word
                    bra       doseek    ; combine base and requested offset

lseek10
                    cmpd      #SEEK_CUR ; test for current-position relative seek
                    beq       here      ; fetch current file position as base
                    cmpd      #SEEK_END ; test for end-of-file relative seek
                    beq       end       ; fetch file size as base
                    ldb       #E_Seek   ; preload invalid-whence error code
lserr
                    clra                ; clear high byte for errno store
                    std       _errno,y  ; update errno with the seek failure code
                    ldd       #-1       ; prepare long -1 return value
                    ldx       stk_lseek_resultp,s ; load hidden pointer to 32-bit return slot
                    std       0,x       ; store high word of -1
                    std       2,x       ; store low word of -1
                    puls      u,pc      ; restore U and return failure

end
                    lda       stk_lseek_path_byte,s ; load path number
                    ldb       #SS_Size  ; request 32-bit file size
                    os9       I_GetStt  ; fetch end-of-file position into X/U
                    bcs       lserr     ; fail if GetStat did not succeed
                    bra       doseek    ; add requested offset to file size

here
                    lda       stk_lseek_path_byte,s ; load path number
                    ldb       #SS_Pos   ; request current 32-bit file position
                    os9       I_GetStt  ; fetch current offset into X/U
                    bcs       lserr     ; fail if GetStat did not succeed

doseek
                    tfr       u,d       ; copy base low word into D
                    addd      stk_lseek_offset_lo,s ; add requested low-word offset
                    std       _flacc+2,y ; save tentative low word in long accumulator
                    tfr       d,u       ; keep combined low word in U for direct seek
                    tfr       x,d       ; copy base high word into D
                    adcb      stk_lseek_offset_hi+1,s ; add carry and requested high-word low byte
                    adca      stk_lseek_offset_hi,s ; add requested high-word high byte
                    bmi       lserr     ; reject negative resulting file positions
                    tfr       d,x       ; keep combined high word in X for direct seek
                    std       _flacc,y  ; save tentative high word in long accumulator
                    lda       stk_lseek_path_byte,s ; load path number
                    os9       I_Seek    ; apply the new absolute file position
                    bcs       lserr     ; fail if the direct seek was rejected
                    ldx       stk_lseek_resultp,s ; load hidden pointer to 32-bit return slot
                    ldd       _flacc,y  ; fetch resulting high word
                    std       0,x       ; store high word through return pointer
                    ldd       _flacc+2,y ; fetch resulting low word
                    std       2,x       ; store low word through return pointer
                    puls      u,pc      ; restore U and return success

                    endsect   ;         end code section
