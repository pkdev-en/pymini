import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, ROOT); sys.path.insert(0, HERE)
from u8sim import load
from pymini2 import compile_to_asm, KEY_NAMES

def ref_line(x1, y1, x2, y2):
    pts = set(); dx = abs(x2-x1); dy = -abs(y2-y1)
    sx = 1 if x1 < x2 else -1; sy = 1 if y1 < y2 else -1
    err = dx + dy; x, y = x1, y1
    while True:
        pts.add((x, y))
        if x == x2 and y == y2: break
        e2 = 2*err
        if e2 >= dy: err += dy; x += sx
        if e2 <= dx: err += dx; y += sy
    return pts

asm = compile_to_asm(open(os.path.join(ROOT,"examples","line_test.pymini")).read())
cpu, sym = load(asm)
WAIT = sym["rt_wait_ms"]

def frame():
    if cpu.pc == WAIT: cpu.step()
    r = cpu.run(until_pc=WAIT, max_steps=cpu.steps + 600_000)
    assert r == "reached", r
    return cpu.pixels(0)

def check(label, got, exp):
    print(f"{label:34s} {'DUNG' if got == exp else 'SAI'}  ({len(got)} diem, mong doi {len(exp)})")

check("khoi dong line(10,10,50,40)", frame(), ref_line(10,10,50,40))
cpu.keys = {KEY_NAMES["RIGHT"]}
check("move(ln,5,0) lan 1", frame(), ref_line(15,10,55,40))
check("move(ln,5,0) lan 2", frame(), ref_line(20,10,60,40))
cpu.keys = {KEY_NAMES["OK"]}
check("moveto(ln,0,0) - giu nguyen do lech", frame(), ref_line(0,0,40,30))
cpu.keys = {KEY_NAMES["AC"]}
check("erase(ln)", frame(), set())
cpu.keys = set()
check("tha phim - van trong", frame(), set())
print("ghi nham ROM:", cpu.rom_writes)
