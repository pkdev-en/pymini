#!/usr/bin/env python3
"""
pymini2.py - Ban mo rong cua pymini.py, theo dung dac ta lang_spec.md.

MOI so voi pymini.py:
  - Bieu thuc toan hoc dung do uu tien nhu Python: * / truoc + -, co ngoac.
  - Tu khoa rieng: if / elf / eles / wh (thay elif/else/while).
  - circle(x,y,r) / rect(x,y,h,w) / line(x1,y1,x2,y2) / render(h,w,x,y,ten)
    - CHI HO TRO khi TAT CA toa do la SO CO DINH (hang so), vi duoc tinh
      san luc compile (giong y het cach da lam va TEST THANH CONG voi
      Hello + duong tron truoc do - khong doan mo, chi tai su dung dung
      cach da chay duoc tren may that).

CHUA LAM (se bao loi ro rang, khong lam lieu):
  - move()/moveto()/erase() - can dong co do hoa thoi gian thuc (tinh dia
    chi VRAM luc chay, khong phai luc compile) - CHUA VIET va CHUA TEST.
  - wait() - can dinh chuan may that (bao nhieu chu ky = 1ms) - CHUA CO.
  - key() - da tim dung thanh ghi that (KID/KOD0/KOCON0/KIMOD) nhung CHUA
    viet logic quet ma tran phim.
  - So thuc that cho phep chia (/) - hien tai se bao loi, KHONG lam
    chia nguyen ngam dinh vi ban da chon ro la muon so thuc that.
"""

import re
import sys
import subprocess
import os

DATA_BASE = 0x9000

SCREEN_BASE = 0xF800
ROW_STRIDE = 32
BUFSEL_SFR = 0xF037

FONT5X7 = {
    " ": [0x00, 0x00, 0x00, 0x00, 0x00],
    "!": [0x00, 0x00, 0x5F, 0x00, 0x00],
    ",": [0x00, 0x40, 0x30, 0x00, 0x00],
    "-": [0x08, 0x08, 0x08, 0x08, 0x08],
    ".": [0x00, 0x00, 0x20, 0x00, 0x00],
    ":": [0x00, 0x00, 0x12, 0x00, 0x00],
    "?": [0x02, 0x01, 0x51, 0x09, 0x06],
    "A": [0x7E, 0x08, 0x09, 0x08, 0x7E],
    "B": [0x7F, 0x49, 0x49, 0x49, 0x36],
    "C": [0x3E, 0x41, 0x41, 0x41, 0x41],
    "D": [0x7F, 0x41, 0x41, 0x41, 0x3E],
    "E": [0x7F, 0x49, 0x49, 0x49, 0x41],
    "F": [0x7F, 0x09, 0x09, 0x09, 0x01],
    "G": [0x3E, 0x41, 0x49, 0x49, 0x79],
    "H": [0x7F, 0x08, 0x08, 0x08, 0x7F],
    "I": [0x41, 0x41, 0x7F, 0x41, 0x41],
    "J": [0x20, 0x40, 0x41, 0x3F, 0x01],
    "K": [0x7F, 0x08, 0x14, 0x22, 0x41],
    "L": [0x7F, 0x40, 0x40, 0x40, 0x40],
    "M": [0x7F, 0x02, 0x04, 0x02, 0x7F],
    "N": [0x7F, 0x02, 0x04, 0x08, 0x7F],
    "O": [0x3E, 0x41, 0x41, 0x41, 0x3E],
    "P": [0x7F, 0x09, 0x09, 0x09, 0x06],
    "Q": [0x3E, 0x41, 0x51, 0x21, 0x5E],
    "R": [0x7F, 0x09, 0x19, 0x29, 0x46],
    "S": [0x46, 0x49, 0x49, 0x49, 0x31],
    "T": [0x01, 0x01, 0x7F, 0x01, 0x01],
    "U": [0x3F, 0x40, 0x40, 0x40, 0x3F],
    "V": [0x1F, 0x20, 0x40, 0x20, 0x1F],
    "W": [0x3F, 0x40, 0x38, 0x40, 0x3F],
    "X": [0x63, 0x14, 0x08, 0x14, 0x63],
    "Y": [0x03, 0x04, 0x78, 0x04, 0x03],
    "Z": [0x61, 0x51, 0x49, 0x45, 0x43],
    "e": [0x38, 0x54, 0x54, 0x54, 0x18],
    "l": [0x00, 0x41, 0x7F, 0x40, 0x00],
    "o": [0x38, 0x44, 0x44, 0x44, 0x38],
    "0": [0x3E, 0x51, 0x49, 0x45, 0x3E],
    "1": [0x00, 0x42, 0x7F, 0x40, 0x00],
    "2": [0x42, 0x61, 0x51, 0x49, 0x46],
    "3": [0x41, 0x41, 0x49, 0x4D, 0x32],
    "4": [0x18, 0x14, 0x12, 0x7F, 0x10],
    "5": [0x27, 0x45, 0x45, 0x45, 0x39],
    "6": [0x3C, 0x4A, 0x49, 0x49, 0x30],
    "7": [0x01, 0x71, 0x09, 0x05, 0x03],
    "8": [0x36, 0x49, 0x49, 0x49, 0x36],
    "9": [0x06, 0x09, 0x49, 0x69, 0x1E],
    "a": [0x20, 0x54, 0x54, 0x54, 0x78],
    "b": [0x7F, 0x48, 0x44, 0x44, 0x3C],
    "c": [0x38, 0x44, 0x44, 0x44, 0x44],
    "d": [0x38, 0x44, 0x44, 0x44, 0x7F],
    "f": [0x04, 0x7E, 0x05, 0x05, 0x00],
    "g": [0x18, 0x24, 0x24, 0x24, 0x7C],
    "h": [0x7F, 0x08, 0x04, 0x04, 0x7C],
    "i": [0x00, 0x00, 0x7D, 0x00, 0x00],
    "j": [0x20, 0x40, 0x40, 0x3D, 0x00],
    "k": [0x7F, 0x10, 0x28, 0x44, 0x00],
    "m": [0x7C, 0x04, 0x38, 0x04, 0x78],
    "n": [0x7C, 0x08, 0x04, 0x04, 0x7C],
    "p": [0x7C, 0x14, 0x14, 0x14, 0x08],
    "q": [0x08, 0x14, 0x14, 0x14, 0x7C],
    "r": [0x7C, 0x08, 0x04, 0x04, 0x0C],
    "s": [0x48, 0x54, 0x54, 0x54, 0x24],
    "t": [0x04, 0x3F, 0x44, 0x44, 0x20],
    "u": [0x3C, 0x40, 0x40, 0x20, 0x7C],
    "v": [0x1C, 0x20, 0x40, 0x20, 0x1C],
    "w": [0x3C, 0x40, 0x30, 0x40, 0x3C],
    "x": [0x44, 0x28, 0x10, 0x28, 0x44],
    "y": [0x0C, 0x50, 0x50, 0x50, 0x3C],
    "z": [0x44, 0x64, 0x54, 0x4C, 0x44],
}


# Bang tra ten phim -> ma quet, LAY NGUYEN tu enum BUTTON + SPECIAL_CHARS
# trong libcw.h (da chay that tren CW/CWX qua CheckButtons(), khong doan).
KEY_NAMES = {
    # So
    "0": 0x0b, "1": 0x3f, "2": 0x37, "3": 0x2f, "4": 0x3e,
    "5": 0x36, "6": 0x2e, "7": 0x3d, "8": 0x35, "9": 0x2d,
    # Chu (theo B_A..B_Z trong libcw.h - luu y mot so trung ma voi so,
    # vi ban phim vat ly dung phim SHIFT de doi nghia, khong phai loi)
    "A": 0x3c, "B": 0x34, "C": 0x2c, "D": 0x24, "E": 0x1c, "F": 0x14,
    "G": 0x3d, "H": 0x35, "I": 0x2d, "J": 0x25, "K": 0x1d,
    "L": 0x3e, "M": 0x36, "N": 0x2e, "O": 0x26, "P": 0x1e,
    "Q": 0x3f, "R": 0x37, "S": 0x2f, "T": 0x27, "U": 0x1f,
    "V": 0x0b, "W": 0x0c, "X": 0x0d, "Y": 0x0e, "Z": 0x0f,
    # Phim dac biet (SPECIAL_CHARS trong libcw.h)
    "HOME": 0x30, "UP": 0x20, "PGUP": 0x10, "SETTINGS": 0x39,
    "BACK": 0x31, "LEFT": 0x29, "OK": 0x21, "RIGHT": 0x19,
    "PGDOWN": 0x11, "SHIFT": 0x3A, "VAR": 0x32, "FUNC": 0x2A,
    "DOWN": 0x22, "CATALOG": 0x1A, "TOOLS": 0x12, "X": 0x3B,
    "FRAC": 0x33, "SQRT": 0x2B, "POWER": 0x23, "SQUARED": 0x1B,
    "LOGAB": 0x13, "ANS": 0x3C, "SIN": 0x34, "COS": 0x2C, "TAN": 0x24,
    "LEFT_PAREN": 0x1C, "RIGHT_PAREN": 0x14, "DEL": 0x25, "AC": 0x1D,
    "MUL": 0x26, "DIV": 0x1E, "PLUS": 0x27, "MINUS": 0x1F,
    "DOT": 0x0C, "SCI": 0x0D, "FORMAT": 0x0E, "EXE": 0x0F,
    "NONE": 0xFF,   # khong phim nao dang nhan (gia tri tra ve khi rong)
}


class CompileError(Exception):
    pass


def _pixel_addr_bit(x, y):
    if not (0 <= x < 192 and 0 <= y < 64):
        raise CompileError(f"Toa do ({x},{y}) nam ngoai man hinh (192x64)")
    addr = SCREEN_BASE + y * ROW_STRIDE + (x >> 3)
    bit = 7 - (x & 7)
    return addr, bit


# --------------------------------------------------------------------
# 1. TOKENIZE THEO KHOI THUT DAU DONG
# --------------------------------------------------------------------

class Node:
    def __init__(self, kind, **kw):
        self.kind = kind
        self.__dict__.update(kw)

    def __repr__(self):
        return f"<{self.kind} {self.__dict__}>"


def tokenize_lines(src):
    out = []
    for raw in src.splitlines():
        line = raw.split(";", 1)[0].rstrip()
        if line.strip() == "":
            continue
        indent = len(line) - len(line.lstrip(" "))
        if indent % 4 != 0:
            raise CompileError(f"Thut dau dong phai la boi so cua 4: '{raw}'")
        out.append((indent // 4, line.strip()))
    return out


# --------------------------------------------------------------------
# 2. BIEU THUC: parser de quy dung do uu tien (giong Python: * / truoc + -)
# --------------------------------------------------------------------

TOKEN_RE = re.compile(r"\s*(==|!=|<=|>=|[()+\-*/,<>]|[A-Za-z_]\w*|\d+|\".*?\")")


def tokenize_expr(s):
    toks = []
    i = 0
    while i < len(s):
        m = TOKEN_RE.match(s, i)
        if not m or m.group(1) is None:
            if s[i:].strip() == "":
                break
            raise CompileError(f"Khong hieu ky tu trong bieu thuc: '{s[i:]}'")
        toks.append(m.group(1))
        i = m.end()
    return toks


class ExprParser:
    """Grammar:
        cmp    := add ((==|!=|<|>|<=|>=) add)?
        add    := mul (('+'|'-') mul)*
        mul    := unary (('*'|'/') unary)*
        unary  := '-' unary | atom
        atom   := NUMBER | NAME | NAME '(' args ')' | '(' cmp ')' | STRING
    """
    def __init__(self, toks):
        self.toks = toks
        self.i = 0

    def peek(self):
        return self.toks[self.i] if self.i < len(self.toks) else None

    def eat(self, expect=None):
        t = self.peek()
        if t is None:
            raise CompileError("Bieu thuc ket thuc som (thieu dau ngoac?)")
        if expect is not None and t != expect:
            raise CompileError(f"Can '{expect}' nhung gap '{t}'")
        self.i += 1
        return t

    def parse(self):
        node = self.parse_cmp()
        if self.i != len(self.toks):
            raise CompileError(f"Con thua ky tu trong bieu thuc: {self.toks[self.i:]}")
        return node

    def parse_cmp(self):
        left = self.parse_add()
        if self.peek() in ("==", "!=", "<", ">", "<=", ">="):
            op = self.eat()
            right = self.parse_add()
            return Node("binop", op=op, left=left, right=right)
        return left

    def parse_add(self):
        node = self.parse_mul()
        while self.peek() in ("+", "-"):
            op = self.eat()
            rhs = self.parse_mul()
            node = Node("binop", op=op, left=node, right=rhs)
        return node

    def parse_mul(self):
        node = self.parse_unary()
        while self.peek() in ("*", "/"):
            op = self.eat()
            rhs = self.parse_unary()
            node = Node("binop", op=op, left=node, right=rhs)
        return node

    def parse_unary(self):
        if self.peek() == "-":
            self.eat()
            return Node("neg", val=self.parse_unary())
        return self.parse_atom()

    def parse_atom(self):
        t = self.peek()
        if t is None:
            raise CompileError("Thieu toan hang trong bieu thuc")
        if t == "(":
            self.eat("(")
            node = self.parse_cmp()
            self.eat(")")
            return node
        if re.match(r"^\d+$", t):
            self.eat()
            return Node("num", val=int(t))
        if re.match(r'^".*"$', t):
            self.eat()
            return Node("str", val=t[1:-1])
        if re.match(r"^[A-Za-z_]\w*$", t):
            name = self.eat()
            if self.peek() == "(":
                self.eat("(")
                args = []
                if self.peek() != ")":
                    args.append(self.parse_cmp())
                    while self.peek() == ",":
                        self.eat(",")
                        args.append(self.parse_cmp())
                self.eat(")")
                return Node("funccall_expr", name=name, args=args)
            return Node("name", name=name)
        raise CompileError(f"Token la khong hop le: {t}")


def parse_expr(s):
    return ExprParser(tokenize_expr(s)).parse()


def const_eval(node):
    """Neu bieu thuc CHI gom hang so (khong bien) -> tra ve gia tri int.
    Neu co bien -> tra ve None (bao hieu 'khong phai hang so')."""
    if node.kind == "num":
        return node.val
    if node.kind == "neg":
        v = const_eval(node.val)
        return None if v is None else -v
    if node.kind == "binop":
        a = const_eval(node.left)
        b = const_eval(node.right)
        if a is None or b is None:
            return None
        if node.op == "+": return a + b
        if node.op == "-": return a - b
        if node.op == "*": return a * b
        if node.op == "/":
            if b == 0:
                raise CompileError("Chia cho 0 trong bieu thuc hang so")
            return int(a / b) if (a < 0) != (b < 0) else a // b
        raise CompileError(f"Toan tu chua ho tro trong hang so: {node.op}")
    return None


# --------------------------------------------------------------------
# 3. PARSE KHOI LENH
# --------------------------------------------------------------------

def parse_block(lines, i, level):
    stmts = []
    while i < len(lines) and lines[i][0] == level:
        ind, text = lines[i]

        m_if = re.match(r"^if\s+(.+):$", text)
        m_elf = re.match(r"^elf\s+(.+):$", text)
        m_eles = re.match(r"^eles\s*:$", text)
        m_wh = re.match(r"^wh\s+(.+):$", text)
        m_brk = re.match(r"^brk$", text)
        m_cont = re.match(r"^cont$", text)
        m_def = re.match(r"^def\s+([A-Za-z_]\w*)\s*\(([^)]*)\)\s*:$", text)
        m_assign = re.match(r"^([A-Za-z_]\w*)\s*=\s*(.+)$", text)
        m_exprstmt = re.match(r"^([A-Za-z_]\w*)\s*\(.*\)$", text)

        if m_if:
            cond = m_if.group(1)
            i += 1
            then_body, i = parse_block(lines, i, level + 1)
            elf_chain = []
            while i < len(lines) and lines[i][0] == level and \
                  re.match(r"^elf\s+(.+):$", lines[i][1]):
                c2 = re.match(r"^elf\s+(.+):$", lines[i][1]).group(1)
                i += 1
                body2, i = parse_block(lines, i, level + 1)
                elf_chain.append((c2, body2))
            else_body = []
            if i < len(lines) and lines[i][0] == level and \
               re.match(r"^eles\s*:$", lines[i][1]):
                i += 1
                else_body, i = parse_block(lines, i, level + 1)
            stmts.append(Node("if", cond=cond, then=then_body,
                               elfs=elf_chain, els=else_body))
            continue

        if m_wh:
            cond = m_wh.group(1)
            i += 1
            body, i = parse_block(lines, i, level + 1)
            stmts.append(Node("while", cond=cond, body=body))
            continue

        if m_def:
            name = m_def.group(1)
            params_raw = m_def.group(2).strip()
            params = [p.strip() for p in params_raw.split(",")] if params_raw else []
            for p in params:
                if not re.match(r"^[A-Za-z_]\w*$", p):
                    raise CompileError(f"def {name}(): ten tham so khong hop le: '{p}'")
            i += 1
            body, i = parse_block(lines, i, level + 1)
            stmts.append(Node("def", name=name, params=params, body=body))
            continue

        if m_brk:
            stmts.append(Node("brk"))
            i += 1
            continue

        if m_cont:
            stmts.append(Node("cont"))
            i += 1
            continue

        if m_assign:
            # phan biet "ten = so_hex_thuan" (dinh nghia hang render) voi
            # gan bieu thuc thong thuong
            name, rhs = m_assign.groups()
            rhs = rhs.strip()
            if re.match(r"^[0-9A-Fa-f]+$", rhs) and re.search(r"[A-Fa-f]", rhs):
                stmts.append(Node("hexconst", name=name, hexval=rhs))
            else:
                stmts.append(Node("assign", name=name, expr=rhs))
            i += 1
            continue

        if m_exprstmt:
            stmts.append(Node("exprstmt", text=text))
            i += 1
            continue

        raise CompileError(f"Khong hieu dong lenh: '{text}'")

    return stmts, i


def parse_program(src):
    lines = tokenize_lines(src)
    stmts, i = parse_block(lines, 0, 0)
    if i != len(lines):
        raise CompileError("Thut dau dong khong hop le o cuoi file")
    return stmts


# --------------------------------------------------------------------
# 4. CODEGEN
# --------------------------------------------------------------------

CMP_OPS = {"==": "BEQ", "!=": "BNE", "<": "BLT", ">": "BGT", "<=": "BLE", ">=": "BGE"}


class CodeGen:
    def __init__(self):
        self.vars = {}
        self.hexconsts = {}     # ten -> chuoi hex (dung cho render())
        self.objects = {}       # ten -> {'x':addr,'y':addr,'h':addr,'w':addr}
        self.next_addr = DATA_BASE
        self.asm = []
        self.label_count = 0
        self.funcs = {}
        self.need_runtime = False
        self.current_func_params = {}   # ten_tham_so -> dia chi, rong neu top-level
        self.loop_stack = []            # [(top_label, end_label), ...] cho brk/cont long nhau

    def new_label(self, base):
        self.label_count += 1
        return f"_{base}{self.label_count}"

    def var_addr(self, name):
        if name in self.current_func_params:
            return self.current_func_params[name]
        if name not in self.vars:
            self.vars[name] = self.next_addr
            self.next_addr += 1
        return self.vars[name]

    def alloc_block(self, size):
        """Cap phat `size` byte RAM LIEN TIEP (cho bien 16-bit cua runtime)."""
        addr = self.next_addr
        self.next_addr += size
        return addr

    def emit(self, line):
        self.asm.append(line)

    # ---- bieu thuc: dung R0 (ket qua) + R1 (tam), day/lay qua stack khi
    #      can gia tri trung gian (dung PUSH R./POP R. don gian, vi day la
    #      may 1-thanh-ghi-tich-luy, khong toi uu) ----
    def gen_expr(self, node):
        """Sinh ma tinh 'node', KET QUA CUOI CUNG nam o R0."""
        if node.kind == "num":
            self.emit(f"    MOV R0, #{node.val}")
            return
        if node.kind == "name":
            addr = self.var_addr(node.name)
            self.emit(f"    L R0, {addr}")
            return
        if node.kind == "str":
            if node.val not in KEY_NAMES:
                raise CompileError(
                    f'Chuoi "{node.val}" khong phai ten phim hop le. '
                    f'Chuoi chi dung duoc trong bieu thuc khi la ten phim '
                    f'(vd: key() == "OK"). Ten phim hop le: '
                    f'{", ".join(sorted(KEY_NAMES))}')
            self.emit(f'    MOV R0, #{KEY_NAMES[node.val]}   ; "{node.val}"')
            return
        if node.kind == "neg":
            self.gen_expr(node.val)
            self.emit("    MOV R1, #0")
            self.emit("    SUB R1, R0")
            self.emit("    MOV R0, R1")
            return
        if node.kind == "binop":
            if node.op == "/":
                # QUAN TRONG: day la CHIA NGUYEN (lam tron ve 0), khong
                # phai chia thuc kieu Python. Ly do: du co lam duoc so
                # thuc that (IEEE-754 hay fixed-point), print() hien
                # cung CHUA co cach hien thi so co phan thap phan (can
                # viet them ham doi so->chuoi co dau cham, chua lam) -
                # nen chia thuc that su CHUA DUNG DUOC ngay ca khi lam
                # xong. Vi vay uu tien lam CHIA NGUYEN truoc (dung duoc
                # ngay), va se lam so thuc that + hien thi thap phan
                # NHU MOT VIEC RIENG neu ban can.
                self.gen_expr(node.left)
                self.emit("    PUSH R0")
                self.gen_expr(node.right)
                self.emit("    MOV R2, R0")     # R2 = so chia
                self.emit("    POP R0")         # R0 = so bi chia (byte thap)
                self.emit("    MOV R1, #0")     # ER0 = 0:R0 (mo rong 16-bit)
                self.emit("    DIV ER0, R2")    # ER0 = ER0/R2 (thuong so->R0)
                return
            self.gen_expr(node.left)
            self.emit("    PUSH R0")
            self.gen_expr(node.right)
            self.emit("    MOV R1, R0")
            self.emit("    POP R0")
            if node.op == "+":
                self.emit("    ADD R0, R1")
            elif node.op == "-":
                self.emit("    SUB R0, R1")
            elif node.op == "*":
                # MUL can thanh ghi ERn (16-bit). Dung ER0 = R0:R1(sau khi
                # dua toan hang thu 2 vao R2 truoc de khong dam R1).
                self.emit("    MOV R2, R1")
                self.emit("    MOV R1, #0")   # ER0 = 0:R0 (mo rong 8->16 bit)
                self.emit("    MUL ER0, R2")
                # ket qua 16-bit nam trong ER0 (R0:R1) - lay R0 (byte thap)
                # lam ket qua 8-bit (CANH BAO: se tran neu tich > 255)
            elif node.op in CMP_OPS:
                # dung cho dieu kien so sanh dung ngay trong bieu thuc
                # (hien khong sinh gia tri 0/1 vao R0 - chi ho tro trong
                # gen_cond_branch ben duoi, khong dung o day)
                raise CompileError("Toan tu so sanh chi dung truc tiep sau if/wh")
            else:
                raise CompileError(f"Toan tu chua ho tro: {node.op}")
            return
        if node.kind == "funccall_expr" and node.name == "key":
            if len(node.args) != 0:
                raise CompileError("key() khong nhan tham so")
            self.need_runtime = True
            self.emit("    BL rt_scan_key")
            return
        raise CompileError(f"Node bieu thuc khong ho tro: {node.kind}")

    def gen_cond_branch(self, cond_text, true_label):
        node = parse_expr(cond_text)
        if node.kind != "binop" or node.op not in CMP_OPS:
            raise CompileError(f"Dieu kien phai co dang so sanh (==,!=,<,>,<=,>=): {cond_text}")
        self.gen_expr(node.left)
        self.emit("    PUSH R0")
        self.gen_expr(node.right)
        self.emit("    MOV R1, R0")
        self.emit("    POP R0")
        self.emit("    CMP R0, R1")
        self.emit(f"    {CMP_OPS[node.op]} {true_label}")

    # ---- ve hinh: CHI khi toa do la hang so (tinh san luc compile) ----
    def _require_const_args(self, fname, arg_nodes):
        vals = []
        for a in arg_nodes:
            v = const_eval(a)
            if v is None:
                raise CompileError(
                    f"{fname}(...): toa do/tham so phai la SO CO DINH "
                    f"(hang so), CHUA ho tro dung bien chay luc thuc thi "
                    f"o day (can dong co do hoa thoi gian thuc - chua "
                    f"viet). Neu ban dang thu di chuyen hinh theo bien, "
                    f"dung move()/moveto() (hien cung dang bao loi tuong "
                    f"tu vi ly do giong het the nay).")
            vals.append(v)
        return vals

    def gen_set_pixels(self, pts):
        for bufsel in (0, 4):
            self.emit(f"    MOV R0, #{bufsel}")
            self.emit("    ST R0, 61495")   # 0xF037
            for x, y in sorted(pts):
                addr, bit = _pixel_addr_bit(x, y)
                self.emit(f"    SB {addr}.{bit}")

    def gen_circle(self, args):
        x, y, r = self._require_const_args("circle", args)
        pts = set()
        xx, yy = r, 0
        err = 1 - r
        while xx >= yy:
            for dx, dy in [(xx, yy), (yy, xx), (-yy, xx), (-xx, yy),
                            (-xx, -yy), (-yy, -xx), (yy, -xx), (xx, -yy)]:
                pts.add((x + dx, y + dy))
            yy += 1
            if err < 0:
                err += 2 * yy + 1
            else:
                xx -= 1
                err += 2 * (yy - xx) + 1
        self.emit(f"    ; circle({x},{y},{r})")
        self.gen_set_pixels(pts)

    def gen_rect(self, args):
        x, y, h, w = self._require_const_args("rect", args)
        pts = set()
        for i in range(w):
            pts.add((x + i, y))
            pts.add((x + i, y + h - 1))
        for j in range(h):
            pts.add((x, y + j))
            pts.add((x + w - 1, y + j))
        self.emit(f"    ; rect({x},{y},{h},{w})")
        self.gen_set_pixels(pts)

    def gen_line(self, args):
        x1, y1, x2, y2 = self._require_const_args("line", args)
        pts = set()
        dx = abs(x2 - x1); dy = -abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx + dy
        x, y = x1, y1
        while True:
            pts.add((x, y))
            if x == x2 and y == y2:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy; x += sx
            if e2 <= dx:
                err += dx; y += sy
        self.emit(f"    ; line({x1},{y1},{x2},{y2})")
        self.gen_set_pixels(pts)

    def gen_render(self, args):
        if len(args) != 5:
            raise CompileError("render() can dung 5 tham so: cao,dai,x,y,ten_bien")
        h, w, x, y = self._require_const_args("render", args[:4])
        if args[4].kind != "name" or args[4].name not in self.hexconsts:
            raise CompileError(
                "render(): tham so thu 5 phai la ten bien da gan chuoi "
                "hex truoc do (vd: tron = 187E7EFF...)")
        hexstr = self.hexconsts[args[4].name]
        if len(hexstr) != w * 2:
            raise CompileError(
                f"render(): chieu_dai={w} nhung chuoi hex '{hexstr}' co "
                f"{len(hexstr)//2} byte - khong khop nhau")
        if h > 8:
            raise CompileError(
                "render(): chieu_cao toi da 8 (1 byte chi chua 8 hang) - "
                "hinh cao hon phai tach nhieu lan render() chong nhau")
        cols = [int(hexstr[i:i+2], 16) for i in range(0, len(hexstr), 2)]
        pts = set()
        for col, byte in enumerate(cols):
            for row in range(h):
                if byte & (1 << row):
                    pts.add((x + col, y + row))
        self.emit(f"    ; render({h},{w},{x},{y},...)")
        self.gen_set_pixels(pts)

    def compile_stmts(self, stmts):
        for st in stmts:
            self.compile_stmt(st)

    def compile_stmt(self, st):
        if st.kind == "hexconst":
            self.hexconsts[st.name] = st.hexval
            return

        if st.kind == "assign":
            node = parse_expr(st.expr)
            if node.kind == "funccall_expr" and node.name == "rect":
                x, y, h, w = self._require_const_args("rect", node.args)
                xa, ya, ha, wa = (self.var_addr(f"__{st.name}_x"),
                                   self.var_addr(f"__{st.name}_y"),
                                   self.var_addr(f"__{st.name}_h"),
                                   self.var_addr(f"__{st.name}_w"))
                self.objects[st.name] = {"type": "rect", "x": xa, "y": ya, "h": ha, "w": wa}
                self.need_runtime = True
                self.emit(f"    ; {st.name} = rect({x},{y},{h},{w})")
                self.emit(f"    MOV R0, #{x}")
                self.emit(f"    ST R0, {xa}")
                self.emit(f"    MOV R0, #{y}")
                self.emit(f"    ST R0, {ya}")
                self.emit(f"    MOV R0, #{h}")
                self.emit(f"    ST R0, {ha}")
                self.emit(f"    MOV R0, #{w}")
                self.emit(f"    ST R0, {wa}")
                self.emit(f"    MOV R4, #{x}")
                self.emit(f"    MOV R5, #{y}")
                self.emit(f"    MOV R6, #{h}")
                self.emit(f"    MOV R7, #{w}")
                self.emit("    BL rt_fill_rect")
                return
            if node.kind == "funccall_expr" and node.name == "circle":
                x, y, r = self._require_const_args("circle", node.args)
                xa, ya, ra = (self.var_addr(f"__{st.name}_x"),
                              self.var_addr(f"__{st.name}_y"),
                              self.var_addr(f"__{st.name}_r"))
                self.objects[st.name] = {"type": "circle", "x": xa, "y": ya, "r": ra}
                self.need_runtime = True
                self.emit(f"    ; {st.name} = circle({x},{y},{r})")
                self.emit(f"    MOV R0, #{x}")
                self.emit(f"    ST R0, {xa}")
                self.emit(f"    MOV R0, #{y}")
                self.emit(f"    ST R0, {ya}")
                self.emit(f"    MOV R0, #{r}")
                self.emit(f"    ST R0, {ra}")
                self.emit(f"    MOV R4, #{x}")
                self.emit(f"    MOV R5, #{y}")
                self.emit(f"    MOV R6, #{r}")
                self.emit("    BL rt_fill_circle")
                return
            if node.kind == "funccall_expr" and node.name == "line":
                x1, y1, x2, y2 = self._require_const_args("line", node.args)
                x1a, y1a, x2a, y2a = (self.var_addr(f"__{st.name}_x1"),
                                       self.var_addr(f"__{st.name}_y1"),
                                       self.var_addr(f"__{st.name}_x2"),
                                       self.var_addr(f"__{st.name}_y2"))
                self.objects[st.name] = {"type": "line", "x1": x1a, "y1": y1a,
                                          "x2": x2a, "y2": y2a}
                self.need_runtime = True
                self.emit(f"    ; {st.name} = line({x1},{y1},{x2},{y2})")
                self.emit(f"    MOV R0, #{x1}")
                self.emit(f"    ST R0, {x1a}")
                self.emit(f"    MOV R0, #{y1}")
                self.emit(f"    ST R0, {y1a}")
                self.emit(f"    MOV R0, #{x2}")
                self.emit(f"    ST R0, {x2a}")
                self.emit(f"    MOV R0, #{y2}")
                self.emit(f"    ST R0, {y2a}")
                self.emit(f"    MOV R4, #{x1}")
                self.emit(f"    MOV R5, #{y1}")
                self.emit(f"    MOV R6, #{x2}")
                self.emit(f"    MOV R7, #{y2}")
                self.emit("    BL rt_line_draw")
                return
            if node.kind == "funccall_expr" and node.name == "render":
                raise CompileError(
                    f"'{st.name} = render(...)': render() chua ho tro gan "
                    f"vao bien de di chuyen (can nhung du lieu hex vao ROM "
                    f"luc chay, chua lam - pham vi rieng). Dung render() "
                    f"nhu lenh ve mot lan co dinh (khong gan ten).")
            self.gen_expr(node)
            addr = self.var_addr(st.name)
            self.emit(f"    ST R0, {addr}")
            return

        if st.kind == "if":
            end_l = self.new_label("endif")
            branches = [(st.cond, st.then)] + st.elfs
            for cond, body in branches:
                true_l = self.new_label("then")
                self.gen_cond_branch(cond, true_l)
                skip_l = self.new_label("skip")
                self.emit(f"    B {skip_l}")
                self.emit(f"{true_l}:")
                self.compile_stmts(body)
                self.emit(f"    B {end_l}")
                self.emit(f"{skip_l}:")
            self.compile_stmts(st.els)
            self.emit(f"{end_l}:")
            return

        if st.kind == "while":
            top_l = self.new_label("wtop")
            body_l = self.new_label("wbody")
            end_l = self.new_label("wend")
            self.emit(f"{top_l}:")
            self.gen_cond_branch(st.cond, body_l)
            self.emit(f"    B {end_l}")
            self.emit(f"{body_l}:")
            self.loop_stack.append((top_l, end_l))
            self.compile_stmts(st.body)
            self.loop_stack.pop()
            self.emit(f"    B {top_l}")
            self.emit(f"{end_l}:")
            return

        if st.kind == "brk":
            if not self.loop_stack:
                raise CompileError("'brk' chi dung duoc ben trong 'wh'")
            _, end_l = self.loop_stack[-1]
            self.emit(f"    B {end_l}")
            return

        if st.kind == "cont":
            if not self.loop_stack:
                raise CompileError("'cont' chi dung duoc ben trong 'wh'")
            top_l, _ = self.loop_stack[-1]
            self.emit(f"    B {top_l}")
            return

        if st.kind == "def":
            skip_l = self.new_label("skipfn")
            self.emit(f"    B {skip_l}")
            fn_label = f"_fn_{st.name}"
            param_addrs = [self.var_addr(f"__arg_{st.name}_{p}") for p in st.params]
            self.funcs[st.name] = {"label": fn_label, "params": st.params,
                                    "param_addrs": param_addrs}
            self.emit(f"{fn_label}:")
            self.emit("    PUSH LR")
            saved_params = self.current_func_params
            self.current_func_params = dict(zip(st.params, param_addrs))
            self.compile_stmts(st.body)
            self.current_func_params = saved_params
            self.emit("    POP LR")
            self.emit("    RT")
            self.emit(f"{skip_l}:")
            return

        if st.kind == "exprstmt":
            node = parse_expr(st.text)
            if node.kind != "funccall_expr":
                raise CompileError(f"Dong lenh khong hop le: {st.text}")
            self.compile_call(node)
            return

        raise CompileError(f"Node khong ho tro: {st.kind}")

    def compile_call(self, node):
        name = node.name
        args = node.args

        if name == "print":
            if len(args) not in (1, 3, 5) or args[0].kind != "str":
                raise CompileError(
                    'print() dung dang print("chuoi") hoac '
                    'print("chuoi", x, y) hoac '
                    'print("chuoi", x, y, chieu_cao, chieu_dai)')
            text = args[0].val
            if len(args) == 1:
                x, y, ch, cw = 10, 10, 7, 5
            elif len(args) == 3:
                x, y = self._require_const_args("print", args[1:])
                ch, cw = 7, 5
            else:
                x, y, ch, cw = self._require_const_args("print", args[1:])
            self._gen_print(text, x, y, ch, cw)
            return

        if name == "circle":
            self.gen_circle(args); return
        if name == "rect":
            self.gen_rect(args); return
        if name == "line":
            self.gen_line(args); return
        if name == "render":
            self.gen_render(args); return

        if name in ("move", "moveto"):
            if len(args) != 3 or args[0].kind != "name":
                raise CompileError(f"{name}(ten_vat_the, x, y) can 3 tham so")
            objname = args[0].name
            if objname not in self.objects:
                raise CompileError(f"'{objname}' chua duoc tao bang 'ten = rect(...)', 'ten = circle(...)' hoac 'ten = line(...)'")
            self.need_runtime = True
            obj = self.objects[objname]

            if obj["type"] == "line":
                # line: x,y ap dung cho CA HAI dau (x1,y1) va (x2,y2) dich
                # chuyen cung luong - giu nguyen do dai/huong duong thang
                self.emit(f"    ; {name}({objname}, ...) [line]")
                self.emit(f"    L R4, {obj['x1']}")
                self.emit(f"    L R5, {obj['y1']}")
                self.emit(f"    L R6, {obj['x2']}")
                self.emit(f"    L R7, {obj['y2']}")
                self.emit("    BL rt_line_clear")
                if name == "move":
                    dx_node, dy_node = args[1], args[2]
                    self.gen_expr(dx_node)
                    self.emit("    PUSH R0")
                    self.gen_expr(dy_node)
                    self.emit("    MOV R1, R0")
                    self.emit("    POP R0")   # R0=dx, R1=dy
                    for coord in ("x1", "x2"):
                        self.emit(f"    L R2, {obj[coord]}")
                        self.emit("    ADD R2, R0")
                        self.emit(f"    ST R2, {obj[coord]}")
                    for coord in ("y1", "y2"):
                        self.emit(f"    L R2, {obj[coord]}")
                        self.emit("    ADD R2, R1")
                        self.emit(f"    ST R2, {obj[coord]}")
                else:
                    # moveto: dat DAU MOT (x1,y1) vao toa do moi, GIU
                    # NGUYEN do lech sang dau hai (x2,y2) - tuong duong
                    # "di chuyen ca doan" toi vi tri moi cho dau mot.
                    self.emit(f"    L R2, {obj['y1']}")
                    self.emit(f"    L R3, {obj['y2']}")
                    self.emit("    SUB R3, R2")             # R3 = y2-y1 (do lech)
                    self.emit("    PUSH R3")
                    self.emit(f"    L R2, {obj['x1']}")   # x1 cu
                    self.emit(f"    L R3, {obj['x2']}")   # x2 cu
                    self.emit("    SUB R3, R2")            # R3 = x2-x1 (do lech)
                    self.emit("    PUSH R3")               # [SP]=dx_lech,[SP+1]=dy_lech
                    x_node, y_node = args[1], args[2]
                    self.gen_expr(x_node)
                    self.emit(f"    ST R0, {obj['x1']}")
                    self.emit("    POP R1")                 # dx_lech
                    self.emit("    ADD R0, R1")
                    self.emit(f"    ST R0, {obj['x2']}")
                    self.gen_expr(y_node)
                    self.emit(f"    ST R0, {obj['y1']}")
                    self.emit("    POP R1")                  # dy_lech
                    self.emit("    ADD R0, R1")
                    self.emit(f"    ST R0, {obj['y2']}")
                self.emit(f"    L R4, {obj['x1']}")
                self.emit(f"    L R5, {obj['y1']}")
                self.emit(f"    L R6, {obj['x2']}")
                self.emit(f"    L R7, {obj['y2']}")
                self.emit("    BL rt_line_draw")
                return

            def emit_load_params():
                self.emit(f"    L R4, {obj['x']}")
                self.emit(f"    L R5, {obj['y']}")
                if obj["type"] == "rect":
                    self.emit(f"    L R6, {obj['h']}")
                    self.emit(f"    L R7, {obj['w']}")
                else:
                    self.emit(f"    L R6, {obj['r']}")

            clear_sub = "rt_clear_rect" if obj["type"] == "rect" else "rt_clear_circle"
            fill_sub = "rt_fill_rect" if obj["type"] == "rect" else "rt_fill_circle"

            self.emit(f"    ; {name}({objname}, ...) [{obj['type']}]")
            emit_load_params()
            self.emit(f"    BL {clear_sub}")
            if name == "move":
                dx_node = args[1]
                dy_node = args[2]
                self.gen_expr(dx_node)
                self.emit(f"    L R1, {obj['x']}")
                self.emit("    ADD R0, R1")
                self.emit(f"    ST R0, {obj['x']}")
                self.gen_expr(dy_node)
                self.emit(f"    L R1, {obj['y']}")
                self.emit("    ADD R0, R1")
                self.emit(f"    ST R0, {obj['y']}")
            else:
                x_node = args[1]
                y_node = args[2]
                self.gen_expr(x_node)
                self.emit(f"    ST R0, {obj['x']}")
                self.gen_expr(y_node)
                self.emit(f"    ST R0, {obj['y']}")
            emit_load_params()
            self.emit(f"    BL {fill_sub}")
            return

        if name == "erase":
            if len(args) != 1 or args[0].kind != "name":
                raise CompileError("erase(ten_vat_the) can 1 tham so")
            objname = args[0].name
            if objname not in self.objects:
                raise CompileError(f"'{objname}' chua duoc tao bang 'ten = rect(...)', 'ten = circle(...)' hoac 'ten = line(...)'")
            self.need_runtime = True
            obj = self.objects[objname]
            self.emit(f"    ; erase({objname}) [{obj['type']}]")
            if obj["type"] == "line":
                self.emit(f"    L R4, {obj['x1']}")
                self.emit(f"    L R5, {obj['y1']}")
                self.emit(f"    L R6, {obj['x2']}")
                self.emit(f"    L R7, {obj['y2']}")
                self.emit("    BL rt_line_clear")
            elif obj["type"] == "rect":
                self.emit(f"    L R4, {obj['x']}")
                self.emit(f"    L R5, {obj['y']}")
                self.emit(f"    L R6, {obj['h']}")
                self.emit(f"    L R7, {obj['w']}")
                self.emit("    BL rt_clear_rect")
            else:
                self.emit(f"    L R4, {obj['x']}")
                self.emit(f"    L R5, {obj['y']}")
                self.emit(f"    L R6, {obj['r']}")
                self.emit("    BL rt_clear_circle")
            return

        if name == "wait":
            if len(args) != 1:
                raise CompileError("wait(so_mili_giay) can 1 tham so")
            ms = const_eval(args[0])
            if ms is None:
                raise CompileError("wait(): so mili giay phai la hang so")
            if not (0 <= ms <= 8000):
                raise CompileError(
                    "wait(): so mili giay phai trong khoang 0-8000 "
                    "(gioi han 1 lan nap Timer0Interval o TICKS_PER_MS=8, "
                    "16-bit: 65535/8 = 8191ms toi da, lam tron xuong 8000 "
                    "cho de nho). Can lau hon thi goi wait() nhieu lan.")
            self.need_runtime = True
            ticks = ms * 8   # TICKS_PER_MS = 8, DO THAT tu libcw.h (Timer0),
                              # khong con doan chu ky lenh nhu ban cu
            self.emit(f"    ; wait({ms}ms) = {ticks} tick, Timer0 that "
                      f"(TICKS_PER_MS=8, do tu libcw.h, khong doan)")
            self.emit(f"    MOV R4, #{ticks & 0xFF}")
            self.emit(f"    MOV R5, #{(ticks >> 8) & 0xFF}")
            self.emit("    BL rt_wait_ms")
            return

        if name == "key":
            if len(args) != 0:
                raise CompileError("key() khong nhan tham so")
            self.need_runtime = True
            self.emit("    BL rt_scan_key")
            return

        if name in self.funcs:
            fn = self.funcs[name]
            if len(args) != len(fn["params"]):
                raise CompileError(
                    f"{name}() can {len(fn['params'])} tham so "
                    f"({', '.join(fn['params']) or 'khong co'}) nhung goi "
                    f"voi {len(args)} tham so")
            for arg_node, addr in zip(args, fn["param_addrs"]):
                self.gen_expr(arg_node)
                self.emit(f"    ST R0, {addr}")
            self.emit(f"    BL {fn['label']}")
            return

        raise CompileError(f"Ham chua duoc dinh nghia/ho tro: {name}()")

    def _gen_print(self, text, x0=10, y0=10, ch=7, cw=5):
        """ch/cw = chieu cao/chieu dai MOI ky tu, tinh bang pixel.
        Font goc la 5x7 (rong 5, cao 7) - neu ch/cw khac 5x7 thi PHONG TO
        hoac THU NHO bang cach nhan ban/bo bot pixel theo ti le (nearest-
        neighbor), khong lam mem net."""
        if ch < 1 or cw < 1:
            raise CompileError("print(): chieu_cao/chieu_dai phai >= 1")
        writes = {}
        x = x0
        step = cw + 1   # khoang cach giua cac ky tu (giu ty le voi be rong moi)
        for c in text:
            if c not in FONT5X7:
                raise CompileError(f"print(): ky tu '{c}' chua co trong font")
            glyph = FONT5X7[c]   # 5 cot goc, 7 hang goc
            for dst_col in range(cw):
                src_col = dst_col * 5 // cw
                src_col = min(src_col, 4)
                line = glyph[src_col]
                for dst_row in range(ch):
                    src_row = dst_row * 7 // ch
                    src_row = min(src_row, 6)
                    if line & (1 << src_row):
                        addr, bit = _pixel_addr_bit(x + dst_col, y0 + dst_row)
                        writes[addr] = writes.get(addr, 0) | (1 << bit)
            x += step
        self.emit(f'    ; print("{text}", {x0}, {y0}, cao={ch}, dai={cw})')
        for bufsel in (0, 4):
            self.emit(f"    MOV R3, #{bufsel}")
            self.emit("    ST R3, 61495")
            for addr, mask in sorted(writes.items()):
                self.emit(f"    L R0, {addr}")
                self.emit(f"    OR R0, #{mask}")
                self.emit(f"    ST R0, {addr}")


def compile_to_asm(src):
    stmts = parse_program(src)
    cg = CodeGen()
    cg.emit("    ORG 0x1000")
    cg.compile_stmts(stmts)
    if cg.need_runtime:
        cg.emit("    B __after_runtime__")
        here = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(here, "runtime.inc.asm"), encoding="utf-8") as f:
            rt_text = f.read().rstrip("\n")
        # bien RAM cua runtime: (ten, so byte). Cap phat SAU code nguoi dung
        # nen khong bao gio dam dia chi bien cua ho.
        rt_vars = {}
        for name, size in (("LN_SX", 1), ("LN_SY", 1), ("LN_DX", 2),
                           ("LN_DY", 2), ("LN_ERR", 2)):
            rt_vars[name] = cg.alloc_block(size)
        def _sub(m):
            if m.group(1) not in rt_vars:
                raise CompileError(f"runtime.inc.asm dung bien chua khai bao: @{m.group(1)}@")
            return str(rt_vars[m.group(1)])
        rt_text = re.sub(r"@(\w+)@", _sub, rt_text)
        cg.emit(rt_text)
        cg.emit("__after_runtime__:")
    cg.emit("    NOP")
    return "\n".join(cg.asm) + "\n"


def main():
    if len(sys.argv) < 2:
        print("Dung: python3 pymini2.py chuongtrinh.pymini [-o out.bin]")
        sys.exit(1)
    src_path = sys.argv[1]
    out_bin = "out.bin"
    if "-o" in sys.argv:
        out_bin = sys.argv[sys.argv.index("-o") + 1]

    with open(src_path, encoding="utf-8") as f:
        src = f.read()

    try:
        asm_text = compile_to_asm(src)
    except CompileError as e:
        print(f"Loi compile: {e}", file=sys.stderr)
        sys.exit(1)

    asm_path = os.path.splitext(src_path)[0] + ".gen.asm"
    with open(asm_path, "w", encoding="utf-8") as f:
        f.write(asm_text)
    print(f"Da sinh hop ngu: {asm_path}")

    here = os.path.dirname(os.path.abspath(__file__))
    subprocess.run([sys.executable, os.path.join(here, "nxu8asm.py"),
                     asm_path, "-o", out_bin], check=True)


if __name__ == "__main__":
    main()
