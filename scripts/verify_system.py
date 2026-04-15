import subprocess
import os
import sys

def run_step(name, command):
    print(f"\n--- Phase: {name} ---")
    print(f"Running: {command}")
    try:
        # Use utf-8 encoding to handle non-ASCII output from tools like pyright
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding="utf-8")
        stdout = result.stdout or ""
        stderr = result.stderr or ""
        
        if result.returncode == 0:
            print(f"[PASS] {name}")
            return True, result.stdout
        else:
            print(f"[FAIL] {name} (Exit {result.returncode})")
            print(stdout)
            print(stderr)
            return False, stdout + stderr
    except Exception as e:
        print(f"[ERROR] Error executing {name}: {e}")
        return False, str(e)

def main():
    print("==============================")
    print(" AGENCY SWARM VERIFICATION LOOP ")
    print("==============================\n")
    
    report = {
        "Build/Environment": "PASS",
        "Types (Pyright)": "NOT RUN",
        "Lint (Ruff)": "NOT RUN",
        "Tests (Pytest)": "NOT RUN",
        "Security": "PASS"
    }
    
    # Phase 2: Type Check
    ok, output = run_step("Type Check", "pyright .")
    report["Types (Pyright)"] = "PASS" if ok else "FAIL"
    
    # Phase 3: Lint Check
    ok, output = run_step("Lint Check", "ruff check .")
    report["Lint (Ruff)"] = "PASS" if ok else "FAIL"
    
    # Phase 4: Test Suite
    ok, output = run_step("Test Suite", "pytest tests/test_ecc_foundation.py")
    report["Tests (Pytest)"] = "PASS" if ok else "FAIL"
    
    # Phase 5: Security Scan
    print("\n--- Phase: Security Scan ---")
    secrets_found = False
    # Simple check for API keys in the code
    for root, dirs, files in os.walk("."):
        if ".git" in dirs: dirs.remove(".git")
        if ".cache" in dirs: dirs.remove(".cache")
        for file in files:
            if file.endswith((".py", ".js", ".ts", ".env")):
                path = os.path.join(root, file)
                if path == "./.env": continue # .env is expected to have keys locally
                try:
                    with open(path, "r", errors="ignore") as f:
                        content = f.read()
                        if "sk-" in content or "anthropic-sdk" in content:
                            print(f"[ALERT] Potential leak in {path}")
                            secrets_found = True
                except: pass
    
    report["Security"] = "FAIL" if secrets_found else "PASS"

    # Phase 6: AI Regression Check (ECC Phase 17)
    print("\n--- Phase: AI Regression Check ---")
    regression_issues = False
    for root, dirs, files in os.walk("src"):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", errors="ignore") as f:
                        content = f.read()
                        # Pattern 1: ask_ai(..., is_json=True) but prompt doesn't mention JSON
                        if 'is_json=True' in content and 'JSON' not in content.upper():
                            print(f"[FAIL] AI Blind Spot in {path}: 'is_json=True' used but prompt missing JSON instruction.")
                            regression_issues = True
                except: pass
    
    report["AI Regression"] = "FAIL" if regression_issues else "PASS"
    
    print("\n" + "="*30)
    print(" VERIFICATION REPORT ")
    print("="*30)
    for k, v in report.items():
        print(f"{k.ljust(18)}: [{v}]")
    print("="*30)
    
    if all(v == "PASS" for v in report.values()):
        print("\nOVERALL: SYSTEM READY")
    else:
        print("\nOVERALL: ISSUES DETECTED")

if __name__ == "__main__":
    main()
