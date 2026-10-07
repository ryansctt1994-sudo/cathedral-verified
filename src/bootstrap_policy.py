"""Layer 0 repository source-policy enforcement.

This module implements a bounded no-opaque-artifacts gate for repository inputs.
It does not prove compiler provenance, reproducible toolchain bootstrapping, or
eliminate the Trusting Trust problem. It rejects files that are clearly binary,
precompiled, packaged, or otherwise opaque before they enter higher layers.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


INV_BOOT_001 = "INV-BOOT-001"
INV_BOOT_002 = "INV-BOOT-002"

FORBIDDEN_SUFFIXES = {
    ".a",
    ".bin",
    ".class",
    ".dll",
    ".dylib",
    ".elf",
    ".exe",
    ".jar",
    ".o",
    ".obj",
    ".pyc",
    ".pyd",
    ".so",
    ".wasm",
    ".whl",
    ".zip",
}

FORBIDDEN_NAMES = {
    "a.out",
    "sim_latch",
}

IGNORED_PARTS = {
    ".git",
    ".pytest_cache",
    "__pycache__",
}

BINARY_MAGIC_PREFIXES = (
    b"\x7fELF",
    b"MZ",
    b"PK\x03\x04",
    b"\xca\xfe\xba\xbe",
    b"\x00asm",
)


@dataclass(frozen=True)
class PolicyViolation:
    path: str
    rule: str
    reason: str


@dataclass(frozen=True)
class BootstrapPolicyResult:
    accepted: bool
    violations: tuple[PolicyViolation, ...]

    @property
    def state(self) -> str:
        return "ALLOW" if self.accepted else "REJECT"


def _is_ignored(path: Path) -> bool:
    return any(part in IGNORED_PARTS for part in path.parts)


def inspect_file(path: str | Path, *, root: str | Path | None = None) -> list[PolicyViolation]:
    candidate = Path(path)
    display = candidate.relative_to(root).as_posix() if root is not None else candidate.as_posix()
    violations: list[PolicyViolation] = []

    if candidate.name in FORBIDDEN_NAMES or candidate.suffix.lower() in FORBIDDEN_SUFFIXES:
        violations.append(
            PolicyViolation(
                path=display,
                rule=INV_BOOT_001,
                reason="forbidden opaque or precompiled artifact type",
            )
        )

    try:
        prefix = candidate.read_bytes()[:8192]
    except OSError as exc:
        violations.append(
            PolicyViolation(path=display, rule=INV_BOOT_002, reason=f"unreadable input: {exc.__class__.__name__}")
        )
        return violations

    if b"\x00" in prefix:
        violations.append(
            PolicyViolation(path=display, rule=INV_BOOT_001, reason="binary NUL byte detected")
        )

    if any(prefix.startswith(magic) for magic in BINARY_MAGIC_PREFIXES):
        violations.append(
            PolicyViolation(path=display, rule=INV_BOOT_001, reason="known binary or archive signature detected")
        )

    return violations


def iter_repository_files(root: str | Path) -> Iterable[Path]:
    base = Path(root)
    for path in sorted(base.rglob("*")):
        if path.is_file() and not _is_ignored(path.relative_to(base)):
            yield path


def enforce_source_policy(root: str | Path) -> BootstrapPolicyResult:
    base = Path(root)
    violations: list[PolicyViolation] = []
    for path in iter_repository_files(base):
        violations.extend(inspect_file(path, root=base))
    return BootstrapPolicyResult(accepted=not violations, violations=tuple(violations))


def format_report(result: BootstrapPolicyResult) -> str:
    lines = [f"bootstrap_policy_state={result.state}"]
    for violation in result.violations:
        lines.append(f"{violation.rule} {violation.path}: {violation.reason}")
    return "\n".join(lines)
