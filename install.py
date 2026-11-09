#!/usr/bin/env python3
"""
OSift — OSINT Reconnaissance Framework
Install script for /opt/pr0t31n/OSift/
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

# ─── ANSI colours ────────────────────────────────────────────────────────────
R  = "\033[1;31m"
G  = "\033[1;32m"
Y  = "\033[1;33m"
B  = "\033[1;34m"
C  = "\033[1;36m"
W  = "\033[0m"
# ─────────────────────────────────────────────────────────────────────────────

APP_NAME = "OSift"
APP_DIR  = Path("/opt/pr0t31n/OSift")
BIN_DIR  = Path("/usr/local/bin")
OPT_DIR  = Path("/opt")

SYMLINKS = {
    "osift": APP_DIR / "osift.py",
}

# system package lists --------------------------------------------------------
APT_PKGS = [
    "git", "curl", "wget", "dnsutils", "whois", "amass",
    "golang-go", "python3-pip", "python3-venv", "nmap", "jq",
    "ca-certificates", "build-essential", "whatweb",
    "libimage-exiftool-perl",
]
DNF_PKGS = [
    "git", "curl", "wget", "bind-utils", "whois", "golang",
    "python3-pip", "python3-virtualenv", "nmap", "jq",
    "ca-certificates", "gcc", "make", "whatweb",
]
ZYPPER_PKGS = [
    "git", "curl", "wget", "bind-utils", "whois", "golang",
    "python3-pip", "python3-venv", "nmap", "jq",
    "ca-certificates", "gcc", "make",
]
BREW_PKGS = [
    "git", "curl", "wget", "amass", "go", "jq",
    "nmap", "theharvester", "whatweb", "whois", "exiftool",
]

# pip packages ----------------------------------------------------------------
PIP_PKGS = [
    "requests>=2.31.0",
    "urllib3>=2.0.0",
    "dnspython>=2.4.0",
    "python-whois>=0.9.4",
    "shodan>=1.31.0",
    "censys>=2.2.0",
    "beautifulsoup4>=4.12.0",
    "lxml>=4.9.0",
    "cryptography>=41.0.0",
    "pyOpenSSL>=23.0.0",
    "colorama>=0.4.6",
    "tqdm>=4.66.0",
    "paramiko>=3.3.0",
    "python-docx>=1.1.0",
    "openpyxl>=3.1.0",
    "pandas>=2.1.0",
    "jinja2>=3.1.0",
    "selenium>=4.15.0",
    "webdriver-manager>=4.0.0",
    "cloud-enum",
    "EmailHarvester",
    "playwright",
    "waymore",
    "gato-cli",
]

# Go tools (go install) -------------------------------------------------------
GO_INSTALL_TOOLS = [
    "github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest",
    "github.com/projectdiscovery/httpx/cmd/httpx@latest",
    "github.com/projectdiscovery/dnsx/cmd/dnsx@latest",
    "github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest",
    "github.com/projectdiscovery/tlsx/cmd/tlsx@latest",
    "github.com/projectdiscovery/cdncheck/cmd/cdncheck@latest",
    "github.com/projectdiscovery/katana/cmd/katana@latest",
    "github.com/projectdiscovery/asnmap/cmd/asnmap@latest",
    "github.com/projectdiscovery/uncover/cmd/uncover@latest",
    "github.com/projectdiscovery/cloudlist/cmd/cloudlist@latest",
    "github.com/projectdiscovery/shuffledns/cmd/shuffledns@latest",
    "github.com/projectdiscovery/chaos-client/cmd/chaos@latest",
    "github.com/tomnomnom/waybackurls@latest",
    "github.com/ffuf/ffuf/v2@latest",
    "github.com/d3mondev/puredns/v2@latest",
    "github.com/zricethezav/gitleaks/v8@latest",
    "github.com/hakluke/hakoriginfinder@latest",
]

# Git tools -------------------------------------------------------------------
# Each entry: (repo_url, clone_dir, post_clone_action)
# post_clone_action is a callable that receives the clone path
GIT_TOOLS = [
    # TREVORspray — repo deleted upstream; replaced by o365spray
    {
        "name":   "o365spray",
        "url":    "https://github.com/0xZDH/o365spray",
        "dest":   OPT_DIR / "o365spray",
        "action": "pip_install_dot",
    },
    {
        "name":   "GitDorker",
        "url":    "https://github.com/obheda12/GitDorker",
        "dest":   OPT_DIR / "GitDorker",
        "action": None,
    },
    {
        "name":   "theHarvester",
        "url":    "https://github.com/laramies/theHarvester",
        "dest":   OPT_DIR / "theHarvester",
        "action": "pip_install_dot",  # upstream switched to pyproject.toml
    },
    {
        "name":   "cent",
        "url":    "https://github.com/xm1k3/cent",
        "dest":   OPT_DIR / "cent",
        "action": "go_build",
    },
    {
        "name":   "xurlfind3r",
        "url":    "https://github.com/hueristiq/xurlfind3r",
        "dest":   OPT_DIR / "xurlfind3r",
        "action": "go_build_output",
        "output": "/usr/local/bin/xurlfind3r",
        "go_args": ["./cmd/xurlfind3r/"],
    },
    {
        "name":   "GHunt",
        "url":    "https://github.com/mxrch/GHunt",
        "dest":   OPT_DIR / "GHunt",
        "action": None,
    },
    {
        "name":   "EmailHarvester",
        "url":    "https://github.com/maldevel/EmailHarvester",
        "dest":   OPT_DIR / "EmailHarvester",
        "action": "chmod_executable",
    },
    {
        "name":   "maigret",
        "url":    "https://github.com/soxoj/maigret",
        "dest":   OPT_DIR / "maigret",
        "action": None,  # CLI installed via pip (PIP_PKGS); clone kept for reference
    },
    # trufflehog: installed via install_trufflehog() GitHub release download
    {
        "name":   "cloud_enum",
        "url":    "https://github.com/initstring/cloud_enum",
        "dest":   OPT_DIR / "cloud_enum",
        "action": "pip_install_dot",
    },
]

# Verify tools ----------------------------------------------------------------
VERIFY_BINS = [
    "amass", "nmap", "subfinder", "httpx", "dnsx",
    "nuclei", "waybackurls", "ffuf",
    "maigret", "trufflehog", "cloud_enum", "puredns",
    "gitleaks", "o365spray",
    "waymore", "gato", "hakoriginfinder", "exiftool",
]
VERIFY_MODS = [
    "requests", "dns", "whois", "bs4",
    "colorama", "tqdm", "paramiko",
    "openpyxl", "pandas", "jinja2", "selenium",
]

# File-path tools that aren't on PATH but need to exist
VERIFY_FILES = {
    "EmailHarvester": "/opt/EmailHarvester/EmailHarvester.py",
}

# ─── helpers ─────────────────────────────────────────────────────────────────

def banner():
    print(f"""
{C}╔══════════════════════════════════════════════╗
║        OSift — OSINT Recon Framework         ║
║        Install Script                        ║
╚══════════════════════════════════════════════╝{W}
""")


def info(msg):  print(f"{G}[+]{W} {msg}")
def warn(msg):  print(f"{Y}[!]{W} {msg}")
def note(msg):  print(f"{Y}[i]{W} {msg}")
def err(msg):   print(f"{R}[✗]{W} {msg}")
def step(msg):  print(f"\n{B}━━ {msg} ━━{W}")


def run(cmd, **kwargs):
    print(f"    {C}>{W} {' '.join(str(c) for c in cmd)}")
    result = subprocess.run(cmd, **kwargs)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(str(c) for c in cmd)}")
    return result


def run_ok(cmd, **kwargs):
    try:
        subprocess.run(cmd, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       **kwargs)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def require_root():
    if platform.system() != "Darwin" and os.geteuid() != 0:
        err("This script must be run as root (or with sudo) on Linux.")
        sys.exit(1)


def detect_os():
    system = platform.system()
    if system == "Darwin":
        return "macos"
    if system == "Windows":
        return "windows"
    os_release = {}
    try:
        with open("/etc/os-release") as f:
            for line in f:
                line = line.strip()
                if "=" in line:
                    k, v = line.split("=", 1)
                    os_release[k] = v.strip('"')
    except FileNotFoundError:
        pass
    dist_id = os_release.get("ID", "").lower()
    id_like  = os_release.get("ID_LIKE", "").lower()
    if dist_id in ("kali", "ubuntu", "debian") or "debian" in id_like:
        return "apt"
    if dist_id in ("rhel", "centos", "rocky", "almalinux", "fedora") or "rhel" in id_like or "fedora" in id_like:
        return "dnf"
    if dist_id in ("sles", "opensuse", "opensuse-leap", "opensuse-tumbleweed") or "suse" in id_like:
        return "zypper"
    return "apt"


def _pip_cmd():
    if shutil.which("pip3"):
        return ["pip3"]
    if shutil.which("pip"):
        return ["pip"]
    return [sys.executable, "-m", "pip"]


def _go_bin():
    for candidate in ("/usr/local/go/bin/go", shutil.which("go") or ""):
        if candidate and Path(candidate).exists():
            return candidate
    return "go"


def _go_env():
    gopath = Path.home() / "go"
    go_bin_dir = str(Path("/usr/local/go/bin"))
    return {
        **os.environ,
        "GOPATH": str(gopath),
        "GOBIN":  "/usr/local/bin",
        "PATH":   go_bin_dir + ":" + os.environ.get("PATH", ""),
        "HOME":   str(Path.home()),
    }


MIN_GO_VERSION = (1, 22)


def _go_version_tuple(go_binary):
    """Return (major, minor) for the installed Go, or (0, 0) on failure."""
    try:
        r = subprocess.run([go_binary, "version"], capture_output=True, text=True, timeout=10)
        # output: "go version go1.22.5 linux/amd64"
        import re as _re
        m = _re.search(r'go(\d+)\.(\d+)', r.stdout)
        if m:
            return (int(m.group(1)), int(m.group(2)))
    except Exception:
        pass
    return (0, 0)


def _ensure_modern_go():
    """If the installed Go is too old for projectdiscovery tools, install
    the latest stable Go from golang.org to /usr/local/go/."""
    gb = _go_bin()
    ver = _go_version_tuple(gb)
    if ver >= MIN_GO_VERSION:
        info(f"Go {ver[0]}.{ver[1]} meets minimum {MIN_GO_VERSION[0]}.{MIN_GO_VERSION[1]}.")
        return True

    if ver == (0, 0):
        warn("No working Go compiler found.")
    else:
        warn(f"Go {ver[0]}.{ver[1]} is below minimum {MIN_GO_VERSION[0]}.{MIN_GO_VERSION[1]}.")

    info("Installing latest Go from golang.org …")
    machine = platform.machine().lower()
    arch_map = {"x86_64": "amd64", "amd64": "amd64", "aarch64": "arm64", "arm64": "arm64"}
    arch = arch_map.get(machine, "amd64")
    system = platform.system().lower()

    try:
        import json, tempfile
        r = subprocess.run(
            ["curl", "-fsSL", "https://go.dev/dl/?mode=json&include=all"],
            capture_output=True, text=True, check=True, timeout=30,
        )
        releases = json.loads(r.stdout)
        stable = [rel for rel in releases if rel.get("stable")]
        if not stable:
            warn("Could not determine latest stable Go version.")
            return False
        latest = stable[0]
        go_ver = latest["version"]  # e.g. "go1.23.1"

        tarball_name = f"{go_ver}.{system}-{arch}.tar.gz"
        dl_url = f"https://go.dev/dl/{tarball_name}"
        info(f"Downloading {tarball_name} …")

        with tempfile.TemporaryDirectory() as td:
            tarball = os.path.join(td, tarball_name)
            subprocess.run(["curl", "-fsSL", "-o", tarball, dl_url],
                           check=True, timeout=300)
            # Remove old installation if present
            go_dir = Path("/usr/local/go")
            if go_dir.exists():
                import shutil as _sh
                _sh.rmtree(str(go_dir))
            subprocess.run(["tar", "-C", "/usr/local", "-xzf", tarball], check=True)

        new_ver = _go_version_tuple("/usr/local/go/bin/go")
        if new_ver >= MIN_GO_VERSION:
            info(f"Go {new_ver[0]}.{new_ver[1]} installed to /usr/local/go/")
            return True
        else:
            warn(f"Installed Go {new_ver[0]}.{new_ver[1]} still below minimum.")
            return False
    except Exception as exc:
        warn(f"Go auto-install failed: {exc}")
        return False



def _dpkg_installed(pkg):
    try:
        r = subprocess.run(["dpkg", "-s", pkg],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return r.returncode == 0
    except FileNotFoundError:
        return False


def _rpm_installed(pkg):
    try:
        return subprocess.run(
            ["rpm", "-q", pkg],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        ).returncode == 0
    except FileNotFoundError:
        return False


def _pip_installed(pkg_spec):
    import importlib.util
    name = pkg_spec.split(">=")[0].split("==")[0].split("[")[0].split("<")[0].strip()
    _IMPORT_MAP = {
        "python-whois": "whois", "beautifulsoup4": "bs4", "python-docx": "docx",
        "pyOpenSSL": "OpenSSL", "dnspython": "dns", "pyyaml": "yaml",
        "Pillow": "PIL", "charset-normalizer": "charset_normalizer",
        "webdriver-manager": "webdriver_manager", "edgartools": "edgar",
        "cloud-enum": "cloud_enum", "EmailHarvester": "EmailHarvester",
    }
    mod = _IMPORT_MAP.get(name, name.replace("-", "_"))
    return importlib.util.find_spec(mod) is not None


def _brew_installed_set():
    try:
        r = subprocess.run(["brew", "list", "--formula", "-1"],
                           capture_output=True, text=True, check=True)
        return set(r.stdout.strip().splitlines())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return set()


def _brew_install(pkgs):
    brew_path = shutil.which("brew")
    if not brew_path:
        note("Homebrew not found; skipping brew installs.")
        return
    installed = _brew_installed_set()
    SUDO_USER = os.environ.get("SUDO_USER", "")
    for pkg in pkgs:
        if pkg in installed:
            info(f"  ✓ {pkg} already installed")
            continue
        if os.getuid() == 0:
            if not SUDO_USER:
                note(f"Running as root with no SUDO_USER — cannot brew install {pkg}; skipping.")
                continue
            run(["sudo", "-u", SUDO_USER, brew_path, "install", pkg])
        else:
            run([brew_path, "install", pkg])


def _clone_or_update(url, dest):
    dest = Path(dest)
    if dest.exists():
        info(f"Updating {dest.name} …")
        try:
            # Reset local changes so ff-only pull can succeed
            subprocess.run(["git", "-C", str(dest), "checkout", "--", "."],
                           check=False, stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
            run(["git", "-C", str(dest), "pull", "--ff-only"])
        except RuntimeError:
            warn(f"git pull failed for {dest.name}; continuing with existing checkout.")
    else:
        info(f"Cloning {url} → {dest} …")
        dest.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "clone", "--depth=1", url, str(dest)])


# ─── phase 1: system packages ────────────────────────────────────────────────

def install_system_packages(os_type, args):
    step("Phase 1 — System Packages")
    if args.skip_apt:
        note("--skip-system set; skipping.")
        return

    if os_type == "windows":
        warn("Windows detected. Please install dependencies manually.")
        return

    if os_type == "macos":
        _brew_install(BREW_PKGS)
        return

    if os_type == "apt":
        info("Running apt update + apt upgrade …")
        run(["apt-get", "update", "-y"])
        run(["apt-get", "upgrade", "-y"])
        info("Installing APT packages …")
        _needed = [p for p in APT_PKGS if not _dpkg_installed(p)]
        _skip = len(APT_PKGS) - len(_needed)
        if _skip:
            info(f"  {_skip} APT package(s) already installed")
        if _needed:
            run(["apt-get", "install", "-y"] + _needed)

    elif os_type == "dnf":
        info("Installing DNF packages …")
        _needed = [p for p in DNF_PKGS if not _rpm_installed(p)]
        _skip = len(DNF_PKGS) - len(_needed)
        if _skip:
            info(f"  {_skip} DNF package(s) already installed")
        if _needed:
            run(["dnf", "install", "-y"] + _needed)

    elif os_type == "zypper":
        info("Installing zypper packages …")
        _needed = [p for p in ZYPPER_PKGS if not _rpm_installed(p)]
        _skip = len(ZYPPER_PKGS) - len(_needed)
        if _skip:
            info(f"  {_skip} zypper package(s) already installed")
        if _needed:
            run(["zypper", "install", "-y"] + _needed)


# ─── phase 2: pip packages ───────────────────────────────────────────────────

def install_pip_packages(args):
    step("Phase 2 — Pip Packages")
    if args.skip_pip:
        note("--skip-pip set; skipping.")
        return
    pip = _pip_cmd()
    for pkg in PIP_PKGS:
        if _pip_installed(pkg):
            info(f"  ✓ {pkg} already installed")
            continue
        info(f"pip install {pkg} …")
        try:
            run(pip + ["install", "--break-system-packages", pkg])
        except RuntimeError as exc:
            warn(f"pip install failed for {pkg}: {exc}")

    # edgartools (SEC EDGAR) — optional; its pyarrow transitive dep has
    # no pre-built wheel on ARM, so source-building it hangs or OOMs.
    # Use --only-binary to install only if wheels exist for this platform.
    if not _pip_installed("edgartools>=2.0.0"):
        info("pip install edgartools (optional — SEC EDGAR support) …")
        rc = subprocess.run(
            pip + ["install", "--break-system-packages",
                   "--only-binary", ":all:", "edgartools>=2.0.0"],
            timeout=120,
        ).returncode
        if rc != 0:
            note("edgartools skipped — no pre-built wheel for this platform.")
            note("SEC EDGAR lookups will be unavailable (Phase 6 EDGAR).")
        else:
            info("  ✓ edgartools installed")
    else:
        info("  ✓ edgartools>=2.0.0 already installed")

    # maigret — install separately because its deps (networkx, etc.)
    # commonly conflict with system-managed packages.  pipx first
    # (isolated venv, no conflicts), then pip with --ignore-installed
    # as fallback (avoids trying to uninstall system-managed packages).
    if shutil.which("maigret"):
        info("  ✓ maigret already installed")
    else:
        pipx = shutil.which("pipx")
        if not pipx:
            info("Installing pipx for isolated tool installs …")
            try:
                subprocess.run(
                    pip + ["install", "--break-system-packages", "pipx"],
                    check=True, timeout=60,
                )
                pipx = shutil.which("pipx")
            except Exception:
                pass
        if pipx:
            info("Installing maigret via pipx (isolated) …")
            try:
                subprocess.run([pipx, "install", "maigret"],
                               check=True, timeout=180,
                               env={**os.environ, "PIPX_HOME": "/opt/pipx",
                                    "PIPX_BIN_DIR": "/usr/local/bin"})
                if shutil.which("maigret"):
                    info("  ✓ maigret installed via pipx")
            except Exception as exc:
                warn(f"pipx install maigret failed: {exc}")
        if not shutil.which("maigret"):
            info("maigret: falling back to pip with --ignore-installed …")
            try:
                subprocess.run(
                    pip + ["install", "--break-system-packages",
                           "--ignore-installed", "maigret"],
                    check=True, timeout=120,
                )
                if shutil.which("maigret"):
                    info("  ✓ maigret installed via pip")
                else:
                    warn("pip installed maigret package but binary not on PATH")
            except Exception:
                err("maigret install failed — neither pipx nor pip succeeded")

    # Playwright browser + driver (required by python-wappalyzer, maigret).
    # The Python playwright package bundles its own Node.js driver; we just
    # need to download the browser binary and system deps.  On Debian/Kali
    # where playwright is installed via apt, the package depends on
    # node-playwright for the CLI driver — ensure that is present too.
    pw_cmd = [sys.executable, "-m", "playwright"]
    _env = dict(os.environ, DEBIAN_FRONTEND="noninteractive")
    info("Installing Playwright browser + system deps …")
    try:
        subprocess.run(
            pw_cmd + ["install", "--with-deps", "chromium"],
            env=_env, timeout=300, check=True,
        )
        info("  ✓ Playwright chromium installed")
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        note(f"playwright install --with-deps chromium failed: {exc}")
        # Fallback: try install-deps then install separately
        try:
            subprocess.run(pw_cmd + ["install-deps"],
                           env=_env, timeout=120, check=False,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(pw_cmd + ["install", "chromium"],
                           env=_env, timeout=180, check=True)
            info("  ✓ Playwright chromium installed (fallback)")
        except Exception as exc2:
            note(f"Playwright fallback install also failed: {exc2}")

    # On Debian/Kali apt-installed playwright, the Python package references
    # the system Node.js driver at /usr/share/nodejs/playwright/cli.js.
    # Verify it exists; if missing, install the node-playwright apt package.
    _pw_driver_ok = False
    try:
        import playwright._impl._driver as _pw_drv
        _drv_path = _pw_drv.compute_driver_executable()
        _pw_driver_ok = Path(_drv_path).exists()
    except Exception:
        pass
    if not _pw_driver_ok:
        info("Playwright driver not found — attempting to fix …")
        if sys.platform.startswith("linux") and shutil.which("apt-get"):
            try:
                if not _dpkg_installed("node-playwright"):
                    subprocess.run(
                        ["apt-get", "install", "-y", "node-playwright"],
                        env=_env, timeout=120, check=True,
                    )
                info("  ✓ node-playwright installed via apt")
            except Exception as exc:
                warn(f"apt install node-playwright failed: {exc}")
        _npm = shutil.which("npm")
        if _npm and not _pw_driver_ok:
            try:
                subprocess.run(
                    [_npm, "install", "-g", "playwright"],
                    timeout=120, check=True,
                )
                info("  ✓ playwright installed via npm")
            except Exception as exc:
                warn(f"npm install playwright failed: {exc}")
        # Re-check after fix attempts
        try:
            import importlib
            importlib.reload(_pw_drv)
            _drv_path = _pw_drv.compute_driver_executable()
            _pw_driver_ok = Path(_drv_path).exists()
        except Exception:
            pass
        if not _pw_driver_ok:
            note("Playwright driver still not available — wappalyzer will be skipped at runtime")


# ─── phase 3: go tools ───────────────────────────────────────────────────────

def install_go_tools(args):
    step("Phase 3 — Go Tools (go install)")
    if args.skip_go:
        note("--skip-go set; skipping.")
        return

    _ensure_modern_go()

    gb = _go_bin()
    if not shutil.which(gb) and not Path(gb).exists():
        note(f"go binary not found ({gb}); skipping Go tool installs.")
        return

    env = _go_env()
    BIN_DIR.mkdir(parents=True, exist_ok=True)

    for tool in GO_INSTALL_TOOLS:
        name = tool.split("/")[-1].split("@")[0]
        if shutil.which(name):
            info(f"{name} already installed — skipping")
            continue
        info(f"go install {name} …")
        try:
            run([gb, "install", tool], env=env)
        except RuntimeError as exc:
            warn(f"go install failed for {tool}: {exc}")
            # Retry once after clearing module cache for this tool
            info(f"  Retrying {name} with clean module cache …")
            try:
                gopath = env.get("GOPATH", str(Path.home() / "go"))
                cache_dir = Path(gopath) / "pkg" / "mod" / "cache"
                run([gb, "clean", "-modcache"], env=env)
                run([gb, "install", tool], env=env)
                info(f"  ✓ {name} installed on retry")
            except RuntimeError:
                err(f"  {name} failed on retry — check Go version and network")

    # trufflehog v3 has go.mod replace directives, so `go install` fails.
    # Download the pre-built binary from GitHub releases instead.
    install_trufflehog()


def install_trufflehog():
    """Download trufflehog from GitHub releases (go install fails due to replace directives)."""
    if shutil.which("trufflehog"):
        info("trufflehog already installed — skipping")
        return
    if (BIN_DIR / "trufflehog").exists():
        info("trufflehog already at /usr/local/bin — skipping")
        return

    import json
    import tarfile
    import tempfile

    info("Installing trufflehog from GitHub release …")
    api_url = "https://api.github.com/repos/trufflesecurity/trufflehog/releases/latest"
    try:
        result = subprocess.run(
            ["curl", "-fsSL", api_url],
            capture_output=True, text=True, check=True, timeout=30,
        )
        release = json.loads(result.stdout)
    except Exception as exc:
        warn(f"Failed to fetch trufflehog release info: {exc}")
        return

    machine = platform.machine().lower()
    arch_map = {"x86_64": "amd64", "amd64": "amd64", "aarch64": "arm64", "arm64": "arm64"}
    arch = arch_map.get(machine, "amd64")
    system = platform.system().lower()

    # Find the right asset (e.g. trufflehog_3.x.x_linux_amd64.tar.gz)
    asset_url = None
    for asset in release.get("assets", []):
        name = asset["name"].lower()
        if system in name and arch in name and name.endswith(".tar.gz"):
            asset_url = asset["browser_download_url"]
            break

    if not asset_url:
        warn(f"No trufflehog release asset found for {system}/{arch}")
        return

    try:
        with tempfile.TemporaryDirectory() as td:
            tarball = os.path.join(td, "trufflehog.tar.gz")
            subprocess.run(["curl", "-fsSL", "-o", tarball, asset_url],
                           check=True, timeout=120)
            with tarfile.open(tarball, "r:gz") as tf:
                for member in tf.getmembers():
                    if member.name == "trufflehog" or member.name.endswith("/trufflehog"):
                        member.name = "trufflehog"
                        tf.extract(member, td)
                        break
            src = os.path.join(td, "trufflehog")
            if os.path.isfile(src):
                dst = str(BIN_DIR / "trufflehog")
                subprocess.run(["install", "-m", "0755", src, dst], check=True)
                info(f"trufflehog installed to {dst}")
            else:
                warn("trufflehog binary not found in release tarball")
    except Exception as exc:
        warn(f"trufflehog install failed: {exc}")


# ─── phase 4: git tools ──────────────────────────────────────────────────────

def install_git_tools(args):
    step("Phase 4 — Git Tools")
    if args.skip_git:
        note("--skip-git set; skipping.")
        return

    pip = _pip_cmd()
    gb  = _go_bin()
    env = _go_env()

    for tool in GIT_TOOLS:
        name   = tool["name"]
        url    = tool["url"]
        dest   = Path(tool["dest"])
        action = tool.get("action")

        info(f"[git] {name}")
        try:
            _clone_or_update(url, dest)
        except RuntimeError as exc:
            warn(f"Clone/update failed for {name}: {exc}; skipping.")
            continue

        if action is None:
            continue

        try:
            if action == "pip_install_dot":
                run(pip + ["install", "--break-system-packages", "."], cwd=dest)

            elif action == "pip_install_requirements":
                req = dest / "requirements.txt"
                if req.exists():
                    run(pip + ["install", "--break-system-packages", "-r", str(req)], cwd=dest)
                else:
                    warn(f"requirements.txt not found in {dest}")

            elif action == "pip_install_requirements_base":
                req = dest / "requirements" / "base.txt"
                if req.exists():
                    run(pip + ["install", "--break-system-packages", "-r", str(req)], cwd=dest)
                else:
                    warn(f"requirements/base.txt not found in {dest}")

            elif action == "chmod_executable":
                # Make all .py files in dest executable
                for py in dest.glob("*.py"):
                    py.chmod(py.stat().st_mode | 0o755)
                    info(f"  chmod +x {py}")

            elif action == "go_build":
                run([gb, "build", "./..."], cwd=dest, env=env)

            elif action == "go_build_output":
                output  = tool.get("output", f"/usr/local/bin/{name.lower()}")
                go_args = tool.get("go_args", ["./..."])
                run([gb, "build", "-o", output] + go_args, cwd=dest, env=env)

        except RuntimeError as exc:
            if action == "pip_install_dot" and name.lower() == "theharvester":
                note(f"pip install . failed for {name}: {exc} — trying PyPI fallback …")
                try:
                    run(pip + ["install", "--break-system-packages", "theHarvester"], cwd=None)
                    info(f"  ✓ {name} installed from PyPI")
                except RuntimeError:
                    req = dest / "requirements.txt"
                    if req.exists():
                        try:
                            run(pip + ["install", "--break-system-packages", "-r", str(req)], cwd=dest)
                            info(f"  ✓ {name} requirements installed")
                        except RuntimeError:
                            pass
                    note(f"Post-clone action failed for {name} — tool may have reduced functionality")
            else:
                warn(f"Post-clone action failed for {name}: {exc}")

    # Create symlinks for git tools that aren't installed to PATH
    _create_tool_symlinks()


def _create_tool_symlinks():
    """Create /usr/local/bin symlinks for git-cloned tools without pip entry points."""
    symlinks = {
        "cloud_enum":      OPT_DIR / "cloud_enum" / "cloud_enum.py",
        "EmailHarvester":  OPT_DIR / "EmailHarvester" / "EmailHarvester.py",
    }
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    for link_name, target in symlinks.items():
        link_path = BIN_DIR / link_name
        if not target.exists():
            note(f"Target {target} not found; skipping symlink {link_name}.")
            continue
        # Ensure executable
        target.chmod(target.stat().st_mode | 0o755)
        if link_path.is_symlink() or link_path.exists():
            link_path.unlink()
        link_path.symlink_to(target)
        info(f"Symlink: {link_path} → {target}")

    _fix_emailharvester_plugins()


def _fix_emailharvester_plugins():
    """Ensure EmailHarvester can find its plugins directory.

    EmailHarvester uses os.path.abspath(__file__) (NOT realpath) to locate
    plugins/.  When the entry-point is a symlink at /usr/local/bin/,
    abspath resolves to /usr/local/bin/ and the script tries to load
    /usr/local/bin/plugins/ which doesn't exist.  Fix: symlink plugins/
    next to the SYMLINK (abspath directory), not the resolved target.
    """
    eh_bin = BIN_DIR / "EmailHarvester"
    src_plugins = OPT_DIR / "EmailHarvester" / "plugins"
    if not src_plugins.is_dir():
        note("EmailHarvester plugins/ not found in /opt/EmailHarvester/; skipping fix.")
        return

    if eh_bin.exists() or eh_bin.is_symlink():
        abspath_dir = Path(os.path.abspath(str(eh_bin))).parent
        target_plugins = abspath_dir / "plugins"
        if target_plugins.is_dir() and not target_plugins.is_symlink():
            info(f"EmailHarvester plugins/ already present at {target_plugins}")
            return
        if not target_plugins.exists():
            target_plugins.symlink_to(src_plugins)
            info(f"Symlink: {target_plugins} → {src_plugins}")
        elif target_plugins.is_symlink():
            target_plugins.unlink()
            target_plugins.symlink_to(src_plugins)
            info(f"Symlink (refreshed): {target_plugins} → {src_plugins}")
        resolved = Path(os.path.realpath(str(eh_bin)))
        resolved_dir = resolved.parent
        if resolved_dir != abspath_dir and resolved_dir != src_plugins.parent:
            rp = resolved_dir / "plugins"
            if not rp.exists():
                rp.symlink_to(src_plugins)
                info(f"Symlink (realpath fallback): {rp} → {src_plugins}")


# ─── symlinks ────────────────────────────────────────────────────────────────

def install_symlinks():
    step("Creating Symlinks")
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    for link_name, target in SYMLINKS.items():
        link_path = BIN_DIR / link_name
        if not target.exists():
            note(f"Target {target} not found; skipping symlink {link_name}.")
            continue
        if link_path.is_symlink() or link_path.exists():
            link_path.unlink()
        # Ensure the target script is executable
        target.chmod(target.stat().st_mode | 0o755)
        link_path.symlink_to(target)
        info(f"Symlink: {link_path} → {target}")


# ─── check mode ──────────────────────────────────────────────────────────────

def run_check():
    step("Check Mode — Dependency Status")
    all_ok = True

    for tool in VERIFY_BINS:
        path = shutil.which(tool)
        if path:
            info(f"{tool:22s} {G}OK{W}  ({path})")
        else:
            err(f"{tool:22s} {R}MISSING{W}")
            all_ok = False

    for mod in VERIFY_MODS:
        ok = run_ok([sys.executable, "-c", f"import {mod}"])
        status = f"{G}OK{W}" if ok else f"{R}MISSING{W}"
        marker = f"python:{mod}"
        if ok:
            info(f"{marker:22s} {status}")
        else:
            err(f"{marker:22s} {status}")
            all_ok = False

    # File-path tools
    for name, fpath in VERIFY_FILES.items():
        ok = os.path.isfile(fpath) and os.access(fpath, os.X_OK)
        if ok:
            info(f"{name:22s} {G}OK{W}  ({fpath})")
        else:
            err(f"{name:22s} {R}MISSING{W}  ({fpath})")
            all_ok = False

    # Symlinks
    for name, target in SYMLINKS.items():
        link = BIN_DIR / name
        ok = link.is_symlink()
        status = f"{G}OK{W}" if ok else f"{Y}MISSING{W}"
        print(f"  {'symlink:'+name:22s} {status}")

    # EmailHarvester plugins reachability
    eh_bin = BIN_DIR / "EmailHarvester"
    if eh_bin.exists() or eh_bin.is_symlink():
        resolved_dir = Path(os.path.realpath(str(eh_bin))).parent
        plugins_ok = (resolved_dir / "plugins").is_dir()
        label = "EH-plugins"
        if plugins_ok:
            info(f"{label:22s} {G}OK{W}  ({resolved_dir / 'plugins'})")
        else:
            err(f"{label:22s} {R}MISSING{W}  (plugins/ not found at {resolved_dir})")
            all_ok = False

    print()
    if all_ok:
        info(f"{G}All checks passed.{W}")
    else:
        warn(f"{Y}Some checks failed.{W}")
    return all_ok


# ─── post-install summary ────────────────────────────────────────────────────

def post_install_summary():
    step("Post-Install Verification Summary")
    results = []

    for tool in VERIFY_BINS:
        path = shutil.which(tool)
        results.append((tool, bool(path), path or "missing"))

    for mod in VERIFY_MODS:
        ok = run_ok([sys.executable, "-c", f"import {mod}"])
        results.append((f"python:{mod}", ok, "installed" if ok else "missing"))

    for name, fpath in VERIFY_FILES.items():
        ok = os.path.isfile(fpath) and os.access(fpath, os.X_OK)
        results.append((f"file:{name}", ok, fpath if ok else "missing"))

    for name, target in SYMLINKS.items():
        link = BIN_DIR / name
        ok = link.is_symlink()
        results.append((f"symlink:{name}", ok, str(link) if ok else "missing"))

    eh_bin = BIN_DIR / "EmailHarvester"
    if eh_bin.exists() or eh_bin.is_symlink():
        resolved_dir = Path(os.path.realpath(str(eh_bin))).parent
        plugins_ok = (resolved_dir / "plugins").is_dir()
        results.append(("EH-plugins", plugins_ok,
                         str(resolved_dir / "plugins") if plugins_ok else "missing"))

    pad = max(len(r[0]) for r in results) + 2
    print()
    for label, ok, detail in results:
        status = f"{G}OK{W}" if ok else f"{R}FAIL{W}"
        print(f"  {label:<{pad}} {status}  {detail}")

    failed = [r for r in results if not r[1]]
    print()
    if not failed:
        info(f"{G}OSift installation complete and verified.{W}")
        info(f"Run with: {C}osift{W}  (or  python3 {APP_DIR}/osift.py)")
    else:
        warn(f"{Y}{len(failed)} item(s) need attention (see above).{W}")


# ─── main ─────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(
        description=f"Installer for {APP_NAME}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--skip-apt",    "--skip-system", dest="skip_apt",
                   action="store_true", help="Skip system package installation")
    p.add_argument("--skip-pip",    action="store_true",
                   help="Skip pip package installation")
    p.add_argument("--skip-go",     action="store_true",
                   help="Skip Go tools installation")
    p.add_argument("--skip-git",    action="store_true",
                   help="Skip git tool cloning and builds")
    p.add_argument("--check",       action="store_true",
                   help="Check dependencies without installing")
    return p.parse_args()


def fix_amass_data_dir():
    """Ensure the Amass data directory is owned by the real user.
    The installer runs as root, but amass at runtime runs as the real
    user and fails with exit 1 if it can't write to its data dir.
    Linux: ~/.config/amass   macOS: ~/Library/Application Support/amass
    """
    real_user = os.environ.get("SUDO_USER", "")
    if not real_user:
        return  # not running under sudo, nothing to fix

    real_home = Path(f"/home/{real_user}")
    if not real_home.exists():
        real_home = Path(f"/Users/{real_user}")  # macOS
    if not real_home.exists():
        return

    system = platform.system()
    if system == "Darwin":
        data_dir = real_home / "Library" / "Application Support" / "amass"
    else:
        data_dir = real_home / ".config" / "amass"

    if data_dir.exists():
        st = data_dir.stat()
        import pwd
        try:
            real_uid = pwd.getpwnam(real_user).pw_uid
            real_gid = pwd.getpwnam(real_user).pw_gid
        except KeyError:
            warn(f"Could not resolve uid for {real_user}; skipping amass dir fix.")
            return
        if st.st_uid != real_uid:
            info(f"Fixing amass data dir ownership → {real_user}")
            subprocess.run(["chown", "-R", f"{real_user}:{real_gid}", str(data_dir)],
                           check=False)
    else:
        # Pre-create it as the real user so amass doesn't create it as root
        info(f"Pre-creating amass data dir for {real_user}")
        data_dir.mkdir(parents=True, exist_ok=True)
        import pwd
        try:
            real_uid = pwd.getpwnam(real_user).pw_uid
            real_gid = pwd.getpwnam(real_user).pw_gid
            os.chown(str(data_dir), real_uid, real_gid)
        except (KeyError, OSError) as exc:
            warn(f"Could not set amass dir ownership: {exc}")


def _check_prereqs():
    REQUIRED = [
        ("git",  "git — required for cloning dependencies"),
        ("pip3", "pip3 — required for Python packages (apt: python3-pip)"),
    ]
    missing = []
    for binary, desc in REQUIRED:
        if not shutil.which(binary):
            missing.append(f"  ✗ {binary}  ({desc})")
    if missing:
        print("\nERROR: Missing required prerequisites:\n")
        for m in missing:
            print(m)
        print("\nInstall them first, then re-run install.py.\n")
        sys.exit(1)


def main():
    banner()
    args = parse_args()
    _check_prereqs()
    os_type = detect_os()
    info(f"Detected OS type: {os_type}")

    if args.check:
        ok = run_check()
        sys.exit(0 if ok else 1)

    if os_type == "windows":
        err("OSift is designed for Unix-like systems. Windows is not supported.")
        sys.exit(1)

    require_root()

    # Phase 1 — system packages
    install_system_packages(os_type, args)

    # Phase 2 — pip packages
    install_pip_packages(args)

    # Phase 3 — Go tools
    install_go_tools(args)

    # Phase 4 — Git tools
    install_git_tools(args)

    # Fix Amass data directory ownership (installer runs as root but
    # Amass needs the data dir writable by the real user at runtime)
    fix_amass_data_dir()

    # Symlinks
    install_symlinks()

    # Summary
    post_install_summary()


if __name__ == "__main__":
    main()
