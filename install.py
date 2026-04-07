#!/usr/bin/env python3
"""
install.py — OSift dependency installer
========================================
Installs all Python packages from requirements.txt, required system tools
via apt (Linux) or brew (macOS), and Go-based ProjectDiscovery tools via
`go install`. Also clones Python-based tools (TREVORspray, GitDorker,
theHarvester) to /opt/<toolname>/ for PATH availability.

Usage:
    python3 install.py
    python3 install.py --skip-go      # skip ProjectDiscovery Go tools
    python3 install.py --skip-github  # skip GitHub-cloned tools
    python3 install.py --pip-only     # Python packages only
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

VERSION = "1.0.0"

SYSTEM = platform.system()
IS_LINUX = SYSTEM == "Linux"
IS_MACOS = SYSTEM == "Darwin"

# ── Colours ───────────────────────────────────────────────────────────────────
def _c(code: str, text: str) -> str:
    if sys.stdout.isatty():
        return f"\033[{code}m{text}\033[0m"
    return text

def info(msg: str)    -> None: print(_c("36", f"[INFO]  {msg}"))
def ok(msg: str)      -> None: print(_c("32", f"[OK]    {msg}"))
def warn(msg: str)    -> None: print(_c("33", f"[WARN]  {msg}"), file=sys.stderr)
def error(msg: str)   -> None: print(_c("31", f"[ERROR] {msg}"), file=sys.stderr)
def section(msg: str) -> None: print(_c("35", f"\n{'='*60}\n  {msg}\n{'='*60}"))


def run(cmd: list, check: bool = True, env: dict = None,
        cwd: str = None) -> subprocess.CompletedProcess:
    info(f"Running: {' '.join(str(c) for c in cmd)}")
    merged_env = {**os.environ, **(env or {})}
    result = subprocess.run(cmd, env=merged_env, cwd=cwd)
    if check and result.returncode != 0:
        error(f"Command failed (exit {result.returncode}): {' '.join(str(c) for c in cmd)}")
        sys.exit(result.returncode)
    return result


def cmd_exists(name: str) -> bool:
    return shutil.which(name) is not None


# ── Python packages ───────────────────────────────────────────────────────────
def install_python_packages() -> None:
    section("Installing Python packages (pip)")

    reqs = Path(__file__).parent / "requirements.txt"
    if not reqs.exists():
        error(f"requirements.txt not found at {reqs}")
        sys.exit(1)

    run([sys.executable, "-m", "pip", "install", "--break-system-packages", "--upgrade", "pip"])
    run([sys.executable, "-m", "pip", "install", "--break-system-packages", "-r", str(reqs)])
    ok("Python packages installed.")


# ── System packages ───────────────────────────────────────────────────────────
APT_PACKAGES = [
    "git",
    "curl",
    "wget",
    "dnsutils",        # dig, nslookup, host
    "whois",
    "amass",           # subdomain enum — OWASP Amass by Jeff Foley @caffix
    "golang-go",       # Go — needed for ProjectDiscovery go install
    "python3-pip",
    "python3-venv",
    "nmap",
    "jq",
    "ca-certificates",
    "build-essential",
]

BREW_PACKAGES = [
    "git",
    "curl",
    "wget",
    "amass",           # subdomain enum — OWASP Amass by Jeff Foley @caffix
    "go",              # Go — needed for ProjectDiscovery go install
    "jq",
    "nmap",
    "theharvester",    # email/subdomain OSINT — Christian Martorella @laramies
    "whatweb",         # web tech fingerprinting — urbanadventurer
]


def install_system_linux() -> None:
    section("Installing system packages (apt)")
    if os.geteuid() != 0:
        warn("Not root — apt installs may fail. Re-run with sudo.")
    run(["apt-get", "update", "-y"])
    run(["apt-get", "install", "-y"] + APT_PACKAGES)
    ok("System packages installed.")


def install_system_macos() -> None:
    section("Installing system packages (brew)")
    if not cmd_exists("brew"):
        warn("Homebrew not found. Install from https://brew.sh then re-run.")
        return
    for pkg in BREW_PACKAGES:
        info(f"brew install {pkg}")
        _brew_user = os.environ.get("SUDO_USER", "")
        _brew_pfx  = ["sudo", "-u", _brew_user] if _brew_user and _brew_user != "root" else []
        run(_brew_pfx + ["brew", "install", pkg], check=False)
    ok("Homebrew packages installed.")


# ── ProjectDiscovery Go tools ─────────────────────────────────────────────────
# All tools by ProjectDiscovery (@projectdiscovery — https://projectdiscovery.io)
PD_TOOLS = [
    ("github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest",  "subfinder"),
    ("github.com/projectdiscovery/httpx/cmd/httpx@latest",              "httpx"),
    ("github.com/projectdiscovery/dnsx/cmd/dnsx@latest",                "dnsx"),
    ("github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest",         "nuclei"),
    ("github.com/projectdiscovery/naabu/v2/cmd/naabu@latest",           "naabu"),
    ("github.com/projectdiscovery/tlsx/cmd/tlsx@latest",                "tlsx"),
    ("github.com/projectdiscovery/cdncheck/cmd/cdncheck@latest",        "cdncheck"),
    ("github.com/projectdiscovery/katana/cmd/katana@latest",            "katana"),
    ("github.com/projectdiscovery/asnmap/cmd/asnmap@latest",            "asnmap"),
    ("github.com/projectdiscovery/uncover/cmd/uncover@latest",          "uncover"),
    ("github.com/projectdiscovery/cloudlist/cmd/cloudlist@latest",      "cloudlist"),
    ("github.com/projectdiscovery/shuffledns/cmd/shuffledns@latest",    "shuffledns"),
    ("github.com/projectdiscovery/chaos-client/cmd/chaos@latest",       "chaos"),
    # waybackurls — tomnomnom @tomnomnom (https://github.com/tomnomnom/waybackurls)
    ("github.com/tomnomnom/waybackurls@latest",                         "waybackurls"),
    # ffuf — web fuzzer by Joohoi @joohoi (https://github.com/ffuf/ffuf)
    ("github.com/ffuf/ffuf/v2@latest",                                  "ffuf"),
]


def install_go_tools() -> None:
    section("Installing ProjectDiscovery + Go-based tools (go install)")

    if not cmd_exists("go"):
        warn("Go not found on PATH — skipping Go tool installation.")
        warn("Install Go from https://go.dev/dl/ and re-run.")
        return

    gopath = os.environ.get("GOPATH", os.path.expanduser("~/go"))
    gobin = os.path.join(gopath, "bin")
    info(f"GOPATH={gopath}  GOBIN={gobin}")
    os.makedirs(gobin, exist_ok=True)

    env = {**os.environ, "GOPATH": gopath, "GOBIN": gobin, "GO111MODULE": "on"}

    for pkg, name in PD_TOOLS:
        info(f"go install {pkg}  ({name})")
        result = run(["go", "install", pkg], check=False, env=env)
        if result.returncode == 0:
            ok(f"  → {name} installed to {gobin}")
        else:
            warn(f"  → {name} install failed (non-fatal; will be skipped at runtime)")

    ok(f"Go tools installation complete. Ensure {gobin} is on your PATH:")
    info(f"  echo 'export PATH=$PATH:{gobin}' >> ~/.bashrc")


# ── GitHub-cloned Python tools ────────────────────────────────────────────────
# Tools cloned to /opt/<toolname>/ on both Linux and macOS.
GITHUB_TOOLS = [
    {
        "name": "TREVORspray",
        "repo": "https://github.com/blacklanternsecurity/TREVORspray.git",
        # M365 credential sprayer — blacklanternsecurity @blacklanternsecurity
        "dest": "/opt/TREVORspray",
        "pip_install": True,    # has setup.py / pyproject.toml
    },
    {
        "name": "GitDorker",
        "repo": "https://github.com/obheda12/GitDorker.git",
        # GitHub secret scanner — obheda12 (https://github.com/obheda12/GitDorker)
        "dest": "/opt/GitDorker",
        "pip_install": False,
    },
    {
        "name": "theHarvester",
        "repo": "https://github.com/laramies/theHarvester.git",
        # OSINT email/domain harvester — Christian Martorella @laramies
        "dest": "/opt/theHarvester",
        "pip_install": True,
    },
    {
        "name": "puredns",
        "repo": "https://github.com/d3mondev/puredns.git",
        # DNS brute-force with wildcard filtering — d3mondev
        "dest": "/opt/puredns",
        "pip_install": False,
        "go_build": True,
    },
    {
        "name": "xurlfind3r",
        "repo": "https://github.com/hueristiq/xurlfind3r.git",
        # Passive URL discovery — hueristiq
        "dest": "/opt/xurlfind3r",
        "pip_install": False,
        "go_build": True,
    },
    {
        "name": "maigret",
        "repo": "https://github.com/soxoj/maigret.git",
        # Social profile OSINT by username — soxoj
        "dest": "/opt/maigret",
        "pip_install": True,
    },
    {
        "name": "trufflehog",
        "repo": "https://github.com/trufflesecurity/trufflehog.git",
        # Secret scanning across git history — trufflesecurity
        "dest": "/opt/trufflehog",
        "pip_install": False,
        "go_build": True,
    },
    {
        "name": "cloud_enum",
        "repo": "https://github.com/initstring/cloud_enum.git",
        # Cloud bucket enum (S3/Azure/GCP) — initstring
        "dest": "/opt/cloud_enum",
        "pip_install": True,
    },
]


def clone_or_update(repo: str, dest: str) -> bool:
    """Clone repo to dest, or git pull if it already exists. Returns success."""
    if os.path.isdir(os.path.join(dest, ".git")):
        info(f"Updating existing clone: {dest}")
        result = run(["git", "-C", dest, "pull", "--ff-only"], check=False)
    else:
        info(f"Cloning {repo} → {dest}")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        result = run(["git", "clone", "--depth=1", repo, dest], check=False)
    return result.returncode == 0


def install_github_tools() -> None:
    section("Cloning GitHub-based tools to /opt/")

    for tool in GITHUB_TOOLS:
        name  = tool["name"]
        repo  = tool["repo"]
        dest  = tool["dest"]

        info(f"--- {name} ---")
        success = clone_or_update(repo, dest)

        if not success:
            warn(f"  → Failed to clone/update {name}. Skipping.")
            continue

        ok(f"  → {name} at {dest}")

        if tool.get("pip_install"):
            pyproject = os.path.join(dest, "pyproject.toml")
            setup_py  = os.path.join(dest, "setup.py")
            reqs_txt  = os.path.join(dest, "requirements.txt")

            if os.path.exists(pyproject) or os.path.exists(setup_py):
                info(f"  → pip install -e {dest}")
                run([sys.executable, "-m", "pip", "install", "--break-system-packages", "-e", dest], check=False)
            elif os.path.exists(reqs_txt):
                info(f"  → pip install -r {reqs_txt}")
                run([sys.executable, "-m", "pip", "install", "--break-system-packages", "-r", reqs_txt], check=False)

        if tool.get("go_build"):
            if cmd_exists("go"):
                info(f"  → go build in {dest}")
                run(["go", "build", "-o", f"/usr/local/bin/{name.lower()}", "."],
                    check=False, cwd=dest)
            else:
                warn(f"  → Go not found; cannot build {name}")

    ok("GitHub tool installation complete.")


# ── Symlink installation ──────────────────────────────────────────────────────
def _install_symlinks() -> None:
    """Create /usr/local/bin symlinks for all-user access (including root)."""
    from pathlib import Path as _Path
    import stat as _stat
    app_dir = _Path(__file__).parent.resolve()
    bin_dir = _Path("/usr/local/bin")

    # (script_relative_to_app_dir, symlink_name_in_bin_dir)
    LINKS = [
        ("osift.py", "osift"),
    ]

    try:
        bin_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        warn("Cannot access /usr/local/bin — run as root to install symlinks.")
        return

    for script_rel, link_name in LINKS:
        script = app_dir / script_rel
        link   = bin_dir / link_name
        if not script.exists():
            warn(f"Script not found, skipping symlink: {script}")
            continue
        # Make script executable
        current = script.stat().st_mode
        script.chmod(current | _stat.S_IXUSR | _stat.S_IXGRP | _stat.S_IXOTH)
        # Ensure shebang
        try:
            text = script.read_text(encoding="utf-8", errors="ignore")
            if not text.startswith("#!"):
                script.write_text("#!/usr/bin/env python3\n" + text, encoding="utf-8")
        except Exception:
            pass
        # Create/replace symlink
        if link.exists() or link.is_symlink():
            link.unlink()
        link.symlink_to(script)
        ok(f"Symlink installed: {link}  →  {script}")


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        prog="install.py",
        description=f"OSift installer v{VERSION} — installs all dependencies and tools.",
    )
    parser.add_argument("--skip-go",     action="store_true", help="Skip Go/ProjectDiscovery tool install.")
    parser.add_argument("--skip-github", action="store_true", help="Skip GitHub-cloned tool install.")
    parser.add_argument("--pip-only",    action="store_true", help="Install Python packages only.")
    args = parser.parse_args()

    print(_c("36", f"""
╔══════════════════════════════════════════════════════╗
║           OSift Installer  v{VERSION}                  ║
║   OSINT & Reconnaissance Framework                  ║
║   Platform: {SYSTEM:<43}║
╚══════════════════════════════════════════════════════╝
"""))

    # Step 0: Symlinks — created first so they survive any later failure
    _install_symlinks()

    # Step 1: Python packages
    install_python_packages()

    if args.pip_only:
        ok("--pip-only flag set. Skipping system/Go/GitHub tool installation.")
        print(_c("32", "\n[DONE]  Python package installation complete.\n"))
        return

    # Step 2: System packages
    if IS_LINUX:
        install_system_linux()
    elif IS_MACOS:
        install_system_macos()
    else:
        warn(f"Unsupported platform '{SYSTEM}' — skipping system package install.")

    # Step 3: Go tools
    if not args.skip_go:
        install_go_tools()
    else:
        info("--skip-go set. Skipping ProjectDiscovery / Go tool installation.")

    # Step 4: GitHub-cloned Python tools
    if not args.skip_github:
        install_github_tools()
    else:
        info("--skip-github set. Skipping GitHub tool cloning.")

    # Step 5: Symlinks (already done in Step 0; repeated for idempotency)
_install_symlinks()

    print(_c("32", "\n[DONE]  OSift installation complete.\n"))
    print("Next steps:")
    print("  1. Copy osift_settings.json.example to osift_settings.json and populate API keys.")
    print("  2. Ensure ~/go/bin (or $GOPATH/bin) is on your PATH for ProjectDiscovery tools.")
    print("  3. Run:  sudo python3 osift.py -c 'Company' -d example.com")


if __name__ == "__main__":
    main()
