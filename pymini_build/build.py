#!/usr/bin/env python3
import sys, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
def die(msg):
    print(f"Loi: {msg}", file=sys.stderr); sys.exit(1)
def main():
    src_path = sys.argv[1]
    out_bin = sys.argv[sys.argv.index("-o") + 1] if "-o" in sys.argv else "out.bin"
    base = os.path.splitext(src_path)[0]
    gen_asm = base + ".gen.asm"
    merged_asm = base + ".full.asm"
    r = subprocess.run([sys.executable, os.path.join(HERE, "pymini2.py"), src_path, "-o", "/tmp/__tmp.bin"], capture_output=True, text=True)
    if not os.path.isfile(gen_asm):
        print(r.stdout); print(r.stderr, file=sys.stderr); die("pymini2 khong sinh duoc asm")
    with open(os.path.join(HERE, "boot_full.asm"), encoding="utf-8") as f: boot = f.read()
    with open(os.path.join(HERE, "clear_screen.inc.asm"), encoding="utf-8") as f: clear = f.read()
    with open(gen_asm, encoding="utf-8") as f: gen = f.read()
    body = "\n".join(l for l in gen.splitlines() if not l.strip().startswith("ORG"))
    marker = "user_entry:\n"
    idx = boot.find(marker)
    if idx == -1: die("khong tim thay user_entry")
    merged = boot[:idx+len(marker)] + clear + body + "\n" + boot[idx+len(marker):]
    with open(merged_asm, "w", encoding="utf-8") as f: f.write(merged)
    r = subprocess.run([sys.executable, os.path.join(HERE, "nxu8asm.py"), merged_asm, "-o", out_bin])
    if r.returncode != 0: die("nxu8asm loi")
    print(f"XONG: {out_bin}")
if __name__ == "__main__": main()
