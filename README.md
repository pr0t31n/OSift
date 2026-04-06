# OSift

**Comprehensive OSINT & reconnaissance framework** — domain-level passive recon through M365 credential spray and GitHub secret scanning, in a single script.

OSift takes a company name and domain, and runs a structured 13-phase intelligence pipeline: DNS enumeration, subdomain discovery, certificate harvesting, IP intelligence, WHOIS, company and employee OSINT, web crawling, API-enriched attack surface mapping, ProjectDiscovery toolkit sweep, M365 credential spraying (TREVORspray), and GitHub secret scanning (GitDorker). All results are deduplicated and written to structured JSON/CSV output for direct import into Vantage or security reports.

---

## Features

- **13-phase structured pipeline** — DNS enumeration through GitHub dorking, each phase building on previous results. Phases gate on prior findings to avoid redundant tool runs.
- **30+ tool integrations** — theHarvester, xurlfind3r, amass, puredns, subfinder, dnsx, shuffledns, katana, httpx, naabu, tlsx, cdncheck, uncover, cloudlist, waybackurls, Wappalyzer, maigret, TruffleHog, cloud_enum, EmailHarvester, Shodan CLI, TREVORspray, GitDorker, and more.
- **10+ API integrations** — Shodan, Censys, FullHunt, SecurityTrails, Netlas, VirusTotal, URLScan.io, AlienVault OTX, Hunter.io, Have I Been Pwned, Dehashed, ProjectDiscovery Chaos, FOFA, Quake360, ZoomEye, CriminalIP.
- **Scan resumption** — `checkpoint.json` tracks every completed phase. Re-running with the same output directory skips already-finished work.
- **Vantage integration** — Set `VANTAGE_MANAGED=1` to emit structured protocol tokens for the [Vantage](../vantage/) web UI. All output streams switch to JSON protocol messages; phases report live status.
- **Fingerprint-based deduplication** — `FindingStore` uses 16-hex SHA fingerprints to deduplicate findings across all 30+ tools.
- **Auto-install** — ProjectDiscovery tools are auto-installed via `go install` if Go is present. Python dependencies are detected and offered for auto-install at startup.
- **Cross-platform** — Linux, macOS, Windows. Requires elevated privileges (root/Administrator).
- **Settings file** — All API keys, targets, and scan options persist in a single `osift_settings.json` file across engagements.

---

## Scan Phases

| # | Phase | Tools / Sources | Notes |
|---|-------|-----------------|-------|
| 1 | **DNS Enumeration** | dig, nslookup, host, dnspython, zone transfer | A, AAAA, MX, NS, TXT, SRV, DMARC, SPF, DKIM |
| 1.5-A | **Passive OSINT Wave A** | theHarvester (40+ sources), xurlfind3r | Concurrent with Phase 1 and Amass |
| 2 | **Subdomain Discovery** | Amass (passive + active), certificate CT logs | Concurrent with Phase 1 |
| 1.5-B | **Passive OSINT Wave B** | puredns (DNS brute-force), waybackurls | After subdomain collection |
| 3 | **Certificate Collection** | crt.sh, Certspotter, Facebook CT | SAN/CN parsing, cert chain analysis |
| 4 | **IP Intelligence** | PTR lookups, ASN mapping, geolocation, BGP data | Cloud/CDN detection |
| 4.5 | **Shodan CLI** | shodan CLI per-IP scan | Open ports, banners, CVEs per host |
| 5 | **WHOIS** | python-whois, manual WHOIS query | Registrar, nameservers, abuse contacts |
| 6 | **Company Intelligence** | LinkedIn, Crunchbase, EDGAR SEC filings, Maltego seed | Org structure, subsidiaries, executives |
| 7 | **Email & People OSINT** | Hunter.io, HIBP, Dehashed, maigret, EmailHarvester, TruffleHog | Employee emails, breach exposure, social profiles |
| 8 | **Web Crawling** | katana (JS-aware), sensitive file detection | URLs, forms, secrets in page content |
| 1.5-C | **Tech Fingerprinting** | Wappalyzer, cloud_enum | Tech stack per host, S3/Azure/GCP bucket enum |
| 10 | **OSINT API Engine** | Shodan, Censys, FullHunt, SecurityTrails, Netlas, VirusTotal, URLScan, OTX | Attack surface, threat intel, reputation, passive DNS |
| PD | **ProjectDiscovery Toolkit** | subfinder, chaos, shuffledns, dnsx, httpx, naabu, tlsx, cdncheck, katana, asnmap, uncover, cloudlist | Full PD sweep: subdomains → live hosts → TLS → open ports → cloud assets |
| 11 | **DNS Enrichment** | dig, dnsx | Per-IP PTR, A, AAAA, CNAME resolution for all confirmed subdomains |
| 9 | **Aggregation & Final Report** | IntelAggregator, RawOutputParser, SubdomainConfirmer | Cross-tool deduplication, subdomain liveness confirmation |
| 12 | **M365 Credential Spray** | TREVORspray | Azure AD credential spray against confirmed O365 tenants |
| 13 | **GitHub Secret Scanning** | GitDorker | Dork GitHub for org secrets, API keys, credentials |

---

## Requirements

### Python
- Python 3.10+
- Root / Administrator privileges required
- `requests`, `dnspython`, `python-whois`, `colorama` (required; auto-installed on first run)
- `selenium`, `beautifulsoup4`, `openpyxl` (optional; auto-installed on prompt)

### Go (for ProjectDiscovery tools)
- Go 1.21+ recommended
- ProjectDiscovery tools are auto-installed via `go install` on first run if Go is present

### External tools

The following tools are detected at runtime. Missing tools are skipped gracefully with a warning.

| Tool | Purpose |
|------|---------|
| `amass` | Passive + active subdomain enumeration |
| `theHarvester` | Emails, subdomains, IPs from 40+ passive sources |
| `puredns` | DNS brute-force with wildcard filtering |
| `waybackurls` | Wayback Machine URL extraction |
| `xurlfind3r` | Passive URL discovery (Wayback, CommonCrawl, OTX, GitHub) |
| `maigret` | Social profile OSINT by username |
| `trufflehog` | Secret scanning across git history and web |
| `cloud_enum` | Cloud bucket enumeration (S3, Azure Blob, GCP) |
| `wappalyzer` | Technology fingerprinting (CLI) |
| `shodan` | Shodan CLI for per-IP open-port enumeration |
| `TREVORspray` | M365/Azure AD credential spray |
| `GitDorker` | GitHub dork-based secret scanning |
| `subfinder` | Fast passive subdomain discovery (ProjectDiscovery) |
| `httpx` | HTTP probing and tech detection (ProjectDiscovery) |
| `dnsx` | DNS resolution and enrichment (ProjectDiscovery) |
| `shuffledns` | Massdns-based subdomain brute-force (ProjectDiscovery) |
| `naabu` | Port scanner (ProjectDiscovery) |
| `tlsx` | TLS certificate enumeration (ProjectDiscovery) |
| `cdncheck` | CDN/WAF/cloud provider detection (ProjectDiscovery) |
| `katana` | Web crawler with JS rendering (ProjectDiscovery) |
| `asnmap` | ASN-to-IP-range mapping (ProjectDiscovery) |
| `uncover` | Multi-engine internet-wide search (ProjectDiscovery) |
| `cloudlist` | Cloud asset enumeration across providers (ProjectDiscovery) |
| `chaos` | ProjectDiscovery Chaos subdomain dataset |

---

## Installation

No installation required. Clone or copy the script and run it directly.

```bash
git clone https://github.com/yourorg/osift
cd osift
sudo python3 OSift.py -c "Acme Corp" -d acme.com
```

Python dependencies are detected at startup and offered for auto-install. ProjectDiscovery tools are auto-installed via `go install` if Go is available.

---

## Usage

### Quick start

```bash
# Basic scan — company name and domain
sudo python3 OSift.py -c "Acme Corp" -d acme.com

# With API keys passed inline
sudo python3 OSift.py -c "Acme Corp" -d acme.com \
  --shodan-key YOUR_KEY --virustotal-key YOUR_KEY --hunter-key YOUR_KEY

# Skip slow phases for a quick pass
sudo python3 OSift.py -c "Acme Corp" -d acme.com --skip-amass --skip-brute --skip-api

# Resume an interrupted scan
sudo python3 OSift.py -c "Acme Corp" -d acme.com --output-base acme_2026/
```

### Settings file

Store API keys and defaults once per engagement:

```bash
# Edit osift_settings.json (template shown below)
sudo python3 OSift.py --settings osift_settings.json
```

CLI arguments always override settings file values.

### Common flags

| Flag | Description |
|------|-------------|
| `-c COMPANY` | Company name (required) |
| `-d DOMAIN` | Primary domain (required) |
| `--settings FILE` | Load API keys and defaults from JSON settings file |
| `--output-base DIR` | Override base output directory path |
| `--max-pages N` | Max pages to crawl per host (default: 200) |
| `--max-depth N` | Max crawl depth (default: 3) |
| `--wordlist FILE` | Custom wordlist for DNS brute-force |
| `--skip-crawl` | Skip web crawling |
| `--skip-amass` | Skip Amass enumeration |
| `--skip-brute` | Skip DNS brute-forcing |
| `--skip-api` | Skip Phase 10 OSINT API intelligence entirely |
| `--skip-dns-enrich` | Skip Phase 11 DNS enrichment |
| `--no-spray` | Skip Phase 12 TREVORspray credential spraying |
| `--no-gitdorker` | Skip Phase 13 GitDorker GitHub secret scanning |
| `--github-token TOKEN` | GitHub personal access token for GitDorker |
| `--hibp-key KEY` | Have I Been Pwned API key (domain search) |
| `--dehashed-user EMAIL` | Dehashed account email |
| `--dehashed-key KEY` | Dehashed API key |
| `--shodan-key KEY` | Shodan API key |
| `--censys-id ID` | Censys API ID |
| `--censys-secret SECRET` | Censys API secret |
| `--securitytrails-key KEY` | SecurityTrails API key |
| `--netlas-key KEY` | Netlas API key |
| `--virustotal-key KEY` | VirusTotal API key |
| `--hunter-key KEY` | Hunter.io API key |
| `--chaos-key KEY` | ProjectDiscovery Chaos API key |

---

## Settings File

The settings file allows API keys and scan options to be persisted across engagements.

```json
{
  "target": {
    "company": "Acme Corporation",
    "domain":  "acme.com"
  },
  "scan_options": {
    "max_pages":   200,
    "max_depth":   3,
    "skip_crawl":  false,
    "skip_amass":  false,
    "skip_brute":  false,
    "skip_api":    false,
    "skip_pd":     false,
    "wordlist":    "",
    "output_base": ""
  },
  "breach_intelligence": {
    "hibp_key":      "YOUR_HIBP_KEY",
    "dehashed_user": "you@firm.example",
    "dehashed_key":  "YOUR_DEHASHED_KEY"
  },
  "api_tier1_infrastructure": {
    "shodan_key":         "YOUR_SHODAN_KEY",
    "censys_id":          "YOUR_CENSYS_ID",
    "censys_secret":      "YOUR_CENSYS_SECRET",
    "fullhunt_key":       "YOUR_FULLHUNT_KEY",
    "securitytrails_key": "YOUR_ST_KEY",
    "netlas_key":         "YOUR_NETLAS_KEY"
  },
  "api_tier2_threat_intel": {
    "virustotal_key": "YOUR_VT_KEY",
    "urlscan_key":    "",
    "otx_key":        ""
  },
  "api_tier3_email_people": {
    "hunter_key": "YOUR_HUNTER_KEY"
  },
  "projectdiscovery": {
    "chaos_key":        "YOUR_CHAOS_KEY",
    "cloudlist_config": ""
  },
  "uncover_engine_env_vars": {
    "FOFA_EMAIL":         "",
    "FOFA_KEY":           "",
    "QUAKE_TOKEN":        "",
    "ZOOMEYE_API_KEY":    "",
    "NETLAS_API_KEY":     "YOUR_NETLAS_KEY",
    "CRIMINALIP_API_KEY": ""
  }
}
```

> **Security:** Never commit `osift_settings.json` to version control. Add it to `.gitignore`.

---

## Output Structure

```
<output_dir>/
├── dns/                        DNS records per domain (JSON)
│   ├── records/                A, AAAA, MX, NS, TXT, SRV per host
│   └── zone_transfers/         Zone transfer attempt results
├── subdomains/                 Subdomain discovery results
│   ├── amass.json              Amass output
│   └── puredns/                Brute-force results
├── certs/                      Certificate transparency results
│   └── parsed/                 Parsed SAN/CN per host
├── ip_intelligence/            IP summary, ASN, geolocation
├── whois/                      WHOIS records per domain
├── company/                    Company intelligence (EDGAR, LinkedIn, Maltego seed)
├── email/                      Email OSINT (Hunter.io, HIBP, maigret)
│   └── breach_data/            HIBP + Dehashed breach results
├── osint/
│   ├── theharvester/           theHarvester JSON + XML
│   ├── xurlfind3r/             URL discovery results
│   ├── waybackurls/            Wayback Machine URL dump
│   ├── wappalyzer/             Tech stack per host
│   └── cloud_enum/             Cloud bucket enumeration
├── web/                        Crawled pages, sensitive data hits
├── shodan/                     Shodan CLI per-IP results
├── projectdiscovery/           PD tool results (subfinder, httpx, dnsx, naabu, etc.)
├── spray/                      TREVORspray M365 results
├── gitdorker/                  GitDorker GitHub secret scan results
├── reports/
│   ├── findings_vantage.json   ← Vantage-compatible findings (primary)
│   ├── findings_report.json    ← Unified deduplicated findings
│   ├── final_report.json       ← Full machine-readable report
│   ├── subdomains_confirmed.csv← Live confirmed subdomains
│   ├── targets_osint.json      ← Enriched target IP/host map
│   └── tools_used.json         ← Tool availability log
├── scan.log                    Human-readable progress log
├── scan.log.json               Structured JSON log
├── errors.log                  Tool errors and exceptions
└── checkpoint.json             Scan resumption state
```

### findings_vantage.json schema

```json
[
  {
    "title":       "Subdomain Takeover Risk",
    "severity":    "HIGH",
    "type":        "subdomain",
    "host":        "staging.acme.com",
    "port":        null,
    "hostname":    "staging.acme.com",
    "tool":        "subfinder",
    "evidence":    "CNAME points to unclaimed S3 bucket",
    "cves":        [],
    "scope":       "external",
    "ts":          "2026-04-07T09:14:22"
  }
]
```

Severity values: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO`

---

## Vantage Integration

When launched by [Vantage](../vantage/) (`VANTAGE_MANAGED=1`), OSift switches to structured protocol output:

| Token | Purpose |
|-------|---------|
| `__VANTAGE_LOG__:` | Standard log line forwarded to UI console |
| `__VANTAGE_ERR__:` | Error line forwarded to UI |
| `__VANTAGE_STATUS__:` | Phase progress update |
| `__VANTAGE_PROMPT__:` | Interactive prompt requiring user response |

Dependency installs are non-interactive (auto-approved). Phase status is reported live so the Vantage UI can track progress in real time.

---

## Notes

- **Elevated privileges are required** — OSift exits early with an actionable message if not run as root (Linux/macOS) or Administrator (Windows).
- **Scan resumption** — Re-running against the same output directory resumes from the last completed phase. Partial phase results are discarded and re-run.
- **FindingStore deduplication** — All findings are keyed on a 16-hex SHA fingerprint derived from `(title, host, port, tool)`. Duplicate findings from overlapping tools are merged automatically.
- **ProjectDiscovery tools** — Auto-installed via `go install` into `$GOPATH/bin`. If Go is not present, PD phases are skipped gracefully.
- **TREVORspray (Phase 12)** — Only runs against targets where O365 tenant discovery succeeds. Skip with `--no-spray`.
- **GitDorker (Phase 13)** — Requires a GitHub personal access token (`--github-token`). Skip with `--no-gitdorker`.
- **`uncover` engines** — Each engine (FOFA, Quake360, ZoomEye, CriminalIP) only queries if its API key is present in the settings file or environment.
- All tool timeouts are hardened defaults. Long-running tools (amass, puredns, katana) default to 300–600 seconds.

---

## Contributors

OSift integrates and depends on the following external tools and Python libraries. Full credit to their authors and maintainers.

### External Tools

| Tool | Author / Organisation | Handle | Link |
|------|-----------------------|--------|------|
| dnsx | ProjectDiscovery | @projectdiscovery | https://github.com/projectdiscovery/dnsx |
| subfinder | ProjectDiscovery | @projectdiscovery | https://github.com/projectdiscovery/subfinder |
| httpx | ProjectDiscovery | @projectdiscovery | https://github.com/projectdiscovery/httpx |
| nuclei | ProjectDiscovery | @projectdiscovery | https://github.com/projectdiscovery/nuclei |
| naabu | ProjectDiscovery | @projectdiscovery | https://github.com/projectdiscovery/naabu |
| tlsx | ProjectDiscovery | @projectdiscovery | https://github.com/projectdiscovery/tlsx |
| cdncheck | ProjectDiscovery | @projectdiscovery | https://github.com/projectdiscovery/cdncheck |
| katana | ProjectDiscovery | @projectdiscovery | https://github.com/projectdiscovery/katana |
| asnmap | ProjectDiscovery | @projectdiscovery | https://github.com/projectdiscovery/asnmap |
| uncover | ProjectDiscovery | @projectdiscovery | https://github.com/projectdiscovery/uncover |
| cloudlist | ProjectDiscovery | @projectdiscovery | https://github.com/projectdiscovery/cloudlist |
| shuffledns | ProjectDiscovery | @projectdiscovery | https://github.com/projectdiscovery/shuffledns |
| chaos-client | ProjectDiscovery | @projectdiscovery | https://github.com/projectdiscovery/chaos-client |
| amass | OWASP / Jeff Foley | @caffix | https://github.com/owasp-amass/amass |
| theHarvester | Christian Martorella | @laramies | https://github.com/laramies/theHarvester |
| ffuf | Joohoi | @joohoi | https://github.com/ffuf/ffuf |
| waybackurls | Tom Hudson | @tomnomnom | https://github.com/tomnomnom/waybackurls |
| TREVORspray | Black Lantern Security | @blacklanternsecurity | https://github.com/blacklanternsecurity/TREVORspray |
| GitDorker | obheda12 | @obheda12 | https://github.com/obheda12/GitDorker |
| trufflehog | Truffle Security | @trufflesecurity | https://github.com/trufflesecurity/trufflehog |
| puredns | d3mondev | @d3mondev | https://github.com/d3mondev/puredns |
| xurlfind3r | hueristiq | @hueristiq | https://github.com/hueristiq/xurlfind3r |
| maigret | soxoj | @soxoj | https://github.com/soxoj/maigret |
| cloud_enum | initstring | @initstring | https://github.com/initstring/cloud_enum |
| whatweb | urbanadventurer | @urbanadventurer | https://github.com/urbanadventurer/WhatWeb |
| shodan CLI | Shodan.io / John Matherly | @achillean | https://github.com/achillean/shodan-python |

### Python Libraries

| Library | Author / Organisation | Link |
|---------|-----------------------|------|
| requests | Kenneth Reitz / Python Software Foundation | https://github.com/psf/requests |
| urllib3 | Andrey Petrov / urllib3 contributors | https://github.com/urllib3/urllib3 |
| dnspython | Bob Halley / dnspython contributors | https://github.com/rthalley/dnspython |
| python-whois | drtey / Jochen Kupperschmidt | https://github.com/DannyCork/python-whois |
| shodan (Python SDK) | Shodan.io / John Matherly @achillean | https://github.com/achillean/shodan-python |
| censys | Censys Inc. | https://github.com/censys/censys-python |
| beautifulsoup4 | Leonard Richardson | https://www.crummy.com/software/BeautifulSoup/ |
| lxml | Stefan Behnel / lxml developers | https://github.com/lxml/lxml |
| cryptography | The Python Cryptographic Authority (PyCA) | https://github.com/pyca/cryptography |
| pyOpenSSL | Jean-Paul Calderone / PyCA | https://github.com/pyca/pyopenssl |
| colorama | Jonathan Hartley | https://github.com/tartley/colorama |
| tqdm | Casper da Costa-Luis / tqdm contributors | https://github.com/tqdm/tqdm |
| paramiko | Jeff Forcier / paramiko contributors | https://github.com/paramiko/paramiko |
| python-docx | Steve Canny | https://github.com/python-openxml/python-docx |
| openpyxl | Eric Gazoni / Charlie Clark | https://github.com/theorchard/openpyxl |
| pandas | Wes McKinney / pandas contributors | https://github.com/pandas-dev/pandas |
| jinja2 | Armin Ronacher / Pallets | https://github.com/pallets/jinja |
| edgartools | Dwight Gunning / dgunning | https://github.com/dgunning/edgartools |
| selenium | Selenium HQ contributors | https://github.com/SeleniumHQ/selenium |

### API / Data Sources

| Service | Organisation | Link |
|---------|-------------|------|
| Shodan | Shodan.io | https://www.shodan.io |
| Censys | Censys Inc. | https://censys.io |
| FullHunt | FullHunt | https://fullhunt.io |
| SecurityTrails | SecurityTrails | https://securitytrails.com |
| Netlas | Netlas.io | https://netlas.io |
| VirusTotal | Google / VirusTotal | https://www.virustotal.com |
| URLScan.io | URLScan GmbH | https://urlscan.io |
| AlienVault OTX | AT&T Cybersecurity | https://otx.alienvault.com |
| Hunter.io | Hunter.io | https://hunter.io |
| Have I Been Pwned | Troy Hunt @troyhunt | https://haveibeenpwned.com |
| DeHashed | DeHashed | https://www.dehashed.com |
| ProjectDiscovery Chaos | ProjectDiscovery @projectdiscovery | https://chaos.projectdiscovery.io |
