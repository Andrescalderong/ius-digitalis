#!/usr/bin/env python3
import subprocess, os, datetime, pathlib, sys

BASE = os.path.dirname(os.path.abspath(__file__))
LOGS = os.path.join(BASE, "logs")
pathlib.Path(LOGS).mkdir(parents=True, exist_ok=True)
log = os.path.join(LOGS, f"pipeline_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

def run_step(title, rel_dir, script):
    cwd = os.path.join(BASE, rel_dir)
    cmd = [sys.executable, "-u", script]
    print(f"\n[{datetime.datetime.now().isoformat(timespec='seconds')}] {title}")
    print("$", " ".join(cmd), f"(cwd={cwd})")
    with open(log, "a") as f:
        f.write(f"\n[{datetime.datetime.now().isoformat(timespec='seconds')}] {title}\n$ {' '.join(cmd)} (cwd={cwd})\n")
        p = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in p.stdout:
            print(line, end=""); f.write(line)
        rc = p.wait()
        if rc != 0:
            msg = f"[ERROR] {title} terminó con código {rc}\n"
            print(msg); f.write(msg)
            return False
    return True

ok = True
ok &= run_step("🧠 [1/3] IA Classifier",       "ia_classifier",           "classify.py")
ok &= run_step("🔗 [2/3] Blockchain Registry", "blockchain_registry",      "anchor.py")
ok &= run_step("🤖 [3/3] RPA SECOP",           os.path.join("rpa_secop","src"), "main.py")

print("\n" + ("✅ Pipeline completo OK" if ok else "⚠️ Pipeline completado con errores"))
print("📁 Resultados:")
print(f" - IA:         {os.path.join(BASE, 'ia_classifier', 'outputs')}")
print(f" - Blockchain: {os.path.join(BASE, 'blockchain_registry', 'outputs')}")
print(f" - RPA:        {os.path.join(BASE, 'rpa_secop', 'data')}")
print(f" - Logs:       {log}")
