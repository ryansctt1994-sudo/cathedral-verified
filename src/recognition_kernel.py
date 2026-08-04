"""Weaver Recognition Kernel.

Untrusted input is a proposed computation, not passive data. This module
recognizes, bounds, canonicalizes, types, and semantically validates governance
requests before they can reach Cathedral Forge execution or persistent state.

Evidence boundary: this is the canonical parser for
CATHEDRAL-GOVERNANCE-REQUEST-v1. It is not a general parser generator and does
not prove endpoint equivalence outside the tested Python implementation.
"""

from __future__ import annotations

import hashlib
import json
import math
import unicodedata
from dataclasses import dataclass
from typing import Any, Mapping, TYPE_CHECKING

if TYPE_CHECKING:
    from cathedral_forge_final import CathedralForge, UnifiedResponse


LANGUAGE_ID = "CATHEDRAL-GOVERNANCE-REQUEST-v1"
MAX_INPUT_BYTES = 32_768
MAX_DEPTH = 4
MAX_OBJECT_COUNT = 32
MAX_PROMPT_CHARS = 8_192
MAX_CONTEXT_CHARS = 16_384
MAX_ROUNDS = 8

INV_LANGSEC_001 = "INV-LANGSEC-001"
INV_LANGSEC_002 = "INV-LANGSEC-002"
INV_LANGSEC_003 = "INV-LANGSEC-003"
INV_LANGSEC_004 = "INV-LANGSEC-004"
INV_LANGSEC_005 = "INV-LANGSEC-005"
INV_LANGSEC_006 = "INV-LANGSEC-006"
INV_LANGSEC_007 = "INV-LANGSEC-007"

_ALLOWED_FIELDS = {
    "prompt",
    "conversation_context",
    "strand",
    "require_conservation",
    "alpha_contribution",
    "omega_contribution",
    "max_rounds",
}
_REQUIRED_FIELDS = {"prompt"}
_DEFAULTS: Mapping[str, Any] = {
    "conversation_context": None,
    "strand": "lead",
    "require_conservation": True,
    "alpha_contribution": 7,
    "omega_contribution": 8,
    "max_rounds": 2,
}
_ALLOWED_STRANDS = {"α", "ω", "scale", "lead"}


class RecognitionError(ValueError):
    """Fail-closed recognition error with a stable machine-readable code."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message

    def to_dict(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message}


@dataclass(frozen=True)
class GovernanceRequest:
    prompt: str
    conversation_context: str | None
    strand: str
    require_conservation: bool
    alpha_contribution: int
    omega_contribution: int
    max_rounds: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "alpha_contribution": self.alpha_contribution,
            "conversation_context": self.conversation_context,
            "max_rounds": self.max_rounds,
            "omega_contribution": self.omega_contribution,
            "prompt": self.prompt,
            "require_conservation": self.require_conservation,
            "strand": self.strand,
        }


@dataclass(frozen=True)
class RecognitionReceipt:
    language_id: str
    canonical_sha256: str
    input_size_bytes: int
    canonical_size_bytes: int
    parser_evidence_level: str = "P3"
    side_effects_during_parse: bool = False
    raw_input_retains_authority: bool = False


@dataclass(frozen=True)
class RecognizedGovernanceRequest:
    request: GovernanceRequest
    canonical_bytes: bytes
    receipt: RecognitionReceipt

    def to_unified_request(self):
        """Convert the recognized proposal into Cathedral Forge's typed request."""
        from cathedral_forge_final import Strand, UnifiedRequest

        return UnifiedRequest(
            prompt=self.request.prompt,
            conversation_context=self.request.conversation_context,
            strand=Strand(self.request.strand),
            require_conservation=self.request.require_conservation,
            alpha_contribution=self.request.alpha_contribution,
            omega_contribution=self.request.omega_contribution,
            max_rounds=self.request.max_rounds,
        )


class _DuplicateKeyError(ValueError):
    pass


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKeyError(key)
        result[key] = value
    return result


def _measure_structure(value: Any, *, depth: int = 0) -> tuple[int, int]:
    """Return maximum depth and object count, rejecting unsupported JSON values."""
    if depth > MAX_DEPTH:
        raise RecognitionError("excessive_nesting", f"nesting depth exceeds {MAX_DEPTH}")

    if value is None or isinstance(value, (str, bool, int)):
        return depth, 1
    if isinstance(value, float):
        if not math.isfinite(value):
            raise RecognitionError("non_finite_number", "non-finite numbers are forbidden")
        return depth, 1
    if isinstance(value, list):
        maximum = depth
        count = 1
        for item in value:
            child_depth, child_count = _measure_structure(item, depth=depth + 1)
            maximum = max(maximum, child_depth)
            count += child_count
        return maximum, count
    if isinstance(value, dict):
        maximum = depth
        count = 1
        for key, item in value.items():
            if not isinstance(key, str):
                raise RecognitionError("invalid_key_type", "object keys must be strings")
            child_depth, child_count = _measure_structure(item, depth=depth + 1)
            maximum = max(maximum, child_depth)
            count += child_count
        return maximum, count
    raise RecognitionError("unsupported_value", f"unsupported decoded value: {type(value).__name__}")


def _require_nfc(name: str, value: str) -> str:
    normalized = unicodedata.normalize("NFC", value)
    if normalized != value:
        raise RecognitionError("non_canonical_unicode", f"{name} must already be NFC-normalized")
    return value


def _require_exact_bool(name: str, value: Any) -> bool:
    if type(value) is not bool:
        raise RecognitionError("invalid_type", f"{name} must be a boolean")
    return value


def _require_exact_int(name: str, value: Any, minimum: int, maximum: int) -> int:
    if type(value) is not int:
        raise RecognitionError("invalid_type", f"{name} must be an integer")
    if not minimum <= value <= maximum:
        raise RecognitionError("out_of_range", f"{name} must be between {minimum} and {maximum}")
    return value


def canonical_serialize(request: GovernanceRequest) -> bytes:
    return json.dumps(
        request.to_dict(),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def parse_governance_request(raw: bytes | str) -> RecognizedGovernanceRequest:
    """Recognize one complete governance request with no effects during parsing."""
    if isinstance(raw, str):
        try:
            raw_bytes = raw.encode("utf-8", errors="strict")
        except UnicodeEncodeError as exc:
            raise RecognitionError("invalid_encoding", "input is not valid UTF-8 text") from exc
    elif isinstance(raw, bytes):
        raw_bytes = raw
    else:
        raise RecognitionError("invalid_input_type", "input must be bytes or str")

    if len(raw_bytes) > MAX_INPUT_BYTES:
        raise RecognitionError("input_too_large", f"input exceeds {MAX_INPUT_BYTES} bytes")
    if b"\x00" in raw_bytes:
        raise RecognitionError("null_byte", "NUL bytes are forbidden")

    try:
        text = raw_bytes.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise RecognitionError("invalid_encoding", "input must be strict UTF-8") from exc

    try:
        decoded = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_pairs,
            parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)),
        )
    except _DuplicateKeyError as exc:
        raise RecognitionError("duplicate_field", f"duplicate field: {exc}") from exc
    except (json.JSONDecodeError, ValueError) as exc:
        raise RecognitionError("invalid_json", "input must be one complete JSON value with no trailing data") from exc

    _, object_count = _measure_structure(decoded)
    if object_count > MAX_OBJECT_COUNT:
        raise RecognitionError("too_many_objects", f"decoded object count exceeds {MAX_OBJECT_COUNT}")
    if not isinstance(decoded, dict):
        raise RecognitionError("invalid_root", "root must be a JSON object")

    unknown = sorted(set(decoded) - _ALLOWED_FIELDS)
    if unknown:
        raise RecognitionError("unknown_field", f"unknown fields: {', '.join(unknown)}")
    missing = sorted(_REQUIRED_FIELDS - set(decoded))
    if missing:
        raise RecognitionError("missing_field", f"missing fields: {', '.join(missing)}")

    values = dict(_DEFAULTS)
    values.update(decoded)

    prompt = values["prompt"]
    if not isinstance(prompt, str):
        raise RecognitionError("invalid_type", "prompt must be a string")
    prompt = _require_nfc("prompt", prompt)
    if not prompt or len(prompt) > MAX_PROMPT_CHARS:
        raise RecognitionError("invalid_length", f"prompt length must be 1..{MAX_PROMPT_CHARS}")

    context = values["conversation_context"]
    if context is not None:
        if not isinstance(context, str):
            raise RecognitionError("invalid_type", "conversation_context must be string or null")
        context = _require_nfc("conversation_context", context)
        if len(context) > MAX_CONTEXT_CHARS:
            raise RecognitionError("invalid_length", f"conversation_context exceeds {MAX_CONTEXT_CHARS} chars")

    strand = values["strand"]
    if not isinstance(strand, str):
        raise RecognitionError("invalid_type", "strand must be a string")
    strand = _require_nfc("strand", strand)
    if strand not in _ALLOWED_STRANDS:
        raise RecognitionError("invalid_enum", "strand is not recognized")

    request = GovernanceRequest(
        prompt=prompt,
        conversation_context=context,
        strand=strand,
        require_conservation=_require_exact_bool("require_conservation", values["require_conservation"]),
        alpha_contribution=_require_exact_int("alpha_contribution", values["alpha_contribution"], 0, 15),
        omega_contribution=_require_exact_int("omega_contribution", values["omega_contribution"], 0, 15),
        max_rounds=_require_exact_int("max_rounds", values["max_rounds"], 1, MAX_ROUNDS),
    )

    canonical = canonical_serialize(request)
    reparsed = json.loads(canonical.decode("utf-8"), object_pairs_hook=_reject_duplicate_pairs)
    if reparsed != request.to_dict():
        raise RecognitionError("canonicalization_failure", "canonical round-trip changed meaning")

    receipt = RecognitionReceipt(
        language_id=LANGUAGE_ID,
        canonical_sha256=hashlib.sha256(canonical).hexdigest(),
        input_size_bytes=len(raw_bytes),
        canonical_size_bytes=len(canonical),
    )
    return RecognizedGovernanceRequest(request=request, canonical_bytes=canonical, receipt=receipt)


async def execute_recognized_governance_request(
    forge: "CathedralForge", raw: bytes | str
) -> tuple["UnifiedResponse", RecognitionReceipt]:
    """Recognition Gate: parse fully before invoking Cathedral Forge effects."""
    recognized = parse_governance_request(raw)
    response = await forge.run(recognized.to_unified_request())
    return response, recognized.receipt
