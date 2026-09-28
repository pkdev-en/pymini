import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, ROOT); sys.path.insert(0, HERE)
from u8sim import load
from pymini2 import compile_to_asm, KEY_NAMES

asm = compile_to_asm(open(os.path.join(ROOT,"examples","move_test.pymini")).read())
cpu, sym = load(asm)
WAIT = sym["rt_wait_ms"]

def bbox(px):
    xs = [p[0] for p in px]; ys = [p[1] for p in px]
    return (min(xs), min(ys), max(xs), max(ys), len(px)) if px else None

def frame():
    """chay den lan tiep theo chuong trinh vao wait() - luc do man hinh on dinh"""
    if cpu.pc == WAIT:               # dang o dau wait -> buoc qua de sang vong sau
        cpu.step()
    r = cpu.run(until_pc=WAIT, max_steps=cpu.steps + 400_000)
    assert r == "reached", r
    return bbox(cpu.pixels(0))

print("khoi dong   ->", frame())
for name in ("RIGHT", "RIGHT", "DOWN", "DOWN", "LEFT", "UP"):
    cpu.keys = {KEY_NAMES[name]}
    print(f"giu {name:5s} ->", frame())
cpu.keys = set()
print("tha phim    ->", frame(), "(phai dung yen)")
print("ROM ghi nham:", cpu.rom_writes, "| plane0 == plane1:", cpu.pixels(0) == cpu.pixels(1))
