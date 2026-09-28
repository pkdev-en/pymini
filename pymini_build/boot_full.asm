; ==========================================================================
; boot_full.asm - Toan bo chuong trinh cho ML620909, assemble bang chinh
; nxu8asm.py (KHONG dung Lapis/Lexide).
;
; Phan vector ngat + khoi dong (clock/LCD/watchdog) duoc CHUYEN THE tu
; ML620909.asm goc (file do Lapis sinh ra khi ban tao project moi trong
; Lexide) - giu nguyen logic, chi bo cac chi thi rieng cua Lapis
; (type/model/romwindow/extrn/public) vi assembler nay khong can chung
; (khong lien ket nhieu file .obj, chi xuat thang 1 file .bin).
; ==========================================================================

    ORG 0x0000

RESET_SP EQU 0F000h

; --- Bang vector ngat (21 word, dung dinh dang nhu ML620909.asm goc) ---
    DW RESET_SP
    DW start_up
    DW L_BRK
    DW L_INT
    DW L_INT
    DW L_INT
    DW L_INT
    DW L_INT
    DW L_INT
    DW L_INT
    DW L_INT
    DW L_INT
    DW L_INT
    DW L_INT
    DW L_INT
    DW L_INT
    DW L_INT
    DW L_INT
    DW L_INT
    DW L_INT
    DW L_INT

L_BRK:
    MOV PSW, #3
    BRK

L_INT:
    RTI

; --------------------------------------------------------------------
; helper_060EC: chuyen che do clock/port (chuyen the tu _060EC goc)
; --------------------------------------------------------------------
helper_060EC:
    PUSH LR
    MOV ER2, ER0
    TB 0F00AH.1
    BNE L074
L00A:
    DI
    MOV ER0, #01H
    ST ER0, 0F024H
    MOV ER0, #00H
    ST ER0, 0F022H
    ST ER2, 0F020H
    MOV R0, #01H
    ST R0, 0F025H
    MOV R0, #00H
    ST R0, 0F014H
    ST R0, 0F015H
    MOV R2, #50H
    MOV R3, #0A0H
    ST R2, 0F008H
    ST R3, 0F008H
    MOV R0, #02H
    ST R0, 0F009H
    NOP
    NOP
L044:
    L R0, 0F042H
    BNE L072
L04A:
    MOV ER0, #0FH
    ST ER0, 0F024H
    MOV ER0, #00H
    ST ER0, 0F022H
    MOV R0, #9EH
    MOV R1, #07H
    ST ER0, 0F020H
    MOV R0, #01H
    ST R0, 0F025H
    MOV R0, #00H
    ST R0, 0F014H
    ST R0, 0F015H
    EI
L072:
    POP PC
L074:
    RB 0F00AH.1
    BAL L00A

; --------------------------------------------------------------------
; start_up: diem vao dau tien sau reset (chuyen the tu $$start_up goc)
; --------------------------------------------------------------------
start_up:
    MOV R0, #00H
    ST R0, 0F000H
    B init_clock

; --------------------------------------------------------------------
; init_clock: khoi tao clock/timer (chuyen the tu _2F060 goc)
; --------------------------------------------------------------------
init_clock:
    L R0, 0F058H
    MOV R4, R0
    BL init_lcd
    MOV R0, #40H
    MOV R1, #06H
    BL helper_060EC
    MOV R0, #81H
    ST R0, 0F00AH
    MOV R0, #04H
    ST R0, 0F030H
    MOV R0, #03H
    ST R0, 0F033H
    MOV R0, #06H
    ST R0, 0F034H
    MOV R0, #17H
    ST R0, 0F035H
    MOV R0, #08H
    ST R0, 0F036H
    MOV R0, #00H
    ST R0, 0F039H
    MOV R0, #55H
    ST R0, 0F031H
    BL user_entry

; --------------------------------------------------------------------
; init_lcd: khoi tao LCD/port (chuyen the tu _3DEDE goc)
; --------------------------------------------------------------------
init_lcd:
    PUSH LR
    MOV R0, #31H
    ST R0, 0F00AH
    MOV R0, #0F7H
    ST R0, 0F028H
    MOV R0, #32H
LD010:
    ADD R0, #-1
    CMP R0, #00H
    BNE LD010
    MOV R0, #22H
    ST R0, 0F010H
    MOV R0, #00H
    ST R0, 0F011H
    ST R0, 0F012H
    MOV R0, #03H
    ST R0, 0F018H
    MOV R0, #00H
    ST R0, 0F058H
    MOV R0, #00H
    ST R0, 0F042H
    MOV R0, #07H
    ST R0, 0F03DH
    MOV R0, #0C8H
    MOV R1, #00H
LD02E:
    BL helper_060EC
    MOV R0, #04H
    ST R0, 0F030H
    MOV R0, #07H
    ST R0, 0F033H
    MOV R0, #06H
    ST R0, 0F034H
    MOV R0, #17H
    ST R0, 0F035H
    MOV R0, #08H
    ST R0, 0F036H
    MOV R0, #00H
    ST R0, 0F039H
    MOV R0, #57H
    ST R0, 0F031H
    MOV R0, #12H
    ST R0, 0F032H
    MOV R0, #00H
    ST R0, 0F220H
    MOV R0, #7FH
    ST R0, 0F221H
    MOV R0, #00H
    ST R0, 0F222H
    MOV R0, #7FH
    ST R0, 0F223H
    MOV R0, #00H
    ST R0, 0F224H
    ST R0, 0F225H
    MOV R0, #00H
    ST R0, 0F048H
    ST R0, 0F049H
    MOV R0, #07H
    ST R0, 0F04AH
    MOV R0, #00H
    ST R0, 0F04BH
    MOV R0, #07H
    ST R0, 0F04CH
    MOV R0, #00H
    ST R0, 0F04EH
    MOV R0, #00H
    ST R0, 0F041H
    MOV R0, #80H
    ST R0, 0F044H
    MOV R0, #0FFH
    ST R0, 0F045H
    MOV R2, #00H
    ST R2, 0F046H
    POP PC

; --------------------------------------------------------------------
; user_entry: THAY CHO "_entry: b _main" trong ban Lapis - nhay thang
; toi code cua ban (vd code do pymini sinh ra) thay vi goi mot ham C
; --------------------------------------------------------------------
user_entry:
; >>> DAN CODE DA SINH TU pymini.py (hello.gen.asm) VAO DAY <<<
    NOP
loop_forever:
    B loop_forever
