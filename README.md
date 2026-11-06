<details>
<summary><strong>FULL DISCLOSURE</strong> — AI Development & Legal Notice</summary>

---

### AI Development Disclosure

This tool is part of the **pr0t31n toolkit**, a collection of security testing and penetration testing automation tools. The toolkit was created through AI-assisted development, guided by the professional experience and domain expertise of a cybersecurity consultant and penetration tester. Ya, I named it after myself - but to be fair, AI is horrible at naming things.

**The pr0t31n toolkit exists to serve two purposes:**

1. **Automate repetitive penetration testing workflow steps.** Security assessments involve significant amounts of repetitive, procedural work — running sequential tool chains, parsing outputs, correlating findings across tools, and managing engagement data. Automating these steps frees testers to focus on the work that requires human judgment: manual testing, creative attack paths, analysis, and reporting.

2. **Demonstrate the benefits and failures of AI-assisted development.** This toolkit is a real-world case study in building production security tooling with AI assistance. It demonstrates both what AI-assisted development can accomplish and where it falls short. The quality of AI-generated code varies significantly — between context refreshes, the output can range from senior/principal-level software engineering to the work of a still-in-school intern. This inconsistency is itself part of the demonstration.

In the interest of transparency, every tool in the pr0t31n toolkit carries this disclosure. The creator believes that AI-assisted development should be acknowledged openly, not concealed. Users, reviewers, and anyone examining this code should know how it was built so they can evaluate it accordingly.

---

### Legal & Authorization Notice

> **⚠ WARNING: AUTHORIZED USE ONLY**

This tool is designed and intended **exclusively** for use in **authorized security testing engagements**. "Authorized" means **all** of the following conditions are met:

- **Explicit Written Permission.** You possess explicit, documented, written authorization from the owner or authorized representative of the target system(s), network(s), or application(s) to conduct security testing. Verbal agreements are not sufficient.
- **Defined Scope.** The authorization clearly defines the scope of testing, including which systems, networks, IP ranges, applications, and/or endpoints are included. You must not exceed the boundaries of this defined scope under any circumstances.
- **Defined Timeframe.** The authorization specifies the dates and times during which testing is permitted. Testing outside the authorized window is unauthorized testing.
- **Rules of Engagement.** You are operating under a set of rules of engagement (RoE) or equivalent governing document that establishes acceptable testing methods, escalation procedures, emergency contacts, and any restrictions or exclusions.
- **Legal Compliance.** Your testing complies with all applicable local, state, national, and international laws and regulations, including but not limited to the Computer Fraud and Abuse Act (CFAA), the General Data Protection Regulation (GDPR), and equivalent legislation in your jurisdiction.

**Prohibited uses** include but are not limited to: unauthorized access to or testing of any system; testing against systems without explicit written authorization; any activity that violates applicable laws; use for malicious purposes including data theft, extortion, sabotage, or disruption of services; distribution intended to facilitate unauthorized access; and use without a clear legal basis.

**THIS TOOL IS PROVIDED "AS IS," WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NONINFRINGEMENT.**

The creator(s) and contributor(s) accept no responsibility or liability for any damage, loss, legal consequence, or other harm resulting from the use or misuse of this tool — including damage to systems or data, legal penalties or prosecution, loss of data or revenue, and any direct, indirect, incidental, special, consequential, or punitive damages.

**By using this tool, you acknowledge that you are solely responsible for ensuring that your use is authorized, lawful, and within the defined scope of your engagement. You assume all risk associated with the use of this tool.**

Security testing is a professional discipline with significant ethical and legal obligations. Users operating in a professional capacity are expected to adhere to the standards and codes of conduct established by recognized industry bodies, including PTES, OWASP, NIST, and any certifying body under which they hold credentials.

---

</details>

# OSift

**Comprehensive OSINT & reconnaissance framework** — domain-level passive recon through Azure AD tenant discovery and GitHub secret scanning, in a single script.

OSift takes a company name and one or more domains, and runs a structured 22-stage intelligence pipeline: DNS enumeration, passive OSINT tool sweeps, subdomain discovery, IP intelligence, WHOIS, company and employee OSINT, web crawling, API-enriched attack surface mapping, ProjectDiscovery toolkit sweep, DNS enrichment, GitHub secret scanning (GitDorker), people dorking, Shodan CLI per-IP enumeration, dnstwist typosquatting detection, VirusTotal reputation sweep, and Azure AD tenant reconnaissance. All results are deduplicated and written to structured JSON/CSV output for direct import into Crucible or security reports.

---


> **[View full documentation on the Codex Wiki](https://wiki.pr0t31n.com/tools/osift)** — detailed features, CLI reference, findings catalogue, and integration guides.

## Features

- **22-stage structured pipeline** — DNS enumeration through Azure AD tenant recon, each phase building on previous results. Phases gate on prior findings to avoid redundant tool runs.
- **30+ tool integrations** — theHarvester, xurlfind3r, amass, puredns, shuffledns, dnsx, katana, httpx, naabu, tlsx, cdncheck, uncover, cloudlist, waybackurls, Wappalyzer, maigret, TruffleHog, cloud_enum, EmailHarvester, Shodan CLI, GitDorker, dnstwist, gato, HakOriginFinder, waymore, exiftool, and more.
- **10+ API integrations** — Shodan, Censys, FullHunt, SecurityTrails, Netlas, VirusTotal, URLScan.io, AlienVault OTX, Hunter.io, Have I Been Pwned, Dehashed, ProjectDiscovery Chaos, FOFA, Quake360, ZoomEye, CriminalIP.
- **Scan resumption** — `checkpoint.json` tracks every completed phase. Re-running with the same output directory skips already-finished work.
- **Crucible integration** — Set `CRUCIBLE_MANAGED=1` to emit structured protocol tokens for the Crucible web UI. All output streams switch to JSON protocol messages; phases report live status.
- **Fingerprint-based deduplication** — `FindingStore` uses 16-hex SHA fingerprints to deduplicate findings across all 30+ tools.
- **Auto-install** — ProjectDiscovery tools are auto-installed via `go install` if Go is present. Python dependencies are detected and offered for auto-install at startup.
- **Multi-domain support** — Pass multiple `-d` domains to run the full pipeline against each, with per-domain phase tracking and deduplication.
- **Cross-platform** — Linux, macOS, Windows. Requires elevated privileges (root/Administrator).
- **Settings file** — All API keys, targets, and scan options persist in a single `osift_settings.json` file across engagements.
- **Finding title normalization** — all findings use `Category: Title Body` format with 11 categories (Discovery, DNS, Threat Intel, Known Vulnerable, Credential, CI/CD Security, Enumeration, Configuration, SSL/TLS Certificate, Email Security, Information Disclosure). Category prefixes are applied at emission time so Crucible displays clean, categorized titles.
- **FindingsDB dual-write** — when running under Crucible, findings are written to both JSON and the per-project SQLite database for paginated retrieval.

---

## Scan Phases

The pipeline runs 22 tracked stages. Some stages run concurrently where inputs allow it. The execution order is shown below.

| # | Phase | Tools / Sources | Notes |
|---|-------|-----------------|-------|
| 1 | **DNS Enumeration** | dig, nslookup, host, dnspython, zone transfer | A, AAAA, MX, NS, TXT, SRV, DMARC, SPF, DKIM |
| PD-A | **PD Wave A** | subfinder, chaos | Passive subdomain discovery; concurrent with Phase 1 |
| 1.5-A | **Passive OSINT Wave A** | theHarvester (40+ sources), xurlfind3r | Concurrent with Phase 1 and PD Wave A |
| 2 | **Subdomain Discovery** | Amass (passive + active) | Concurrent with Phase 1; skip with `--skip-amass` |
| PD-B | **PD Wave B** | dnsx | DNS resolution of all discovered subdomains |
| 1.5-B | **Passive OSINT Wave B** | puredns (DNS brute-force), waybackurls, waymore | After subdomain collection |
| 4 | **IP Intelligence** | PTR lookups, ASN mapping, geolocation, BGP data | Cloud/CDN detection |
| PD-CE | **PD Wave C+E** | cdncheck, asnmap, uncover, cloudlist | CDN/ASN/cloud after IPs are known |
| PD-D | **PD Wave D** | katana (passive crawl) | Web crawling via ProjectDiscovery |
| 5 | **WHOIS** | python-whois, manual WHOIS query | Registrar, nameservers, abuse contacts |
| 6 | **Company Intelligence** | EDGAR SEC filings, LinkedIn, Maltego seed | Org structure, subsidiaries, executives |
| 7 | **Email & People OSINT** | Hunter.io, HIBP, Dehashed, maigret, EmailHarvester, TruffleHog, gato, exiftool | Employee emails, breach exposure, social profiles, git secrets |
| 1.5-C | **Tech Fingerprinting** | Wappalyzer, cloud_enum, HakOriginFinder | Tech stack per host, S3/Azure/GCP bucket enum, origin IP detection |
| 10 | **OSINT API Engine** | Shodan, Censys, FullHunt, SecurityTrails, Netlas, VirusTotal, URLScan, OTX | Attack surface, threat intel, reputation, passive DNS |
| 11 | **DNS Enrichment** | dig, dnsx | Per-IP PTR, A, AAAA, CNAME resolution for all confirmed subdomains |
| 13 | **GitHub Secret Scanning** | GitDorker | Dork GitHub for org secrets, API keys, credentials |
| 14 | **People Dorking** | SerpAPI / DuckDuckGo | Search-engine dorks for employee PII and contact intelligence |
| 4.5 | **Shodan CLI** | shodan CLI per-IP scan | Open ports, banners, CVEs per host |
| 15 | **dnstwist** | dnstwist | Typosquatting and brand impersonation domain detection |
| 16 | **VT Reputation Sweep** | VirusTotal API | Subdomain + dnstwist domain reputation check |
| 17 | **Azure Tenant Recon** | Azure AD API | O365 tenant discovery, federation detection, MX/autodiscover probing |
| 12/9 | **Aggregation & Report** | IntelAggregator, RawOutputParser, SubdomainConfirmer, PhoneValidator | Intel classification, phone validation, cross-tool deduplication, subdomain liveness, final report generation |

---

## CLI Reference

### Target and Output

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `-c`, `--company` | `str` | *(required)* | Target company name |
| `-d`, `--domain` | `str` (one or more) | *(required)* | Target FQDN(s) -- one or more (e.g. `acme.com acme.co.uk`) |
| `--settings` | `FILE` | `osift_settings.json` | Path to JSON settings file containing API keys and options |
| `--output-base` | `DIR` | *(auto)* | Override base output directory path |
| `--project-dir` | `DIR` | | Crucible project root; evidence paths stored relative to this directory |
| `--client-short` | `SLUG` | | Client short name / abbreviation for project directory naming |
| `--year` | `YYYY` | *(current)* | Engagement year for project directory naming |

### Web Crawling

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--max-pages` | `int` | `200` | Max pages to crawl per host |
| `--max-depth` | `int` | `3` | Max crawl depth |
| `--wordlist` | `FILE` | | Custom wordlist for DNS brute force |

### Breach Intelligence Keys

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--hibp-key` | `KEY` | | Have I Been Pwned API key (paid -- domain search) |
| `--dehashed-user` | `EMAIL` | | Dehashed account email |
| `--dehashed-key` | `KEY` | | Dehashed API key |

### Phase 10 -- OSINT API Intelligence (all optional)

Provide API keys to enable each intelligence source. Missing keys cause that source to be skipped.

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--shodan-key` | `KEY` | | Shodan API key -- host/port/vuln/cert data |
| `--censys-id` | `API_ID` | | Censys API ID -- TLS cert + host data |
| `--censys-secret` | `SECRET` | | Censys API secret -- required together with `--censys-id` |
| `--fullhunt-key` | `KEY` | | FullHunt API key -- EASM: subdomains, hosts, tech stack |
| `--securitytrails-key` | `KEY` | | SecurityTrails API key -- DNS history, subdomain DB, WHOIS history |
| `--netlas-key` | `KEY` | | Netlas API key -- internet scan: responses, certs, DNS, WHOIS, IoC |
| `--virustotal-key` | `KEY` | | VirusTotal API key -- domain/IP reputation, passive DNS, 70+ AV vendors |
| `--urlscan-key` | `KEY` | | URLScan.io API key -- scan history, tech stack, verdicts |
| `--otx-key` | `KEY` | | AlienVault OTX API key -- threat feeds, passive DNS, malware |
| `--hunter-key` | `KEY` | | Hunter.io API key -- email discovery, company enrichment |

### ProjectDiscovery Toolkit (all optional)

Keys/config for ProjectDiscovery tools. Missing tools are auto-installed via `go install` if Go is present.

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--chaos-key` | `KEY` | | Chaos DB API key for chaos subdomain dataset |
| `--cloudlist-config` | `PATH` | | Path to cloudlist YAML config with cloud provider credentials |
| `--skip-pd` | flag | | Skip all ProjectDiscovery tool phases entirely |

### Phase 1.5 -- Passive OSINT Tool Suite

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--harvester-limit` | `int` | `500` | Max results per source for theHarvester |
| `--skip-passive` | flag | | Skip all Phase 1.5 passive OSINT tools (theHarvester, xurlfind3r, EmailHarvester, puredns, waybackurls, cloud_enum, maigret, TruffleHog, Maltego) |
| `--skip-xurlfind3r` | flag | | Skip xurlfind3r URL discovery (still runs theHarvester) |
| `--skip-wayback` | flag | | Skip waybackurls Wayback Machine CDX mining (Wave B) |
| `--skip-cloud-enum` | flag | | Skip cloud_enum cloud storage bucket enumeration (Wave C) |
| `--github-org` | `ORG` | *(inferred)* | GitHub organisation name for TruffleHog secret scanning |

### Phone Validation

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--abstractapi-phone-key` | `KEY` | | Abstract API phone validation key for external carrier-level enrichment |

### Phase Skip Flags

| Flag | Description |
|------|-------------|
| `--skip-crawl` | Skip web crawling |
| `--skip-amass` | Skip Amass enumeration |
| `--skip-brute` | Skip DNS brute forcing |
| `--skip-api` | Skip Phase 10 OSINT API intelligence entirely |
| `--skip-dns-enrich` | Skip Phase 11 DNS enrichment (dig + dnsx) |
| `--no-gitdorker` | Skip Phase 13 GitDorker GitHub secret scanning |
| `--no-dork` | Skip Phase 14 People Dorking (search-engine dorks for employee PII) |
| `--no-dnstwist` | Skip Phase 15 dnstwist typosquatting detection |
| `--no-vt-sweep` | Skip Phase 16 VirusTotal subdomain reputation sweep |

### Phase-Specific Options

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--github-token` | `TOKEN` | | GitHub personal access token for GitDorker (Phase 13) |
| `--serpapi-key` | `KEY` | | SerpAPI key for Google-backed dork execution in Phase 14 (optional; DuckDuckGo used if omitted) |
| `--max-vt-sweep` | `int` | `100` | Max subdomains to check in VT sweep (Phase 16) |
| `--edgar-email` | `EMAIL` | *(placeholder)* | Email address sent in SEC EDGAR User-Agent header (required by SEC policy) |

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
| `waymore` | Extended Wayback Machine mining |
| `maigret` | Social profile OSINT by username |
| `trufflehog` | Secret scanning across git history and web |
| `cloud_enum` | Cloud bucket enumeration (S3, Azure Blob, GCP) |
| `wappalyzer` | Technology fingerprinting (CLI) |
| `shodan` | Shodan CLI for per-IP open-port enumeration |
| `GitDorker` | GitHub dork-based secret scanning |
| `dnstwist` | Typosquatting and brand impersonation domain detection |
| `gato` | GitHub Actions security auditing |
| `hakoriginfinder` | Origin IP discovery behind CDN/WAF |
| `exiftool` | Metadata extraction from crawled documents |
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

# Multi-domain scan
sudo python3 OSift.py -c "Acme Corp" -d acme.com acme.co.uk acme.io

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
├── dnstwist/                   Typosquatting detection results
├── gitdorker/                  GitDorker GitHub secret scan results
├── reports/
│   ├── findings.json           Crucible-compatible findings (primary)
│   ├── findings_report.json    Unified deduplicated findings
│   ├── final_report.json       Full machine-readable report
│   ├── subdomains_confirmed.csv  Live confirmed subdomains
│   ├── targets_osint.json      Enriched target IP/host map
│   └── tools_used.json         Tool availability log
├── scan.log                    Human-readable progress log
├── scan.log.json               Structured JSON log
├── errors.log                  Tool errors and exceptions
└── checkpoint.json             Scan resumption state
```

### findings.json schema

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

## Crucible Integration

When launched by Crucible (`CRUCIBLE_MANAGED=1`), OSift switches to structured protocol output:

| Token | Purpose |
|-------|---------|
| `__CRUCIBLE_LOG__:` | Standard log line forwarded to UI console |
| `__CRUCIBLE_ERR__:` | Error line forwarded to UI |
| `__CRUCIBLE_STATUS__:` | Phase progress update |
| `__CRUCIBLE_PROMPT__:` | Interactive prompt requiring user response |
| `__CRUCIBLE_FINDING__:` | Real-time finding emission |
| `__CRUCIBLE_ACTION_ITEM__:` | Action item for manual follow-up |

The `__CRUCIBLE_FINDING__` token is emitted each time a new finding is written to `findings.json` -- this includes findings from all 22 phases (DNS misconfigurations, subdomain takeover risks, exposed credentials, technology fingerprints, breach data, etc.). Each token carries the full finding payload so Crucible can render it in the findings table without polling the file.

Dependency installs are non-interactive (auto-approved). Phase status is reported live so the Crucible UI can track progress in real time.

---

## Notes

- **Elevated privileges are required** — OSift exits early with an actionable message if not run as root (Linux/macOS) or Administrator (Windows).
- **Scan resumption** — Re-running against the same output directory resumes from the last completed phase. Partial phase results are discarded and re-run.
- **FindingStore deduplication** — All findings are keyed on a 16-hex SHA fingerprint derived from `(title, host, port, tool)`. Duplicate findings from overlapping tools are merged automatically.
- **ProjectDiscovery tools** — Auto-installed via `go install` into `$GOPATH/bin`. If Go is not present, PD phases are skipped gracefully.
- **GitDorker (Phase 13)** — Requires a GitHub personal access token (`--github-token`). Skip with `--no-gitdorker`.
- **People Dorking (Phase 14)** — Uses SerpAPI for Google-backed results when `--serpapi-key` is provided; falls back to DuckDuckGo when omitted. Skip with `--no-dork`.
- **dnstwist (Phase 15)** — Detects typosquatting and brand impersonation domains. Skip with `--no-dnstwist`.
- **VT Reputation Sweep (Phase 16)** — Checks subdomain and dnstwist-discovered domain reputation via VirusTotal. Requires `--virustotal-key`. Skip with `--no-vt-sweep`.
- **Azure Tenant Recon (Phase 17)** — Probes Azure AD tenant endpoints, federation configuration, and autodiscover records for each target domain.
- **`uncover` engines** — Each engine (FOFA, Quake360, ZoomEye, CriminalIP) only queries if its API key is present in the settings file or environment.
- All tool timeouts are hardened defaults. Long-running tools (amass, puredns, katana) default to 300-600 seconds.
- **FindingsDB dual-write** -- When the `PR0T31N_FINDINGS_DB` environment variable points to a SQLite database, findings are also inserted alongside JSON output. This enables cross-tool querying and Crucible dashboard aggregation.

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
| GitDorker | obheda12 | @obheda12 | https://github.com/obheda12/GitDorker |
| trufflehog | Truffle Security | @trufflesecurity | https://github.com/trufflesecurity/trufflehog |
| puredns | d3mondev | @d3mondev | https://github.com/d3mondev/puredns |
| xurlfind3r | hueristiq | @hueristiq | https://github.com/hueristiq/xurlfind3r |
| maigret | soxoj | @soxoj | https://github.com/soxoj/maigret |
| cloud_enum | initstring | @initstring | https://github.com/initstring/cloud_enum |
| whatweb | urbanadventurer | @urbanadventurer | https://github.com/urbanadventurer/WhatWeb |
| shodan CLI | Shodan.io / John Matherly | @achillean | https://github.com/achillean/shodan-python |
| dnstwist | elceef | @elceef | https://github.com/elceef/dnstwist |
| gato | AdnaneKhan | @AdnaneKhan | https://github.com/AdnaneKhan/gato |
| hakoriginfinder | hakluke | @hakluke | https://github.com/hakluke/hakoriginfinder |
| waymore | xnl-h4ck3r | @xnl-h4ck3r | https://github.com/xnl-h4ck3r/waymore |

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
