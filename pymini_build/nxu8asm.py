#!/usr/bin/env python3
"""
nxu8asm.py - Assembler tu viet cho kien truc nX-U8/100 (Casio ClassWiz/CWX,
ROHM/LAPIS ML610/ML620 series), dua tren du lieu ma hoa opcode chinh thuc
trich xuat tu "nX-U8/100 Core Instruction Manual" (OKI Semiconductor, 2008),
Chuong 3 va Chuong 4 (Appendix).

KHONG can Lapis / Lexide Omega IDE de build - chi can Python 3 (khong thu
vien ngoai).

Vi du cu phap nguon:

        ORG     0x1000
    start:
        MOV     R0, #1
        MOV     R1, R0
        ADD     ER0, #4
    loop:
        CMP     R0, #10
        BLT     loop
        L       R2, [ER0]
        ST      R2, 16[ER4]        ; Disp16[ERm]: so truoc dau [
        PUSH    LR, EPSW
        B       start
        NOP

Chay:   python3 nxu8asm.py chuong_trinh.asm -o out.bin
"""

import re
import sys
import argparse

# --------------------------------------------------------------------------
# 1. BANG MA HOA LENH
#    Trich xuat tu Chuong 3 va Chuong 4 (Appendix) cua Instruction Manual.
#    template = chuoi 16 ky tu cho tu dau tien (bat buoc), va tu thu hai
#    (16 ky tu, hoac None neu lenh chi co 1 tu).
#    Chu cai lam placeholder (do dai truong = so lan xuat hien lien tiep):
#       n, m  : truong thanh ghi toan hang 1 / 2
#       i     : immediate
#       r     : Radr (offset tuong doi da chia 2)
#       w     : width
#       b     : bit_offset (3 bit)
#       g     : segment cua Cadr (4 bit cao, o tu dau)
#       D     : displacement / dia chi (Disp6 nhung tu dau, hoac 16-bit o
#               tu thu hai)
#       C     : 16-bit thap cua Cadr, o tu thu hai
#       L     : nibble danh sach thanh ghi PUSH/POP (da tinh san thanh 1
#               gia tri 4-bit truoc khi dua vao encoder)
# --------------------------------------------------------------------------

INSTR_TABLE = [
    # --- Arithmetic ---
    ("ADD",  ("Rn", "Rm"),        "1000nnnnmmmm0001", None),
    ("ADD",  ("Rn", "imm8"),      "0001nnnniiiiiiii", None),
    ("ADD",  ("ERn", "ERm"),      "1111nnn0mmm00110", None),
    ("ADD",  ("ERn", "imm7"),     "1110nnn01iiiiiii", None),
    ("ADDC", ("Rn", "Rm"),        "1000nnnnmmmm0110", None),
    ("ADDC", ("Rn", "imm8"),      "0110nnnniiiiiiii", None),
    ("AND",  ("Rn", "Rm"),        "1000nnnnmmmm0010", None),
    ("AND",  ("Rn", "imm8"),      "0010nnnniiiiiiii", None),
    ("CMP",  ("Rn", "Rm"),        "1000nnnnmmmm0111", None),
    ("CMP",  ("Rn", "imm8"),      "0111nnnniiiiiiii", None),
    ("CMPC", ("Rn", "Rm"),        "1000nnnnmmmm0101", None),
    ("CMPC", ("Rn", "imm8"),      "0101nnnniiiiiiii", None),
    ("MOV",  ("ERn", "ERm"),      "1111nnn0mmm00101", None),
    ("MOV",  ("ERn", "imm7"),     "1110nnn00iiiiiii", None),
    ("MOV",  ("Rn", "Rm"),        "1000nnnnmmmm0000", None),
    ("MOV",  ("Rn", "imm8"),      "0000nnnniiiiiiii", None),
    ("OR",   ("Rn", "Rm"),        "1000nnnnmmmm0011", None),
    ("OR",   ("Rn", "imm8"),      "0011nnnniiiiiiii", None),
    ("XOR",  ("Rn", "Rm"),        "1000nnnnmmmm0100", None),
    ("XOR",  ("Rn", "imm8"),      "0100nnnniiiiiiii", None),
    ("CMP",  ("ERn", "ERm"),      "1111nnn0mmm00111", None),
    ("SUB",  ("Rn", "Rm"),        "1000nnnnmmmm1000", None),
    ("SUBC", ("Rn", "Rm"),        "1000nnnnmmmm1001", None),

    # --- Shift ---
    ("SLL",  ("Rn", "Rm"),        "1000nnnnmmmm1010", None),
    ("SLL",  ("Rn", "width"),     "1001nnnn0www1010", None),
    ("SLLC", ("Rn", "Rm"),        "1000nnnnmmmm1011", None),
    ("SLLC", ("Rn", "width"),     "1001nnnn0www1011", None),
    ("SRA",  ("Rn", "Rm"),        "1000nnnnmmmm1110", None),
    ("SRA",  ("Rn", "width"),     "1001nnnn0www1110", None),
    ("SRL",  ("Rn", "Rm"),        "1000nnnnmmmm1100", None),
    ("SRL",  ("Rn", "width"),     "1001nnnn0www1100", None),
    ("SRLC", ("Rn", "Rm"),        "1000nnnnmmmm1101", None),
    ("SRLC", ("Rn", "width"),     "1001nnnn0www1101", None),

    # --- Load ---
    ("L", ("ERn", "EA"),        "1001nnn000110010", None),
    ("L", ("ERn", "EAinc"),     "1001nnn001010010", None),
    ("L", ("ERn", "ERm_ind"),   "1001nnn0mmm00010", None),
    ("L", ("ERn", "Disp16"),    "1010nnn0mmm01000", "DDDDDDDDDDDDDDDD"),
    ("L", ("ERn", "Disp6BP"),   "1011nnn000DDDDDD", None),
    ("L", ("ERn", "Disp6FP"),   "1011nnn001DDDDDD", None),
    ("L", ("ERn", "Dadr"),      "1001nnn000010010", "DDDDDDDDDDDDDDDD"),
    ("L", ("Rn", "EA"),         "1001nnnn00110000", None),
    ("L", ("Rn", "EAinc"),      "1001nnnn01010000", None),
    ("L", ("Rn", "ERm_ind"),    "1001nnnnmmm00000", None),
    ("L", ("Rn", "Disp16"),     "1001nnnnmmm01000", "DDDDDDDDDDDDDDDD"),
    ("L", ("Rn", "Disp6BP"),    "1101nnnn00DDDDDD", None),
    ("L", ("Rn", "Disp6FP"),    "1101nnnn01DDDDDD", None),
    ("L", ("Rn", "Dadr"),       "1001nnnn00010000", "DDDDDDDDDDDDDDDD"),
    ("L", ("XRn", "EA"),        "1001nn0000110100", None),
    ("L", ("XRn", "EAinc"),     "1001nn0001010100", None),
    ("L", ("QRn", "EA"),        "1001n00000110110", None),
    ("L", ("QRn", "EAinc"),     "1001n00001010110", None),

    # --- Store ---
    ("ST", ("ERn", "EA"),       "1001nnn000110011", None),
    ("ST", ("ERn", "EAinc"),    "1001nnn001010011", None),
    ("ST", ("ERn", "ERm_ind"),  "1001nnn0mmm00011", None),
    ("ST", ("ERn", "Disp16"),   "1010nnn0mmm01001", "DDDDDDDDDDDDDDDD"),
    ("ST", ("ERn", "Disp6BP"),  "1011nnn010DDDDDD", None),
    ("ST", ("ERn", "Disp6FP"),  "1011nnn011DDDDDD", None),
    ("ST", ("ERn", "Dadr"),     "1001nnn000010011", "DDDDDDDDDDDDDDDD"),
    ("ST", ("Rn", "EA"),        "1001nnnn00110001", None),
    ("ST", ("Rn", "EAinc"),     "1001nnnn01010001", None),
    ("ST", ("Rn", "ERm_ind"),   "1001nnnnmmm00001", None),
    ("ST", ("Rn", "Disp16"),    "1001nnnnmmm01001", "DDDDDDDDDDDDDDDD"),
    ("ST", ("Rn", "Disp6BP"),   "1101nnnn10DDDDDD", None),
    ("ST", ("Rn", "Disp6FP"),   "1101nnnn11DDDDDD", None),
    ("ST", ("Rn", "Dadr"),      "1001nnnn00010001", "DDDDDDDDDDDDDDDD"),
    ("ST", ("XRn", "EA"),       "1001nn0000110101", None),
    ("ST", ("XRn", "EAinc"),    "1001nn0001010101", None),
    ("ST", ("QRn", "EA"),       "1001n00000110111", None),
    ("ST", ("QRn", "EAinc"),    "1001n00001010111", None),

    # --- Control Register Access ---
    ("ADD", ("SP", "signed8"),    "11100001iiiiiiii", None),
    ("MOV", ("ECSR", "Rm"),       "10100000mmmm1111", None),
    ("MOV", ("ELR", "ERm"),       "1010mmm000001101", None),
    ("MOV", ("EPSW", "Rm"),       "10100000mmmm1100", None),
    ("MOV", ("ERn", "ELR"),       "1010nnn000000101", None),
    ("MOV", ("ERn", "SP"),        "1010nnn000011010", None),
    ("MOV", ("PSW", "Rm"),        "10100000mmmm1011", None),
    ("MOV", ("PSW", "unsigned8"), "11101001iiiiiiii", None),
    ("MOV", ("Rn", "ECSR"),       "1010nnnn00000111", None),
    ("MOV", ("Rn", "EPSW"),       "1010nnnn00000100", None),
    ("MOV", ("Rn", "PSW"),        "1010nnnn00000011", None),
    ("MOV", ("SP", "ERm"),        "10100001mmm01010", None),

    # --- EA register transfer ---
    ("LEA", ("ERm_ind",),  "11110000mmm01010", None),
    ("LEA", ("Disp16",),   "11110000mmm01011", "DDDDDDDDDDDDDDDD"),
    ("LEA", ("Dadr",),     "1111000000001100", "DDDDDDDDDDDDDDDD"),

    # --- ALU ---
    ("DAA", ("Rn",), "1000nnnn00011111", None),
    ("DAS", ("Rn",), "1000nnnn00111111", None),
    ("NEG", ("Rn",), "1000nnnn01011111", None),

    # --- Bit Access ---
    ("SB", ("Rn_bit",),   "1010nnnn0bbb0000", None),
    ("SB", ("Dbitadr",),  "101000001bbb0000", "DDDDDDDDDDDDDDDD"),
    ("RB", ("Rn_bit",),   "1010nnnn0bbb0010", None),
    ("RB", ("Dbitadr",),  "101000001bbb0010", "DDDDDDDDDDDDDDDD"),
    ("TB", ("Rn_bit",),   "1010nnnn0bbb0001", None),
    ("TB", ("Dbitadr",),  "101000001bbb0001", "DDDDDDDDDDDDDDDD"),

    # --- PSW Access ---
    ("EI",   (), "1110110100001000", None),
    ("DI",   (), "1110101111110111", None),
    ("SC",   (), "1110110110000000", None),
    ("RC",   (), "1110101101111111", None),
    ("CPLC", (), "1111111011001111", None),

    # --- Sign extension (n-field xuat hien 2 lan, encoder xu ly rieng) ---
    ("EXTBW", ("ERn",), "1000nnn1nnn01111", None),

    # --- Software interrupt ---
    ("SWI", ("snum",), "1110010100iiiiii", None),
    ("BRK", (),         "1111111111111111", None),

    # --- Branch ---
    ("B",  ("Cadr",),    "1111gggg00000000", "CCCCCCCCCCCCCCCC"),
    ("B",  ("ERn",),     "11110000nnn00010", None),
    ("BL", ("Cadr",),    "1111gggg00000001", "CCCCCCCCCCCCCCCC"),
    ("BL", ("ERn",),     "11110000nnn00011", None),

    # --- Conditional relative branch (mnemonic rieng cho tung dieu kien) ---
    ("BGE",  ("Radr",), "11000000rrrrrrrr", None),
    ("BLT",  ("Radr",), "11000001rrrrrrrr", None),
    ("BGT",  ("Radr",), "11000010rrrrrrrr", None),
    ("BLE",  ("Radr",), "11000011rrrrrrrr", None),
    ("BGES", ("Radr",), "11000100rrrrrrrr", None),
    ("BLTS", ("Radr",), "11000101rrrrrrrr", None),
    ("BGTS", ("Radr",), "11000110rrrrrrrr", None),
    ("BLES", ("Radr",), "11000111rrrrrrrr", None),
    ("BNE",  ("Radr",), "11001000rrrrrrrr", None),
    ("BEQ",  ("Radr",), "11001001rrrrrrrr", None),
    ("BNV",  ("Radr",), "11001010rrrrrrrr", None),
    ("BOV",  ("Radr",), "11001011rrrrrrrr", None),
    ("BPS",  ("Radr",), "11001100rrrrrrrr", None),
    ("BNS",  ("Radr",), "11001101rrrrrrrr", None),
    ("BAL",  ("Radr",), "11001110rrrrrrrr", None),

    # --- Multiplication / Division ---
    ("MUL", ("ERn", "Rm"), "1111nnn0mmmm0100", None),
    ("DIV", ("ERn", "Rm"), "1111nnn0mmmm1001", None),

    # --- Misc ---
    ("INC", ("EA",), "1111111000101111", None),
    ("DEC", ("EA",), "1111111000111111", None),
    ("RT",  (),      "1111111000011111", None),
    ("RTI", (),      "1111111000001111", None),
    ("NOP", (),      "1111111010001111", None),

    # --- PUSH / POP (thanh ghi don) ---
    ("PUSH", ("Rn",),  "1111nnnn01001110", None),
    ("PUSH", ("ERn",), "1111nnn001011110", None),
    ("PUSH", ("XRn",), "1111nn0001101110", None),
    ("PUSH", ("QRn",), "1111n00001111110", None),
    ("POP",  ("Rn",),  "1111nnnn00001110", None),
    ("POP",  ("ERn",), "1111nnn000011110", None),
    ("POP",  ("XRn",), "1111nn0000101110", None),
    ("POP",  ("QRn",), "1111n00000111110", None),

    # --- PUSH / POP (danh sach thanh ghi dieu khien: LR/EPSW/ELR/EA) ---
    ("PUSH", ("CtrlList",), "1111LLLL11001110", None),
    ("POP",  ("CtrlList",), "1111LLLL10001110", None),
]

# Dieu kien cho dang tong quat "BC cond,Radr" (dung chung mnemonic o tren)
COND_CODES = {
    "GE": "BGE", "NC": "BGE",
    "LT": "BLT", "CY": "BLT",
    "GT": "BGT",
    "LE": "BLE",
    "GES": "BGES",
    "LTS": "BLTS",
    "GTS": "BGTS",
    "LES": "BLES",
    "NE": "BNE", "NZ": "BNE",
    "EQ": "BEQ", "ZF": "BEQ",
    "NV": "BNV",
    "OV": "BOV",
    "PS": "BPS",
    "NS": "BNS",
    "AL": "BAL",
}

# PUSH/POP: anh xa ten thanh ghi dieu khien -> bit trong nibble "lepa"
#   bit3=LR bit2=EPSW bit1=ELR bit0=EA  (suy tu bang PUSH register_list
#   trong Instruction Manual: vi du LR,EPSW,ELR,EA = 1111B)
PUSHPOP_CTRL_BITS = {"EA": 0b0001, "ELR": 0b0010, "EPSW": 0b0100, "LR": 0b1000}


# --------------------------------------------------------------------------
# 2. GENERIC ENCODER: dien gia tri vao cac truong placeholder trong template
# --------------------------------------------------------------------------

def _fill_template(template, values):
    """
    template: chuoi 16 ky tu voi placeholder (vd 'n','m','i',...)
    values:   dict {ky_tu_placeholder: gia_tri_nguyen}
    Tra ve chuoi 16 bit '0'/'1' da dien du lieu.

    Neu mot ky tu xuat hien nhieu doan rieng biet (vd EXTBW co 'n' o 2
    cho khac nhau), CA HAI doan deu duoc dien cung mot gia tri (khong
    phai chia gia tri ra tung phan) - dung cho truong hop ma hoa lap
    lai thanh ghi de kiem tra/can chinh nhu trong manual.
    """
    chars = list(template)
    # gom nhom vi tri theo tung ky tu placeholder (bo qua '0'/'1')
    positions = {}
    for idx, ch in enumerate(chars):
        if ch in "01":
            continue
        positions.setdefault(ch, []).append(idx)

    for ch, idxs in positions.items():
        if ch not in values:
            raise ValueError(f"Thieu gia tri cho truong '{ch}' trong template {template}")
        val = values[ch]

        # tim cac "doan" (run) lien tiep trong idxs
        runs = []
        cur = [idxs[0]]
        for i in idxs[1:]:
            if i == cur[-1] + 1:
                cur.append(i)
            else:
                runs.append(cur)
                cur = [i]
        runs.append(cur)

        if len(runs) == 1:
            width = len(runs[0])
            mask = (1 << width) - 1
            if val < 0:
                val = val & mask  # so am da duoc bu 2 truoc khi goi ham nay
            bits = format(val & mask, f"0{width}b")
            for pos, b in zip(runs[0], bits):
                chars[pos] = b
        else:
            # nhieu doan rieng biet cung ky tu -> dien CUNG gia tri vao
            # MOI doan (vd EXTBW: thanh ghi lap lai 2 lan trong ma lenh)
            for run in runs:
                width = len(run)
                mask = (1 << width) - 1
                bits = format(val & mask, f"0{width}b")
                for pos, b in zip(run, bits):
                    chars[pos] = b

    if any(c not in "01" for c in chars):
        raise ValueError(f"Template chua dien het: {''.join(chars)}")
    return "".join(chars)


def _bits_to_word(bits16):
    return int(bits16, 2)


# --------------------------------------------------------------------------
# 3. PARSER TOAN HANG
# --------------------------------------------------------------------------

REG_R = re.compile(r"^R(1[0-5]|[0-9])$", re.IGNORECASE)
REG_ER = re.compile(r"^ER(1[0-4]|[0-9])$", re.IGNORECASE)
REG_XR = re.compile(r"^XR(0|4|8|12)$", re.IGNORECASE)
REG_QR = re.compile(r"^QR(0|8)$", re.IGNORECASE)

CTRL_KEYWORDS = {"PSW", "EPSW", "ECSR", "ELR", "LR", "SP", "EA"}


class Operand:
    """Ket qua phan tich mot toan hang trong dong lenh nguon."""
    def __init__(self, kind, value=None, extra=None):
        self.kind = kind      # 'Rn','ERn','XRn','QRn','imm','EA','EAinc',
                               # 'ERm_ind','Disp16','Disp6BP','Disp6FP',
                               # 'Dadr','Rn_bit','Dbitadr','PSW','EPSW',
                               # 'ECSR','ELR','SP','CtrlList','Cadr','Radr'
        self.value = value    # bieu thuc (string) hoac so nguyen da giai
        self.extra = extra    # gia tri phu (vd thanh ghi trong Disp16[ERm])

    def __repr__(self):
        return f"Operand({self.kind},{self.value},{self.extra})"


def _reg_num(tok):
    m = REG_R.match(tok)
    if m:
        return int(m.group(1))
    return None


def parse_operand(tok, evaluator):
    tok = tok.strip()
    if tok == "":
        return None

    # -- danh sach thanh ghi dieu khien PUSH/POP se duoc gop truoc khi goi
    #    ham nay (xu ly rieng trong assemble_line) --

    # -- immediate: #bieu_thuc --
    if tok.startswith("#"):
        return Operand("imm", tok[1:].strip())

    # -- thanh ghi bit: Rn.bit hoac bieu_thuc.bit --
    if "." in tok and "[" not in tok:
        left, right = tok.rsplit(".", 1)
        left = left.strip()
        rn = _reg_num(left)
        if rn is not None:
            return Operand("Rn_bit", right.strip(), extra=rn)
        return Operand("Dbitadr", right.strip(), extra=left)

    # -- dia chi/offset kem [ERn] hoac [EA] hoac [EA+] --
    if "[" in tok and tok.endswith("]"):
        pre, inside = tok.split("[", 1)
        inside = inside[:-1].strip()
        pre = pre.strip()
        if inside.upper() == "EA":
            if pre != "":
                raise ValueError(f"Cu phap khong hop le: {tok}")
            return Operand("EA")
        if inside.upper() == "EA+":
            return Operand("EAinc")
        erreg = REG_ER.match(inside.upper())
        if erreg and pre == "":
            return Operand("ERm_ind", extra=int(erreg.group(1)))
        if erreg and pre != "":
            return Operand("Disp16", pre, extra=int(erreg.group(1)))
        if inside.upper() == "BP" and pre != "":
            return Operand("Disp6BP", pre)
        if inside.upper() == "FP" and pre != "":
            return Operand("Disp6FP", pre)
        raise ValueError(f"Khong nhan dien duoc dang dia chi: {tok}")

    up = tok.upper()

    if up in CTRL_KEYWORDS:
        return Operand(up)

    rn = _reg_num(tok)
    if rn is not None:
        return Operand("Rn", extra=rn)

    m = REG_ER.match(up)
    if m:
        return Operand("ERn", extra=int(m.group(1)))
    m = REG_XR.match(up)
    if m:
        return Operand("XRn", extra=int(m.group(1)))
    m = REG_QR.match(up)
    if m:
        return Operand("QRn", extra=int(m.group(1)))

    # con lai: coi la bieu thuc (nhan/so) -> dung lam Dadr/Cadr/Radr tuy lenh
    return Operand("EXPR", tok)


# --------------------------------------------------------------------------
# 4. DOI CHIEU KIEU TOAN HANG <-> KIEU MONG DOI TRONG BANG LENH
# --------------------------------------------------------------------------

def _compatible(expected, op):
    if expected in ("Rn", "Rm"):
        return op.kind == "Rn"
    if expected in ("ERn", "ERm"):
        return op.kind == "ERn"
    if expected == "XRn":
        return op.kind == "XRn"
    if expected == "QRn":
        return op.kind == "QRn"
    if expected in ("imm8", "imm7", "width", "signed8", "unsigned8", "snum"):
        return op.kind == "imm"
    if expected == "EA":
        return op.kind == "EA"
    if expected == "EAinc":
        return op.kind == "EAinc"
    if expected == "ERm_ind":
        return op.kind == "ERm_ind"
    if expected == "Disp16":
        return op.kind == "Disp16"
    if expected == "Disp6BP":
        return op.kind == "Disp6BP"
    if expected == "Disp6FP":
        return op.kind == "Disp6FP"
    if expected in ("Dadr", "Cadr", "Radr"):
        return op.kind == "EXPR"
    if expected == "Rn_bit":
        return op.kind == "Rn_bit"
    if expected == "Dbitadr":
        return op.kind == "Dbitadr"
    if expected in ("PSW", "EPSW", "ECSR", "ELR", "SP"):
        return op.kind == expected
    if expected == "CtrlList":
        return op.kind == "CtrlList"
    return False


def _find_variant(mnemonic, expected_kinds_list, operands):
    for mnem, kinds, w1, w2 in INSTR_TABLE:
        if mnem != mnemonic or len(kinds) != len(operands):
            continue
        if all(_compatible(k, o) for k, o in zip(kinds, operands)):
            return kinds, w1, w2
    return None


def _reg_field_value(op):
    """Gia tri dua vao truong 'n'/'m' cua template, tuy loai thanh ghi."""
    if op.kind == "Rn":
        return op.extra               # 0..15, truong 4 bit
    if op.kind == "ERn":
        return op.extra // 2          # 0,2,..14 -> 0..7, truong 3 bit
    if op.kind == "XRn":
        return op.extra // 4          # 0,4,8,12 -> 0..3, truong 2 bit
    if op.kind == "QRn":
        return op.extra // 8          # 0,8 -> 0..1, truong 1 bit
    if op.kind == "ERm_ind":
        return op.extra // 2
    if op.kind == "Disp16":
        return op.extra // 2
    raise ValueError(f"Khong the lay truong thanh ghi tu {op}")


class AsmError(Exception):
    pass


class Assembler:
    def __init__(self):
        self.symtab = {}          # ten -> gia tri (int)
        self.lines = []           # danh sach dong da tien xu ly
        self.output = bytearray()
        self.origin = 0
        self.pc = 0

    # ---- bieu thuc: so hoc don gian + nhan da dinh nghia ----
    def eval_expr(self, expr, pass_no):
        expr = expr.strip()
        # thay the nhan bang gia tri (neu co) truoc khi eval bang Python
        def repl(m):
            name = m.group(0)
            if name.upper() in ("EA", "BP", "FP"):
                return name
            if name in self.symtab:
                return str(self.symtab[name])
            if pass_no == 1:
                return "0"     # pass 1: nhan chua chac da co, dung tam 0
            raise AsmError(f"Nhan chua duoc dinh nghia: {name}")

        # QUAN TRONG: doi so hex (0xNN hoac NNh) sang thap phan TRUOC KHI
        # thay the ten nhan/bien, neu khong hau to 'H'/'h' se bi nham la
        # mot nhan chua dinh nghia va lam hong so (vd "01H" -> "010").
        py_expr = re.sub(r"\b0[Xx][0-9A-Fa-f]+\b", lambda m: str(int(m.group(0), 16)), expr)
        py_expr = re.sub(r"\b([0-9A-Fa-f]+)[Hh]\b", lambda m: str(int(m.group(1), 16)), py_expr)
        py_expr = re.sub(r"[A-Za-z_$][A-Za-z0-9_$]*", repl, py_expr)
        try:
            return int(eval(py_expr, {"__builtins__": {}}, {}))
        except Exception as e:
            raise AsmError(f"Loi bieu thuc '{expr}': {e}")

    def encode_instruction(self, mnemonic, operands, pass_no):
        """Tra ve list cac tu 16-bit (1 hoac 2 phan tu)."""
        mnemonic = mnemonic.upper()

        # --- dang tong quat BC cond,Radr -> quy ve mnemonic Bxxx ---
        if mnemonic == "BC":
            cond_tok = operands[0].value if operands[0].kind == "EXPR" else None
            if cond_tok is None:
                raise AsmError("BC can dieu kien o toan hang dau (vd BC EQ,label)")
            real = COND_CODES.get(cond_tok.upper())
            if real is None:
                raise AsmError(f"Dieu kien khong hop le: {cond_tok}")
            mnemonic = real
            operands = operands[1:]

        # --- "POP PC" (cu phap Lapis) - LUU Y: lenh RT that su chi doc
        #     LR truc tiep (PC <- LR), KHONG doc tu stack (theo dung mo ta
        #     trong Instruction Manual). Vi vay "POP PC" phai la 2 lenh:
        #     POP LR (lay dia chi tra ve tu stack vao LR) roi RT (LR->PC).
        if mnemonic == "POP" and len(operands) == 1 and \
           operands[0].kind == "EXPR" and operands[0].value.upper() == "PC":
            pop_lr_bits = _fill_template("1111LLLL10001110", {"L": PUSHPOP_CTRL_BITS["LR"]})
            rt_bits = _fill_template("1111111000011111", {})
            return [_bits_to_word(pop_lr_bits), _bits_to_word(rt_bits)]

        # --- EXTBW: n xuat hien 2 lan, gia tri = so ERn/2 ---
        if mnemonic == "EXTBW":
            op = operands[0]
            if op.kind != "ERn":
                raise AsmError("EXTBW can toan hang ERn")
            values = {"n": op.extra // 2}
            bits = _fill_template("1000nnn1nnn01111", values)
            return [_bits_to_word(bits)]

        # --- PUSH / POP danh sach thanh ghi dieu khien ---
        if mnemonic in ("PUSH", "POP") and len(operands) >= 1 and \
           all(o.kind in CTRL_KEYWORDS or o.kind == "EXPR" for o in operands) and \
           any(o.kind in ("LR", "EPSW", "ELR", "EA") for o in operands):
            nib = 0
            for o in operands:
                if o.kind not in PUSHPOP_CTRL_BITS:
                    raise AsmError(f"Thanh ghi khong hop le trong PUSH/POP list: {o.kind}")
                nib |= PUSHPOP_CTRL_BITS[o.kind]
            template = "1111LLLL11001110" if mnemonic == "PUSH" else "1111LLLL10001110"
            bits = _fill_template(template, {"L": nib})
            return [_bits_to_word(bits)]

        found = _find_variant(mnemonic, None, operands)
        if found is None:
            raise AsmError(f"Khong tim thay dang lenh phu hop: {mnemonic} {[o.kind for o in operands]}")
        kinds, w1, w2 = found

        values = {}
        second_word_val = None

        for kind, op in zip(kinds, operands):
            if kind in ("Rn", "ERn", "XRn", "QRn"):
                values["n"] = _reg_field_value(op)
            elif kind in ("Rm", "ERm", "XRm", "QRm"):
                values["m"] = _reg_field_value(op)
            elif kind in ("imm8", "imm7", "signed8", "unsigned8", "snum"):
                values["i"] = self.eval_expr(op.value, pass_no)
            elif kind == "width":
                values["w"] = self.eval_expr(op.value, pass_no)
            elif kind == "ERm_ind":
                values["m"] = _reg_field_value(op)
            elif kind == "Disp16":
                values["m"] = _reg_field_value(op)
                second_word_val = self.eval_expr(op.value, pass_no)
            elif kind in ("Disp6BP", "Disp6FP"):
                values["D"] = self.eval_expr(op.value, pass_no)
            elif kind == "Dadr":
                second_word_val = self.eval_expr(op.value, pass_no)
            elif kind == "Rn_bit":
                values["n"] = op.extra
                values["b"] = self.eval_expr(op.value, pass_no)
            elif kind == "Dbitadr":
                values["b"] = self.eval_expr(op.value, pass_no)
                second_word_val = self.eval_expr(op.extra, pass_no)
            elif kind == "Cadr":
                addr = self.eval_expr(op.value, pass_no)
                values["g"] = (addr >> 16) & 0xF
                second_word_val = addr & 0xFFFF
            elif kind == "Radr":
                target = self.eval_expr(op.value, pass_no)
                next_pc = self.pc + 2
                values["r"] = ((target - next_pc) >> 1) & 0xFF
            elif kind in ("EA", "EAinc", "PSW", "EPSW", "ECSR", "ELR", "SP"):
                pass  # khong co truong so trong template, chi la dang co dinh
            else:
                raise AsmError(f"Chua ho tro kieu toan hang: {kind}")

        bits1 = _fill_template(w1, values)
        words = [_bits_to_word(bits1)]
        if w2 is not None:
            if second_word_val is None:
                second_word_val = 0
            values2 = {"D": second_word_val, "C": second_word_val}
            bits2 = _fill_template(w2, values2)
            words.append(_bits_to_word(bits2))
        return words

    # ---- tach toan hang, xu ly rieng danh sach PUSH/POP (co dau phay) ----
    def _split_operands(self, mnemonic, rest):
        rest = rest.strip()
        if rest == "":
            return []
        if mnemonic.upper() in ("PUSH", "POP"):
            names = [t.strip().upper() for t in rest.split(",")]
            if all(n in ("LR", "EPSW", "ELR", "EA") for n in names) and len(names) > 0 \
               and not any(REG_R.match(n) or REG_ER.match(n) or REG_XR.match(n) or REG_QR.match(n) for n in names):
                return [Operand(n) for n in names]
        # tach thong thuong theo dau phay o cap ngoai cung (khong nam trong [])
        parts = []
        depth = 0
        cur = ""
        for ch in rest:
            if ch == "[":
                depth += 1
            elif ch == "]":
                depth -= 1
            if ch == "," and depth == 0:
                parts.append(cur)
                cur = ""
            else:
                cur += ch
        parts.append(cur)
        return [parse_operand(p, self) for p in parts]

    def _process_line(self, raw_line, pass_no):
        line = raw_line.split(";", 1)[0].rstrip("\r\n")
        if line.strip() == "":
            return

        # nhan dang "ten:" o dau dong
        m = re.match(r"^\s*([A-Za-z_$][A-Za-z0-9_$]*)\s*:\s*(.*)$", line)
        label = None
        if m:
            label = m.group(1)
            line = m.group(2)

        if label is not None:
            if pass_no == 1:
                if label in self.symtab:
                    raise AsmError(f"Nhan bi trung: {label}")
                self.symtab[label] = self.pc
            else:
                pass

        line = line.strip()
        if line == "":
            return

        toks = line.split(None, 1)
        mnemonic = toks[0]
        rest = toks[1] if len(toks) > 1 else ""

        up = mnemonic.upper()

        if up == "ORG":
            addr = self.eval_expr(rest, pass_no)
            self.pc = addr
            if pass_no == 2:
                # dem khoang trong bang 0xFF (chua lap trinh) den vi tri moi
                while len(self.output) < addr:
                    self.output.append(0xFF)
            return

        if up == "EQU":
            raise AsmError("Dung dang 'TEN EQU bieu_thuc', khong dat EQU o dau dong")

        if up == "END":
            return

        # dang "TEN EQU bieu_thuc" da bi bat bang nhanh nhan ':' o tren,
        # ho tro them dang khong dau ':' : "TEN EQU bieu_thuc"
        m2 = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s+EQU\s+(.*)$", line, re.IGNORECASE)
        if m2:
            name, expr = m2.groups()
            if pass_no == 1:
                self.symtab[name] = self.eval_expr(expr, pass_no)
            return

        if up in ("DB", "DEFB"):
            vals = [self.eval_expr(v, pass_no) for v in rest.split(",")]
            if pass_no == 2:
                for v in vals:
                    self.output.append(v & 0xFF)
            self.pc += len(vals)
            return

        if up in ("DW", "DEFW"):
            vals = [self.eval_expr(v, pass_no) for v in rest.split(",")]
            if pass_no == 2:
                for v in vals:
                    self.output.append(v & 0xFF)
                    self.output.append((v >> 8) & 0xFF)
            self.pc += 2 * len(vals)
            return

        if up == "DS":
            n = self.eval_expr(rest, pass_no)
            if pass_no == 2:
                for _ in range(n):
                    self.output.append(0)
            self.pc += n
            return

        # --- lenh may thuc su ---
        operands = self._split_operands(mnemonic, rest)
        words = self.encode_instruction(up, operands, pass_no)

        if pass_no == 2:
            while len(self.output) < self.pc:
                self.output.append(0xFF)
            for w in words:
                self.output.append(w & 0xFF)          # little-endian
                self.output.append((w >> 8) & 0xFF)
        self.pc += 2 * len(words)

    def assemble(self, source_lines):
        # pass 1: tinh dia chi nhan
        self.pc = 0
        self.symtab = {}
        for raw in source_lines:
            self._process_line(raw, pass_no=1)

        # pass 2: sinh ma that
        self.pc = 0
        self.output = bytearray()
        for raw in source_lines:
            self._process_line(raw, pass_no=2)

        return bytes(self.output)


def main():
    ap = argparse.ArgumentParser(description="Assembler tu viet cho nX-U8/100")
    ap.add_argument("source", help="file .asm nguon")
    ap.add_argument("-o", "--output", default="out.bin", help="file nhi phan dau ra")
    args = ap.parse_args()

    with open(args.source, "r", encoding="utf-8") as f:
        lines = f.readlines()

    asm = Assembler()
    try:
        data = asm.assemble(lines)
    except AsmError as e:
        print(f"Loi assemble: {e}", file=sys.stderr)
        sys.exit(1)

    with open(args.output, "wb") as f:
        f.write(data)

    print(f"OK: {len(data)} byte -> {args.output}")


if __name__ == "__main__":
    main()
