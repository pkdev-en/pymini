import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, ROOT); sys.path.insert(0, HERE)
from u8sim import load
from pymini2 import compile_to_asm, KEY_NAMES

def go(src, max_steps=2_000_000):
    cpu, sym = load(compile_to_asm(src))
    r = cpu.run(until_pc=sym["__sim_end"], max_steps=max_steps)
    return r, cpu, sym

# ---- brk / cont ----
r, cpu, _ = go(open(os.path.join(ROOT,"examples","brk_test.pymini")).read())
i = cpu.mem[36864]
print(f"brk_test   : ket thuc={r}, i={i} (mong doi 10: cont o 5, brk o 10) ->", "DUNG" if r=="reached" and i==10 else "SAI")

r, cpu, _ = go(open(os.path.join(ROOT,"examples","brk_nested.pymini")).read())
i, j = cpu.mem[36864], cpu.mem[36865]
print(f"brk_nested : ket thuc={r}, i={i}, j={j} (mong doi i=5, j=3) ->", "DUNG" if r=="reached" and (i,j)==(5,3) else "SAI")

# ---- brk chi thoat vong TRONG ----
src = """i = 0
n = 0
wh i < 4:
    i = i + 1
    j = 0
    wh j < 10:
        j = j + 1
        if j == 3:
            brk
        n = n + 1
"""
r, cpu, _ = go(src)
print(f"brk long   : n={cpu.mem[36865]} (mong doi 4 vong x 2 lan = 8) ->", "DUNG" if r=="reached" and cpu.mem[36865]==8 else "SAI")

# ---- def co tham so: move qua ham moveit(dx,dy) ----
cpu, sym = load(compile_to_asm(open(os.path.join(ROOT,"examples","def_param_test.pymini")).read()))
W = sym["rt_wait_ms"]
def frame():
    if cpu.pc == W: cpu.step()
    assert cpu.run(until_pc=W, max_steps=cpu.steps+600_000) == "reached"
    px = cpu.pixels(0); xs=[p[0] for p in px]; ys=[p[1] for p in px]
    return (min(xs), min(ys), len(px))
exp = [((50,20,150), None), ((55,20,150),"RIGHT"), ((60,20,150),"RIGHT"),
       ((60,25,150),"DOWN"), ((55,25,150),"LEFT"), ((55,20,150),"UP")]
ok = True
for want, key in exp:
    cpu.keys = {KEY_NAMES[key]} if key else set()
    got = frame()
    ok &= (got == want)
    print(f"def-tham-so {str(key):5s}: {got} mong doi {want}")
print("def co tham so ->", "DUNG" if ok else "SAI", "| ROM ghi nham:", cpu.rom_writes)

# ---- def long nhau: ham goi ham, LR phai song sot ----
src = """box = rect(10, 10, 5, 5)
def a(d):
    move(box, d, 0)
def b():
    a(3)
    a(4)
b()
b()
"""
r, cpu, _ = go(src)
xs = [p[0] for p in cpu.pixels(0)]
print(f"def goi def: x_min={min(xs)} (mong doi 10+3+4+3+4=24), ket thuc={r} ->", "DUNG" if r=="reached" and min(xs)==24 else "SAI")
