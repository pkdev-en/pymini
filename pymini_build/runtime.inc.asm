; ==========================================================================
; runtime.inc.asm - Cac ham chay LUC THUC THI (khong phai tinh san luc
; compile) - dung cho move()/moveto()/erase(). Quy uoc thanh ghi:
;   rt_plot_pixel / rt_clear_pixel : vao R4=x, R5=y (bat/tat 1 diem anh)
;   rt_fill_rect / rt_clear_rect   : vao R4=x,R5=y,R6=cao,R7=dai
; CANH BAO: cac ham nay dung R0-R15 lam thanh ghi tam - KHONG duoc goi
; xen giua luc dang tinh mot bieu thuc dang do (bieu thuc dung R0-R3).
; ==========================================================================

rt_plot_pixel:
    MOV R2, R5
    MOV R15, #32
    MUL ER2, R15
    MOV R0, #0
    MOV R1, #0F8H
    ADD ER0, ER2
    MOV R12, R4
    SRL R12, #3
    ADD R0, R12
    MOV R13, #0
    ADDC R1, R13
    MOV R12, R4
    AND R12, #7
    MOV R13, #7
    SUB R13, R12
    MOV R2, #1
    SLL R2, R13
    MOV R3, #0
    ST R3, 61495
    L R3, [ER0]
    OR R3, R2
    ST R3, [ER0]
    MOV R3, #4
    ST R3, 61495
    L R3, [ER0]
    OR R3, R2
    ST R3, [ER0]
    RT

rt_clear_pixel:
    MOV R2, R5
    MOV R15, #32
    MUL ER2, R15
    MOV R0, #0
    MOV R1, #0F8H
    ADD ER0, ER2
    MOV R12, R4
    SRL R12, #3
    ADD R0, R12
    MOV R13, #0
    ADDC R1, R13
    MOV R12, R4
    AND R12, #7
    MOV R13, #7
    SUB R13, R12
    MOV R2, #1
    SLL R2, R13
    MOV R14, #0FFH
    XOR R14, R2
    MOV R3, #0
    ST R3, 61495
    L R3, [ER0]
    AND R3, R14
    ST R3, [ER0]
    MOV R3, #4
    ST R3, 61495
    L R3, [ER0]
    AND R3, R14
    ST R3, [ER0]
    RT

rt_fill_rect:
    PUSH LR
    MOV R8, R4
    MOV R9, R5
    MOV R10, #0
rt_fr_row:
    CMP R10, R6
    BGE rt_fr_rows_done
    MOV R11, #0
rt_fr_col:
    CMP R11, R7
    BGE rt_fr_cols_done
    MOV R4, R8
    ADD R4, R11
    MOV R5, R9
    ADD R5, R10
    BL rt_plot_pixel
    ADD R11, #1
    B rt_fr_col
rt_fr_cols_done:
    ADD R10, #1
    B rt_fr_row
rt_fr_rows_done:
    POP LR
    RT

rt_clear_rect:
    PUSH LR
    MOV R8, R4
    MOV R9, R5
    MOV R10, #0
rt_cr_row:
    CMP R10, R6
    BGE rt_cr_rows_done
    MOV R11, #0
rt_cr_col:
    CMP R11, R7
    BGE rt_cr_cols_done
    MOV R4, R8
    ADD R4, R11
    MOV R5, R9
    ADD R5, R10
    BL rt_clear_pixel
    ADD R11, #1
    B rt_cr_col
rt_cr_cols_done:
    ADD R10, #1
    B rt_cr_row
rt_cr_rows_done:
    POP LR
    RT

rt_fill_circle:
    PUSH LR
    MOV R8, R4
    MOV R9, R5
    MOV R10, R6
    MOV R11, #0
    MOV R15, #1
    SUB R15, R6
rt_fill_circle_loop:
    CMP R10, R11
    BLTS rt_fill_circle_done
    MOV R4, R8
    ADD R4, R10
    MOV R5, R9
    ADD R5, R11
    BL rt_plot_pixel
    MOV R4, R8
    ADD R4, R11
    MOV R5, R9
    ADD R5, R10
    BL rt_plot_pixel
    MOV R4, R8
    SUB R4, R11
    MOV R5, R9
    ADD R5, R10
    BL rt_plot_pixel
    MOV R4, R8
    SUB R4, R10
    MOV R5, R9
    ADD R5, R11
    BL rt_plot_pixel
    MOV R4, R8
    SUB R4, R10
    MOV R5, R9
    SUB R5, R11
    BL rt_plot_pixel
    MOV R4, R8
    SUB R4, R11
    MOV R5, R9
    SUB R5, R10
    BL rt_plot_pixel
    MOV R4, R8
    ADD R4, R11
    MOV R5, R9
    SUB R5, R10
    BL rt_plot_pixel
    MOV R4, R8
    ADD R4, R10
    MOV R5, R9
    SUB R5, R11
    BL rt_plot_pixel
    ADD R11, #1
    CMP R15, #0
    BGES rt_fill_circle_else
    MOV R0, R11
    SLL R0, #1
    ADD R0, #1
    ADD R15, R0
    B rt_fill_circle_cont
rt_fill_circle_else:
    ADD R10, #-1
    MOV R0, R11
    SUB R0, R10
    SLL R0, #1
    ADD R0, #1
    ADD R15, R0
rt_fill_circle_cont:
    B rt_fill_circle_loop
rt_fill_circle_done:
    POP LR
    RT

rt_clear_circle:
    PUSH LR
    MOV R8, R4
    MOV R9, R5
    MOV R10, R6
    MOV R11, #0
    MOV R15, #1
    SUB R15, R6
rt_clear_circle_loop:
    CMP R10, R11
    BLTS rt_clear_circle_done
    MOV R4, R8
    ADD R4, R10
    MOV R5, R9
    ADD R5, R11
    BL rt_clear_pixel
    MOV R4, R8
    ADD R4, R11
    MOV R5, R9
    ADD R5, R10
    BL rt_clear_pixel
    MOV R4, R8
    SUB R4, R11
    MOV R5, R9
    ADD R5, R10
    BL rt_clear_pixel
    MOV R4, R8
    SUB R4, R10
    MOV R5, R9
    ADD R5, R11
    BL rt_clear_pixel
    MOV R4, R8
    SUB R4, R10
    MOV R5, R9
    SUB R5, R11
    BL rt_clear_pixel
    MOV R4, R8
    SUB R4, R11
    MOV R5, R9
    SUB R5, R10
    BL rt_clear_pixel
    MOV R4, R8
    ADD R4, R11
    MOV R5, R9
    SUB R5, R10
    BL rt_clear_pixel
    MOV R4, R8
    ADD R4, R10
    MOV R5, R9
    SUB R5, R11
    BL rt_clear_pixel
    ADD R11, #1
    CMP R15, #0
    BGES rt_clear_circle_else
    MOV R0, R11
    SLL R0, #1
    ADD R0, #1
    ADD R15, R0
    B rt_clear_circle_cont
rt_clear_circle_else:
    ADD R10, #-1
    MOV R0, R11
    SUB R0, R10
    SLL R0, #1
    ADD R0, #1
    ADD R15, R0
rt_clear_circle_cont:
    B rt_clear_circle_loop
rt_clear_circle_done:
    POP LR
    RT

; ==========================================================================
; rt_scan_key - quet ma tran ban phim, dung DUNG dia chi SFR tu libcw.h
; (KeyboardOut=0xF046, KeyboardIn=0xF040) va DUNG thuat toan CheckButtons()
; trong libcw.c - da chay that tren CW/CWX (chip ML620909), khong doan so.
;
; Thuat toan (giu y nguyen logic goc, dich sang asm):
;   for x = 0x80 xuong 0x01 (dich phai moi vong), x != 0:
;       ST x -> KeyboardOut (0xF046)   ; chon cot dang quet
;       for y = 0x80 xuong 0x01 (dich phai moi vong), y != 0:
;           L KeyboardIn (0xF040)      ; doc hang
;           neu (KeyboardIn AND y) == 0 -> phim tai vi tri nay dang nhan
;               tra ve i (chi so bit, 0-63) trong R0
;           i += 1
;   het vong -> khong co phim nao nhan, tra ve 0xFF trong R0
;
; KHONG lam debounce/lastbutton nhu ban goc (ban goc dung cho polling lien
; tuc moi frame va chi tra phim MOI - o day tra RAW state moi lan goi, vi
; day la ham dung cho dieu kien if/wh, goi lai lien tuc trong vong wh se
; tu nhien co hanh vi tuong duong. Neu can debounce kieu "chi 1 lan nhan",
; goi rt_scan_key roi tu so sanh voi bien luu tu truoc trong code .pymini).
;
; Vao:  khong co tham so
; Ra:   R0 = ma phim (0-63) neu dang nhan, hoac 0xFF neu khong phim nao
; Dung: R0-R3 lam thanh ghi tam (giu dung quy uoc bieu thuc R0-R3 o dau
;       file nay - AN TOAN goi tu gen_expr/gen_cond_branch)
; ==========================================================================

rt_scan_key:
    MOV R1, #80H         ; R1 = x, cot dang quet, bat dau tu 0x80
    MOV R3, #0            ; R3 = i, chi so bit tich luy (0-63)
rt_sk_col_loop:
    CMP R1, #0
    BEQ rt_sk_none
    MOV R0, R1
    ST R0, 0F046H         ; KeyboardOut = x
    MOV R2, #80H          ; R2 = y, hang dang do, bat dau tu 0x80
rt_sk_row_loop:
    CMP R2, #0
    BEQ rt_sk_col_next
    L R0, 0F040H          ; R0 = KeyboardIn
    AND R0, R2             ; R0 = KeyboardIn & y
    CMP R0, #0
    BEQ rt_sk_found        ; bit = 0 nghia la phim dang nhan (active-low)
    ADD R3, #1
    SRL R2, #1             ; y >>= 1
    B rt_sk_row_loop
rt_sk_col_next:
    SRL R1, #1             ; x >>= 1
    B rt_sk_col_loop
rt_sk_found:
    MOV R0, R3
    RT
rt_sk_none:
    MOV R0, #0FFH
    RT

; ==========================================================================
; rt_wait_ms - cho X tick Timer0, dung THAT Timer0 (KHONG con vong lap dem
; tay doan chu ky lenh). Cau hinh Timer0Control=0x0101 LAY Y NGUYEN tu ham
; __delay() that trong libcw.c (da chay tren CW/CWX, ML620909 xac nhan qua
; comment RTC trong libcw.h). TICKS_PER_MS=8 cung lay tu libcw.h - DO THAT,
; khong doan chu ky/tan so xung he thong.
;
; KHAC voi __delay() goc: ban goc dung STOP mode + ngat Timer0 (tat loi CPU
; cho toi khi ngat xay ra) - CHUA lam vi bang vector ngat trong boot_full.asm
; hien dang route MOI nguon ngat ve chung 1 nhan L_INT (RTI ngay, khong phan
; biet nguon) - can sua rieng bang vector de STOP mode hoat dong dung, pham
; vi ngoai yeu cau nay. O day dung POLLING: bat Timer0 chay, doc lien tuc
; Timer0Counter cho toi khi >= gia tri da nap - CPU khong ngu nhung tick
; rate van CHINH XAC vi la dong ho phan cung that, khong phai dem lenh.
;
; Vao:  R4:R5 = so tick can cho (16-bit, R4=byte thap, R5=byte cao)
;       (goi tu compile_call: ticks = ms * 8, TICKS_PER_MS that)
; Ra:   khong co
; Dung: R0-R3 (giu dung quy uoc bieu thuc), R6-R7 lam thanh ghi tam rieng
; ==========================================================================

rt_wait_ms:
    PUSH LR
    DI
    MOV ER6, ER4           ; ER6 = so tick can cho (giu qua loi goi ST/L)
    MOV ER0, #01H
    ST ER0, 0F024H          ; Timer0Control = 0x0001 (E=0, CS0=1 - tat truoc)
    MOV ER0, #00H
    ST ER0, 0F022H          ; Timer0Counter = 0 (16-bit, 1 lan ghi)
    ST ER6, 0F020H          ; Timer0Interval = so tick (16-bit, 1 lan ghi)
    MOV R0, #01H
    ST R0, 0F025H            ; Timer0Control1: E=1 (bat timer chay)
    EI
rt_wm_poll:
    L ER0, 0F022H            ; doc Timer0Counter (16-bit, 1 lan doc)
    CMP ER0, ER6
    BLTS rt_wm_poll
    DI
    MOV R0, #00H
    ST R0, 0F025H            ; Timer0Control1: E=0 (tat timer)
    EI
    POP LR
    RT

; ==========================================================================
; rt_line_draw / rt_line_clear - ve/xoa duong thang luc CHAY bang Bresenham
; (cung thuat toan gen_line() tinh luc compile, nhung ho tro toa do BIEN).
;
; Vao:  R4=x1, R5=y1, R6=x2, R7=y2   (toa do 0-255, so sanh KHONG dau)
;
; QUY UOC THANH GHI - da kiem chung bang mo phong:
;   rt_plot_pixel/rt_clear_pixel GHI DE R0-R3 va R12-R15, nhung KHONG dung
;   toi R4-R11. Nen trang thai song qua BL chi duoc nam o R4-R11 hoac RAM:
;     R8=x hien tai  R9=y hien tai  R10=x2  R11=y2  R6=che do (1 ve, 0 xoa)
;     RAM: @LN_SX@ @LN_SY@ (buoc +1/-1), @LN_DX@ (dx>=0, 16-bit),
;          @LN_DY@ (dy<=0, 16-bit co dau), @LN_ERR@ (sai so, 16-bit co dau)
;   err/dx/dy DUNG 16-bit co dau vi dx co the toi 191 (>127 la tran 8-bit).
;   Cac ten bao trong dau @ duoc pymini2 thay bang dia chi RAM that luc ghep file
;   (KHONG dung DB o day: DB nam trong ROM, ghi vao do bi bo qua).
; ==========================================================================

rt_line_draw:
    PUSH LR
    MOV R0, #1
    B rt_ln_setup
rt_line_clear:
    PUSH LR
    MOV R0, #0
rt_ln_setup:
    MOV R8, R4
    MOV R9, R5
    MOV R10, R6
    MOV R11, R7
    MOV R6, R0                 ; R6 = che do
    ; ---- dx = |x2-x1|, sx ----
    MOV R0, R10
    SUB R0, R8                 ; R0 = x2-x1
    MOV R1, #1                 ; sx = +1
    CMP R10, R8                ; x2 >= x1 (khong dau) ?
    BGE rt_ln_dx_pos
    MOV R1, #0FFH              ; sx = -1
    MOV R2, #0
    SUB R2, R0
    MOV R0, R2                 ; R0 = x1-x2
rt_ln_dx_pos:
    ST R1, @LN_SX@
    MOV R1, #0
    ST ER0, @LN_DX@            ; dx 16-bit (R0 thap, R1=0 cao)
    ; ---- dy = -|y2-y1|, sy ----
    MOV R0, R11
    SUB R0, R9                 ; R0 = y2-y1
    MOV R1, #1                 ; sy = +1
    CMP R11, R9                ; y2 >= y1 (khong dau) ?
    BGE rt_ln_dy_pos
    MOV R1, #0FFH              ; sy = -1
    MOV R2, #0
    SUB R2, R0
    MOV R0, R2                 ; R0 = y1-y2
rt_ln_dy_pos:
    ST R1, @LN_SY@
    MOV R2, #0
    SUB R2, R0                 ; R2 = -|dy| (byte thap)
    MOV R3, #0
    CMP R0, #0
    BEQ rt_ln_dy_zero
    MOV R3, #0FFH              ; mo rong dau: -|dy| < 0 -> byte cao 0xFF
rt_ln_dy_zero:
    ST ER2, @LN_DY@            ; dy 16-bit co dau
    L ER0, @LN_DX@
    ADD ER0, ER2               ; err = dx + dy
    ST ER0, @LN_ERR@
rt_ln_loop:
    MOV R4, R8
    MOV R5, R9
    CMP R6, #0
    BEQ rt_ln_clr
    BL rt_plot_pixel
    B rt_ln_after
rt_ln_clr:
    BL rt_clear_pixel
rt_ln_after:
    CMP R8, R10
    BNE rt_ln_step
    CMP R9, R11
    BEQ rt_ln_done
rt_ln_step:
    L ER0, @LN_ERR@            ; ER0 = err
    MOV ER2, ER0
    ADD ER2, ER0               ; ER2 = e2 = 2*err  (GIU NGUYEN cho ca 2 dieu kien)
    L ER12, @LN_DY@
    CMP ER2, ER12              ; e2 >= dy ?
    BLTS rt_ln_no_x
    ADD ER0, ER12              ; err += dy
    L R4, @LN_SX@
    ADD R8, R4                 ; x += sx
rt_ln_no_x:
    L ER14, @LN_DX@
    CMP ER2, ER14              ; e2 <= dx ?
    BGTS rt_ln_no_y
    ADD ER0, ER14              ; err += dx
    L R4, @LN_SY@
    ADD R9, R4                 ; y += sy
rt_ln_no_y:
    ST ER0, @LN_ERR@
    B rt_ln_loop
rt_ln_done:
    POP LR
    RT
