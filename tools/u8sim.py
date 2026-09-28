#!/usr/bin/env python3
"""
u8sim.py - mo phong nX-U8/100 toi gian, giai ma TRUC TIEP tu INSTR_TABLE cua
nxu8asm.py (bang ma hoa lay tu Instruction Manual), du de chay code sinh ra
boi pymini2 va kiem chung logic ve pixel / quet phim / cho timer.

Mo hinh bo nho:
  0x0000-0x7FFF : ROM (ghi bi BO QUA va dem lai - dung de bat loi ghi vao ROM)
  0x8000-0xF7FF : RAM
  0xF800-0xFFFF : VRAM, chon bitplane qua 0xF037 (0 -> plane0, 4 -> plane1)
  0xF040        : KeyboardIn  (doc phu thuoc 0xF046 KeyboardOut va phim dang nhan)
  0xF022/0xF023 : Timer0Counter (gia lap: moi lan doc tang len 8 tick)
Ngan xep: danh sach Python (PUSH/POP doi xung, khong mo hinh SP that).
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from nxu8asm import INSTR_TABLE, Assembler


def _build_decoder():
    dec = []
    for mn, ops, t1, t2 in INSTR_TABLE:
        if mn == "EXTBW":
            continue
        mask = val = 0
        fields = {}
        for idx, ch in enumerate(t1):
            bit = 15 - idx
            if ch in "01":
                mask |= 1 << bit
                if ch == "1":
                    val |= 1 << bit
            else:
                fields.setdefault(ch, []).append(bit)
        dec.append((bin(mask).count("1"), mask, val, mn, ops, fields, t2))
    dec.sort(key=lambda e: -e[0])
    return dec


DEC = _build_decoder()


class SimError(Exception):
    pass


class CPU:
    def __init__(self, image, entry=0x1000):
        self.mem = bytearray(65536)
        self.mem[:len(image)] = image
        self.R = [0] * 16
        self.pc = entry
        self.LR = 0
        self.stack = []
        self.Z = self.C = self.S = self.OV = 0
        self.vram = [bytearray(0x800), bytearray(0x800)]
        self.plane = 0
        self.keys = set()
        self.timer = 0
        self.rom_writes = 0
        self.steps = 0
        self.timer_reads = 0

    # ---------------- bo nho ----------------
    def kbd_in(self):
        ko = self.mem[0xF046]
        res = 0xFF
        for i in self.keys:
            if ko & (0x80 >> (i // 8)):
                res &= ~(0x80 >> (i % 8)) & 0xFF
        return res

    def rd8(self, a):
        a &= 0xFFFF
        if a >= 0xF800:
            return self.vram[self.plane][a - 0xF800]
        if a == 0xF040:
            return self.kbd_in()
        if a in (0xF022, 0xF023):
            if a == 0xF022:
                self.timer_reads += 1
                self.timer = (self.timer + 8) & 0xFFFF
            return (self.timer >> (8 * (a - 0xF022))) & 0xFF
        return self.mem[a]

    def wr8(self, a, v):
        a &= 0xFFFF
        v &= 0xFF
        if a >= 0xF800:
            self.vram[self.plane][a - 0xF800] = v
            return
        if a == 0xF037:
            self.plane = 1 if (v & 4) else 0
        if a in (0xF022, 0xF023):
            self.timer = 0
        if a < 0x8000:
            self.rom_writes += 1
            return
        self.mem[a] = v

    def rd16(self, a):
        return self.rd8(a) | (self.rd8(a + 1) << 8)

    def wr16(self, a, v):
        self.wr8(a, v & 0xFF)
        self.wr8(a + 1, (v >> 8) & 0xFF)

    def er(self, n):
        return self.R[n] | (self.R[n + 1] << 8)

    def set_er(self, n, v):
        self.R[n] = v & 0xFF
        self.R[n + 1] = (v >> 8) & 0xFF

    # ---------------- co ----------------
    def _flags_sub(self, a, b, c, bits, chain):
        mask = (1 << bits) - 1
        top = 1 << (bits - 1)
        r = a - b - c
        res = r & mask
        self.C = 1 if r < 0 else 0
        self.OV = 1 if ((a ^ b) & (a ^ res) & top) else 0
        self.S = 1 if res & top else 0
        z = 1 if res == 0 else 0
        self.Z = (self.Z & z) if chain else z
        return res

    def _flags_add(self, a, b, c, bits, chain):
        mask = (1 << bits) - 1
        top = 1 << (bits - 1)
        r = a + b + c
        res = r & mask
        self.C = 1 if r > mask else 0
        self.OV = 1 if (~(a ^ b) & (a ^ res) & top) else 0
        self.S = 1 if res & top else 0
        z = 1 if res == 0 else 0
        self.Z = (self.Z & z) if chain else z
        return res

    def _zs(self, res, bits=8):
        self.Z = 1 if res == 0 else 0
        self.S = 1 if res & (1 << (bits - 1)) else 0

    def _cond(self, mn):
        lt = self.S ^ self.OV
        return {
            "BGE": not self.C, "BLT": self.C,
            "BGT": (not self.C) and (not self.Z),
            "BLE": self.C or self.Z,
            "BGES": not lt, "BLTS": lt,
            "BGTS": not (lt or self.Z), "BLES": lt or self.Z,
            "BNE": not self.Z, "BEQ": self.Z,
            "BAL": True,
        }[mn]

    # ---------------- 1 lenh ----------------
    def step(self):
        pc = self.pc
        w = self.rd16(pc)
        for _, mask, val, mn, ops, f, t2 in DEC:
            if (w & mask) == val:
                break
        else:
            raise SimError(f"khong giai ma duoc {w:04X} tai {pc:04X}")
        F = {}
        for k, bits in f.items():
            v = 0
            for b in bits:
                v = (v << 1) | ((w >> b) & 1)
            F[k] = v
        ln = 2
        w2 = None
        if t2:
            w2 = self.rd16(pc + 2)
            ln = 4
        nxt = pc + ln
        R = self.R
        self.steps += 1

        # --- 8-bit ALU ---
        if ops in (("Rn", "Rm"), ("Rn", "imm8")) and mn in (
                "ADD", "ADDC", "SUB", "SUBC", "CMP", "CMPC", "AND", "OR", "XOR", "MOV"):
            n = F["n"]
            b = R[F["m"]] if ops[1] == "Rm" else F["i"]
            a = R[n]
            if mn == "MOV":
                R[n] = b
                self._zs(b)
            elif mn == "ADD":
                R[n] = self._flags_add(a, b, 0, 8, False)
            elif mn == "ADDC":
                R[n] = self._flags_add(a, b, self.C, 8, True)
            elif mn == "SUB":
                R[n] = self._flags_sub(a, b, 0, 8, False)
            elif mn == "SUBC":
                R[n] = self._flags_sub(a, b, self.C, 8, True)
            elif mn == "CMP":
                self._flags_sub(a, b, 0, 8, False)
            elif mn == "CMPC":
                self._flags_sub(a, b, self.C, 8, True)
            elif mn == "AND":
                R[n] = a & b
                self._zs(R[n])
            elif mn == "OR":
                R[n] = a | b
                self._zs(R[n])
            elif mn == "XOR":
                R[n] = a ^ b
                self._zs(R[n])
        # --- 16-bit ALU ---
        elif ops in (("ERn", "ERm"), ("ERn", "imm7")) and mn in ("ADD", "CMP", "MOV"):
            n = F["n"] * 2
            if ops[1] == "ERm":
                b = self.er(F["m"] * 2)
            else:
                b = F["i"]
                if b & 0x40:
                    b -= 0x80
                b &= 0xFFFF
            a = self.er(n)
            if mn == "MOV":
                self.set_er(n, b)
                self._zs(b, 16)
            elif mn == "ADD":
                self.set_er(n, self._flags_add(a, b, 0, 16, False))
            else:
                self._flags_sub(a, b, 0, 16, False)
        # --- dich bit ---
        elif mn in ("SLL", "SRL", "SRA") and ops[0] == "Rn":
            n = F["n"]
            k = R[F["m"]] if ops[1] == "Rm" else F["w"]
            a = R[n]
            if mn == "SLL":
                res = (a << k) & 0xFF
                self.C = ((a << k) >> 8) & 1 if k else self.C
            elif mn == "SRL":
                res = a >> k
                self.C = (a >> (k - 1)) & 1 if k else self.C
            else:
                sa = a - 256 if a & 0x80 else a
                res = (sa >> k) & 0xFF
            R[n] = res
            self._zs(res)
        # --- load/store ---
        elif mn in ("L", "ST"):
            dst, src = ops
            if src == "Dadr":
                addr = w2
            elif src == "ERm_ind":
                addr = self.er(F["m"] * 2)
            else:
                raise SimError(f"L/ST kieu {src} chua mo phong")
            if dst == "Rn":
                n = F["n"]
                if mn == "L":
                    R[n] = self.rd8(addr)
                    self._zs(R[n])
                else:
                    self.wr8(addr, R[n])
            elif dst == "ERn":
                n = F["n"] * 2
                if mn == "L":
                    self.set_er(n, self.rd16(addr))
                    self._zs(self.er(n), 16)
                else:
                    self.wr16(addr, self.er(n))
            else:
                raise SimError(f"L/ST {dst} chua mo phong")
        # --- ngan xep ---
        elif mn == "PUSH":
            if ops == ("Rn",):
                self.stack.append(R[F["n"]])
            elif ops == ("ERn",):
                self.stack.append(self.er(F["n"] * 2))
            elif ops == ("CtrlList",):
                if F["L"] & 0b0111:
                    raise SimError("PUSH danh sach dieu khien ngoai LR")
                if F["L"] & 8:
                    self.stack.append(self.LR)
            else:
                raise SimError("PUSH kieu la")
        elif mn == "POP":
            if ops == ("Rn",):
                R[F["n"]] = self.stack.pop() & 0xFF
            elif ops == ("ERn",):
                self.set_er(F["n"] * 2, self.stack.pop())
            elif ops == ("CtrlList",):
                if F["L"] & 0b0111:
                    raise SimError("POP danh sach dieu khien ngoai LR")
                if F["L"] & 8:
                    self.LR = self.stack.pop()
            else:
                raise SimError("POP kieu la")
        # --- nhay ---
        elif mn == "B" and ops == ("Cadr",):
            nxt = w2
        elif mn == "BL" and ops == ("Cadr",):
            self.LR = nxt
            nxt = w2
        elif mn == "RT":
            nxt = self.LR
        elif ops == ("Radr",):
            if self._cond(mn):
                r = F["r"]
                if r & 0x80:
                    r -= 256
                nxt = pc + 2 + 2 * r
        # --- nhan/chia ---
        elif mn == "MUL":
            n = F["n"] * 2
            p = R[n] * R[F["m"]]
            self.set_er(n, p)
            self._zs(p & 0xFFFF, 16)
        elif mn == "DIV":
            n = F["n"] * 2
            d = R[F["m"]]
            if d == 0:
                self.C = 1
            else:
                q, rem = divmod(self.er(n), d)
                self.set_er(n, q)
                R[F["m"]] = rem
                self.C = 0
        # --- bit ---
        elif mn in ("SB", "RB", "TB"):
            b = F["b"]
            if ops == ("Dbitadr",):
                a = w2
                v = self.rd8(a)
                if mn == "SB":
                    self.wr8(a, v | (1 << b))
                elif mn == "RB":
                    self.wr8(a, v & ~(1 << b) & 0xFF)
                else:
                    self.Z = 0 if (v >> b) & 1 else 1
            else:
                n = F["n"]
                if mn == "SB":
                    R[n] |= 1 << b
                elif mn == "RB":
                    R[n] &= ~(1 << b) & 0xFF
                else:
                    self.Z = 0 if (R[n] >> b) & 1 else 1
        elif mn in ("NOP", "DI", "EI"):
            pass
        else:
            raise SimError(f"lenh {mn} {ops} chua mo phong tai {pc:04X}")

        self.pc = nxt & 0xFFFF

    def run(self, until_pc=None, max_steps=2_000_000, on_step=None):
        while self.steps < max_steps:
            if until_pc is not None and self.pc == until_pc:
                return "reached"
            if on_step:
                on_step(self)
            self.step()
        return "max_steps"

    # ---------------- man hinh ----------------
    def pixels(self, plane=0):
        out = set()
        for y in range(64):
            for xb in range(24):
                v = self.vram[plane][y * 32 + xb]
                for bit in range(8):
                    if v & (0x80 >> bit):
                        out.add((xb * 8 + bit, y))
        return out


def assemble(text):
    a = Assembler()
    img = a.assemble(text.splitlines(keepends=True))
    return img, a.symtab


def load(asm_text, entry=0x1000):
    img, sym = assemble(asm_text + "\n__sim_end:\n    B __sim_end\n")
    return CPU(img, entry), sym
