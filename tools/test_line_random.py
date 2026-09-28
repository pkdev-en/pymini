import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, ROOT); sys.path.insert(0, HERE)
import random
from u8sim import load
from pymini2 import compile_to_asm

def ref_line(x1, y1, x2, y2):   # y nguyen thuat toan trong CodeGen.gen_line
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
    return pts

def run_line(x1, y1, x2, y2):
    asm = compile_to_asm(f"ln = line({x1}, {y1}, {x2}, {y2})\n")
    cpu, sym = load(asm)
    r = cpu.run(until_pc=sym["__sim_end"], max_steps=4_000_000)
    return r, cpu

random.seed(20260928)
cases = [(10,10,50,40), (0,0,191,63), (191,63,0,0), (0,63,191,0), (191,0,0,63),
         (5,5,5,5), (0,30,191,30), (100,0,100,63), (0,0,63,63), (0,0,1,63),
         (0,0,191,1), (191,10,0,11), (30,60,31,2)]
while len(cases) < 250:
    cases.append((random.randint(0,191), random.randint(0,63),
                  random.randint(0,191), random.randint(0,63)))

bad = 0
for c in cases:
    r, cpu = run_line(*c)
    exp = ref_line(*c)
    ok = (r == "reached" and cpu.pixels(0) == exp and cpu.pixels(1) == exp and cpu.rom_writes == 0)
    if not ok:
        bad += 1
        if bad <= 5:
            print("LECH:", c, r, len(cpu.pixels(0)), "vs", len(exp), "rom_writes", cpu.rom_writes)
print(f"{len(cases)} duong, sai lech: {bad}")
