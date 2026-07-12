# Independent Reproduction Review — Windows

Independent reproduction review performed 2026-07-12 on Microsoft Windows. This document records what was directly observed when executing validation commands against a pinned commit of `cathedral-verified` from a separate local clone.

**Review type:** Independent reproduction attempt (Windows host).

**Scope:** Document only the evidence directly observed during execution. This report does not claim complete reproduction, production readiness, or independent certification.

---

## Repository

| Item | Value |
|------|-------|
| Repository URL | https://github.com/ryansctt1994-sudo/cathedral-verified.git |
| Local clone path | `C:\dev\cathedral-forge-review\cathedral-verified` |
| Clone method | Full clone (`git clone https://github.com/ryansctt1994-sudo/cathedral-verified.git`) |

---

## Review branch

| Item | Value |
|------|-------|
| Initial checkout | `independent-review` tracking `origin/agent/p0-repair-regressions` |
| Validation execution state | Detached HEAD at pinned commit (see below) |

The review session created `independent-review` from `origin/agent/p0-repair-regressions`, then detached to the pinned commit before running the Python validation suites recorded below.

---

## Pinned commit

| Item | Value |
|------|-------|
| Full hash | `8ab93420b6ce86c66834d697aabc6a672ba0ec73` |
| Commit message | Record classifier assurance validation receipt |
| Recorded via | `git rev-parse HEAD` during review |

---

## Review environment

| Item | Value |
|------|-------|
| Review date | 2026-07-12 |
| OS | Microsoft Windows NT 10.0.26200.0 |
| Shell | PowerShell 5.1.26100.8737 |
| Python | 3.14.3 (`python` on PATH) |
| GNU Make | Not available on PATH (`CommandNotFoundException` for `make --version`) |
| Icarus Verilog | Not available on PATH (`CommandNotFoundException` for `iverilog -V`) |

---

## Commands executed

Commands below are taken from the review session command history and preserved terminal transcript. Order reflects the review sequence at the pinned commit unless noted.

### Clone and branch setup

```powershell
cd C:\dev
mkdir cathedral-forge-review
cd cathedral-forge-review
git clone https://github.com/ryansctt1994-sudo/cathedral-verified.git
cd cathedral-verified
git branch -a
git remote -v
git switch -c independent-review --track origin/agent/p0-repair-regressions
git switch --detach 8ab93420b6ce86c66834d697aabc6a672ba0ec73
git rev-parse HEAD
```

### Environment checks

```powershell
python --version
python3 --version
make --version
iverilog -V
$PSVersionTable.PSVersion
[System.Environment]::OSVersion.VersionString
```

`make --version` and `iverilog -V` were not recognized as commands in this environment.

### Attempted aggregate target (before pinning)

```powershell
make test
```

This command was attempted earlier in the review session on the initial branch checkout. GNU Make was not available on PATH in the documented Windows environment.

### Python validation suites (pinned commit)

```powershell
$env:PYTHONPATH="src;."
python -m unittest tests.test_bootstrap -v
python -m unittest tests.test_recognition_kernel -v
python -m unittest tests.test_classifier_assurance -v
cd chronicle
python test_chronicle.py
cd ..
python -m unittest discover -s tests -p "test_p0_regressions.py" -v
git rev-parse HEAD
```

The review used `python` rather than the `python3` invocations shown in the repository `Makefile`.

### Documentation review (read-only)

```powershell
Get-Content README.md
Select-String -Path README.md,EXTERNAL_ENGINEERING_REVIEW_PACKAGE.md -Pattern "Windows|PowerShell|make|mingw|MSYS|WSL|GNU Make"
```

---

## Validation results

### Bootstrap Policy (`tests.test_bootstrap`)

Command executed: `python -m unittest tests.test_bootstrap -v` with `PYTHONPATH=src;.`

**Result: PASS.** The Bootstrap Policy suite completed successfully during the review session. The preserved terminal transcript for this review begins at Recognition Kernel; Bootstrap Policy was executed immediately before that suite in the same session.

### Recognition Kernel (`tests.test_recognition_kernel`)

Exit status: **OK**

```
Ran 18 tests in 0.159s

OK
```

All 18 listed tests reported `ok`.

### Classifier Assurance (`tests.test_classifier_assurance`)

Exit status: **OK**

```
Ran 7 tests in 0.002s

OK
```

All 7 listed tests reported `ok`.

### Chronicle (`chronicle/test_chronicle.py`)

Exit status: **PASS**

```
================ RESULT ================
  PASSED: 15   FAILED: 0
=======================================
  VERDICT: TAMPER-EVIDENCE VERIFIED
```

Checks T1 through T12 were observed passing in the preserved transcript.

### P0 Regression (`tests/test_p0_regressions.py`)

Exit status: **OK**

```
Ran 11 tests in 0.081s

OK
```

All 11 listed tests reported `ok`.

### Hardware simulation (`make test-hw` / Lucifer Latch RTL)

**Not executed.** GNU Make and Icarus Verilog were unavailable in the documented Windows environment, so the documented hardware simulation path was not reproduced.

---

## Successfully reproduced components

On Windows, at pinned commit `8ab93420b6ce86c66834d697aabc6a672ba0ec73`, the following Python validation suites were successfully reproduced using direct `python` invocations:

| Component | Suite | Observed result |
|-----------|-------|-----------------|
| Bootstrap Policy | `tests.test_bootstrap` | PASS |
| Recognition Kernel | `tests.test_recognition_kernel` | 18/18 OK |
| Classifier Assurance | `tests.test_classifier_assurance` | 7/7 OK |
| Chronicle | `chronicle/test_chronicle.py` | 15/15 PASSED |
| P0 Regression | `tests/test_p0_regressions.py` | 11/11 OK |

**Summary:** The Python validation suites documented above were successfully reproduced on Windows.

---

## Components not reproduced

| Component | Reason |
|-----------|--------|
| `make test` aggregate target | GNU Make not available on PATH |
| Lucifer Latch RTL simulation (`make test-hw`, `iverilog`, `vvp`) | Icarus Verilog not available on PATH |
| Full Makefile-driven workflow | Makefile targets invoke `python3` and `make`; review substituted direct `python` commands for the Python suites only |

Hardware simulation was not reproduced in this review environment.

---

## Documentation observations

Observations below are limited to what was read or searched during the review session.

1. **`README.md` at the pinned commit** instructs reviewers to clone the repository and run `make test`, with `make test-hw` noted as requiring `iverilog`. No Windows-specific reproduction path is documented in `README.md`.

2. **`Makefile` at the pinned commit** defines aggregate and per-suite targets using `python3` and GNU Make. The Windows review host used `python` successfully for the Python suites but could not invoke `make` targets.

3. **`LAYER0_SOURCE_POLICY.md`** documents Bootstrap Policy commands using `python3` and `make test-bootstrap`. The review reproduced Bootstrap Policy using `python` with an explicit `PYTHONPATH` instead.

4. **Windows tooling search.** The review session searched `README.md` and `EXTERNAL_ENGINEERING_REVIEW_PACKAGE.md` for Windows, PowerShell, make, MSYS, WSL, and GNU Make guidance. No substitute Windows reproduction procedure was observed in the preserved search scope.

5. **Pinned commit vs branch tip.** Validation was executed at detached HEAD `8ab93420`, not at the moving tip of `independent-review`.

---

## Evidence boundaries

This report documents only the evidence directly observed during execution.

**What this review observed:**

- A full local clone of `cathedral-verified`
- Python 3.14.3 availability on Windows via `python`
- Successful execution of the Bootstrap Policy, Recognition Kernel, Classifier Assurance, Chronicle, and P0 Regression Python validation suites at pinned commit `8ab93420`
- Absence of GNU Make and Icarus Verilog on PATH in the documented Windows environment

**What this review does NOT claim:**

- Complete reproduction of all repository validation paths
- Production readiness
- Independent certification
- External audit
- Hardware or silicon verification
- Truth of prose claims beyond the executed test outputs
- GitHub Actions status for the pinned commit (not checked during this review session)
- Reproduction of `make test` as a single aggregate command on Windows

**Preservation note:** The preserved terminal transcript begins at Recognition Kernel output. Bootstrap Policy execution is recorded in the review command history and reported here as a completed passing suite from the same session; its stdout was not separately preserved in the captured transcript.

---

## Overall assessment

**Partial reproduction on Windows.**

The Python validation suites were successfully reproduced on Windows at pinned commit `8ab93420b6ce86c66834d697aabc6a672ba0ec73`. Bootstrap Policy, Recognition Kernel, Classifier Assurance, Chronicle, and P0 Regression all passed under direct `python` invocation with `PYTHONPATH=src;.`.

GNU Make and Icarus Verilog were unavailable in the documented Windows environment, so hardware simulation was not reproduced and the documented `make test` entry path was not usable without additional tooling.

This review does not claim complete reproduction. This review does not claim production readiness. This review does not claim independent certification.

---

## Recommendations

1. **Document a Windows Python reproduction path.** Publish explicit PowerShell commands equivalent to the Makefile Python targets, including `PYTHONPATH=src;.` and `python` instead of assuming `python3` and GNU Make.

2. **Separate software and hardware prerequisites.** State clearly that Lucifer Latch RTL simulation requires Icarus Verilog (and a runner such as `vvp`) in addition to Python.

3. **Preserve full terminal transcripts.** Capture stdout for every suite, including Bootstrap Policy, when filing future witness or reproduction records.

4. **Record reviewer identity and independence statement.** This report records environment and command evidence only; a future witness record should add reviewer handle, relationship to the project, and an explicit independence statement if E4-style attestation is required.

5. **Re-run hardware simulation on a host with documented tooling.** Reproduce `make test-hw` or the equivalent `iverilog`/`vvp` commands on a system where GNU Make and Icarus Verilog are available, then preserve that output separately from this Windows Python-only partial reproduction.
