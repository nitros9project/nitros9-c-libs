* Raw OS-9 runtime services, shared by CMOC, C3 and LLVM.
* X:U and module bodies preserve the assembly from llvm-mc6809
* compiler-rt/lib/builtins/mc6809-os9/{os9-xu,os9-link}.S.
* SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
* Part of LLVM-MC6809, under the Apache License v2.0 with LLVM Exceptions.
* https://llvm.org/LICENSE.txt
                    use ../include/os9.d
                    section code
_osret              EXTERNAL
_oserr              EXTERNAL
_n9_create          EXPORT
_n9_create:
stk_n9_create_ret equ 0
stk_n9_create_name equ 2
stk_n9_create_mode equ 4
stk_n9_create_attrs equ 6
stk_n9_create_out equ 8
                    ldx stk_n9_create_name,s
                    lda stk_n9_create_mode+1,s
                    ldb stk_n9_create_attrs+1,s
                    os9 I_Create
                    bcs n9_create_done
                    tfr a,b
                    clra
                    std [stk_n9_create_out,s]
n9_create_done
                    lbra _osret
_n9_delete          EXPORT
_n9_delete:
stk_n9_delete_ret equ 0
stk_n9_delete_name equ 2
                    ldx stk_n9_delete_name,s
                    os9 I_Delete
                    lbra _osret
_n9_chgdir          EXPORT
_n9_chgdir:
stk_n9_chgdir_ret equ 0
stk_n9_chgdir_name equ 2
stk_n9_chgdir_mode equ 4
                    ldx stk_n9_chgdir_name,s
                    lda stk_n9_chgdir_mode+1,s
                    os9 I_ChgDir
                    lbra _osret
_n9_dup             EXPORT
_n9_dup:
stk_n9_dup_ret equ 0
stk_n9_dup_path equ 2
stk_n9_dup_out equ 4
                    lda stk_n9_dup_path+1,s
                    os9 I_Dup
                    bcs n9_dup_done
                    tfr a,b
                    clra
                    std [stk_n9_dup_out,s]
n9_dup_done         lbra _osret
_n9_getstt_buf      EXPORT
_n9_getstt_buf:
stk_n9_gbuf_ret equ 0
stk_n9_gbuf_path equ 2
stk_n9_gbuf_fn equ 4
stk_n9_gbuf_buf equ 6
stk_n9_gbuf_count equ 8
                    pshs y
                    lda stk_n9_gbuf_path+3,s
                    ldb stk_n9_gbuf_fn+3,s
                    ldx stk_n9_gbuf_buf+2,s
                    ldy stk_n9_gbuf_count+2,s
                    os9 I_GetStt
                    puls y
                    lbra _osret
_n9_setstt_buf      EXPORT
_n9_setstt_buf:
stk_n9_sbuf_ret equ 0
stk_n9_sbuf_path equ 2
stk_n9_sbuf_fn equ 4
stk_n9_sbuf_buf equ 6
stk_n9_sbuf_count equ 8
                    pshs y
                    lda stk_n9_sbuf_path+3,s
                    ldb stk_n9_sbuf_fn+3,s
                    ldx stk_n9_sbuf_buf+2,s
                    ldy stk_n9_sbuf_count+2,s
                    os9 I_SetStt
                    puls y
                    lbra _osret
_n9_getstt          EXPORT
_n9_getstt:
stk_n9_getstt_ret equ 0
stk_n9_getstt_path equ 2
stk_n9_getstt_fn equ 4
                    lda stk_n9_getstt_path+1,s
                    ldb stk_n9_getstt_fn+1,s
                    os9 I_GetStt
                    lbra _osret
_n9_mem             EXPORT
_n9_mem:
stk_n9_mem_ret equ 0
stk_n9_mem_size equ 2
stk_n9_mem_actual equ 4
stk_n9_mem_top equ 6
                    pshs y
                    ldd stk_n9_mem_size+2,s
                    os9 F_Mem
                    bcs n9_mem_done
                    ldx stk_n9_mem_actual+2,s
                    beq n9_mem_top
                    std ,x
n9_mem_top          ldx stk_n9_mem_top+2,s
                    beq n9_mem_done
                    sty ,x
n9_mem_done         puls y
                    lbra _osret
_n9_id              EXPORT
_n9_id:
stk_n9_id_ret equ 0
stk_n9_id_pid equ 2
stk_n9_id_uid equ 4
                    pshs y
                    os9 F_ID
                    bcs n9_id_done
                    tfr a,b
                    clra
                    ldx stk_n9_id_pid+2,s
                    beq n9_id_uid
                    std ,x
n9_id_uid           ldx stk_n9_id_uid+2,s
                    beq n9_id_done
                    sty ,x
n9_id_done          puls y
                    lbra _osret
_n9_sleep           EXPORT
_n9_sleep:
stk_n9_sleep_ret equ 0
stk_n9_sleep_ticks equ 2
                    ldx stk_n9_sleep_ticks,s
                    os9 F_Sleep
                    lbra _osret
_n9_exit            EXPORT
_n9_exit:
stk_n9_exit_ret equ 0
stk_n9_exit_status equ 2
                    ldb stk_n9_exit_status+1,s
                    os9 F_Exit
n9_exit_forever     bra n9_exit_forever
_n9_seek            EXPORT
_n9_seek:
stk_n9_seek_ret equ 0
stk_n9_seek_arg equ 2
                    ldx stk_n9_seek_arg,s
                    pshs u,x
                    lda ,x
                    ldu 4,x
                    ldx 2,x
                    os9 I_Seek
                    bra n9_xu_return
_n9_setstt_xu       EXPORT
_n9_setstt_xu:
stk_n9_setxu_ret equ 0
stk_n9_setxu_arg equ 2
                    ldx stk_n9_setxu_arg,s
                    pshs u,x
                    ldd ,x
                    ldu 4,x
                    ldx 2,x
                    os9 I_SetStt
                    bra n9_xu_return
_n9_getstt_xu       EXPORT
_n9_getstt_xu:
stk_n9_getxu_ret equ 0
stk_n9_getxu_arg equ 2
                    ldx stk_n9_getxu_arg,s
                    pshs u,x
                    ldd ,x
                    os9 I_GetStt
                    bcs n9_xu_return
                    pshs u
                    ldu 2,s
                    stx 2,u
                    puls x
                    stx 4,u
n9_xu_return        puls x,u
                    lbra _osret
_n9_link            EXPORT
_n9_link:
stk_n9_link_ret equ 0
stk_n9_link_arg equ 2
                    ldx stk_n9_link_arg,s
                    pshs y,u,x
                    lda 2,x
                    ldx ,x
                    os9 F_Link
                    bra n9_module_found
_n9_load            EXPORT
_n9_load:
stk_n9_load_ret equ 0
stk_n9_load_arg equ 2
                    ldx stk_n9_load_arg,s
                    pshs y,u,x
                    lda 2,x
                    ldx ,x
                    os9 F_Load
n9_module_found     bcs n9_module_return
                    ldx ,s
                    stu 3,x
                    sty 5,x
n9_module_return    puls x,y,u
                    lbra _osret
_n9_unlink          EXPORT
_n9_unlink:
stk_n9_unlink_ret equ 0
stk_n9_unlink_arg equ 2
                    pshs u
                    ldu stk_n9_unlink_arg+2,s
                    os9 F_UnLink
                    puls u
                    lbra _osret
_n9_prerr           EXPORT
_n9_prerr:
stk_n9_prerr_ret equ 0
stk_n9_prerr_path equ 2
stk_n9_prerr_error equ 4
                    lda stk_n9_prerr_path+1,s
                    ldb stk_n9_prerr_error+1,s
                    os9 F_PErr
                    lbra _osret
_n9_icpt            EXPORT
_n9_icpt:
stk_n9_icpt_ret equ 0
stk_n9_icpt_entry equ 2
stk_n9_icpt_data equ 4
                    pshs u
                    ldx stk_n9_icpt_entry+2,s
                    ldu stk_n9_icpt_data+2,s
                    os9 F_Icpt
                    puls u
                    lbra _osret
                    endsect
