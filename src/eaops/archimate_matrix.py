from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any
import hashlib
import os
import urllib.request
import xml.etree.ElementTree as ET


RELATION_CODES = {
    "a": "Access",
    "c": "Composition",
    "f": "Flow",
    "g": "Aggregation",
    "i": "Assignment",
    "n": "Influence",
    "o": "Association",
    "r": "Realization",
    "s": "Specialization",
    "t": "Triggering",
    "v": "Serving",
}


class RelationshipMatrixError(RuntimeError):
    """Raised when the configured ArchiMate relationship matrix cannot be loaded safely."""


def _git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def _default_cache_path(version: str) -> Path:
    cache_root = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    return cache_root / "ea-ops" / f"archimate-{version}-relationships.xml"


def _read_verified(path: Path, expected_blob_sha: str | None) -> bytes | None:
    if not path.exists():
        return None
    data = path.read_bytes()
    if expected_blob_sha and _git_blob_sha(data) != expected_blob_sha:
        return None
    return data


def _download(url: str, expected_blob_sha: str | None) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "EA-Ops relationship-matrix loader"},
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:  # nosec B310 - URL is pinned by the metamodel profile
            data = response.read()
    except Exception as exc:  # pragma: no cover - exact urllib exceptions vary by platform
        raise RelationshipMatrixError(f"Could not download relationship matrix from {url}: {exc}") from exc
    if expected_blob_sha:
        actual = _git_blob_sha(data)
        if actual != expected_blob_sha:
            raise RelationshipMatrixError(
                f"Relationship matrix integrity check failed: expected Git blob {expected_blob_sha}, got {actual}"
            )
    return data


def parse_relationship_matrix(data: bytes | str) -> tuple[str, dict[tuple[str, str], frozenset[str]]]:
    """Parse an Archi-style relationship matrix into allowed relationship names.

    Archi's compact relation letters are mapped to the ArchiMate relationship names used by EA-Ops.
    The returned mapping is keyed by ``(source_type, target_type)``.
    """
    raw = data.encode("utf-8") if isinstance(data, str) else data
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        raise RelationshipMatrixError(f"Relationship matrix is not valid XML: {exc}") from exc
    version = str(root.attrib.get("version", ""))
    matrix: dict[tuple[str, str], frozenset[str]] = {}
    for source in root.findall("source"):
        source_type = source.attrib.get("concept")
        if not source_type:
            continue
        for target in source.findall("target"):
            target_type = target.attrib.get("concept")
            if not target_type:
                continue
            letters = target.attrib.get("relations", "")
            unknown = sorted(set(letters) - set(RELATION_CODES))
            if unknown:
                raise RelationshipMatrixError(
                    f"Unknown relationship code(s) {unknown} for {source_type} -> {target_type}"
                )
            matrix[(source_type, target_type)] = frozenset(RELATION_CODES[letter] for letter in letters)
    return version, matrix


@lru_cache(maxsize=8)
def _load_cached(url: str, expected_blob_sha: str, version: str) -> tuple[str, dict[tuple[str, str], frozenset[str]]]:
    override = os.environ.get("EAOPS_ARCHIMATE_MATRIX")
    candidates = []
    if override:
        candidates.append(Path(override).expanduser())
    package_copy = Path(__file__).parent / "data" / f"archimate-{version}-relationships.xml"
    candidates.append(package_copy)
    cache_path = _default_cache_path(version)
    candidates.append(cache_path)

    data = None
    for candidate in candidates:
        data = _read_verified(candidate, expected_blob_sha or None)
        if data is not None:
            break

    if data is None:
        if not url:
            raise RelationshipMatrixError("No relationship-matrix URL is configured and no verified local copy was found")
        data = _download(url, expected_blob_sha or None)
        try:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_bytes(data)
        except OSError:
            pass  # A read-only home directory must not prevent validation.

    parsed_version, matrix = parse_relationship_matrix(data)
    if version and parsed_version != version:
        raise RelationshipMatrixError(
            f"Relationship matrix version mismatch: expected {version}, got {parsed_version or 'unknown'}"
        )
    return parsed_version, matrix


def load_relationship_matrix(spec: dict[str, Any]) -> tuple[str, dict[tuple[str, str], frozenset[str]]]:
    version = str(spec.get("version", "3.2"))
    url = str(spec.get("url", ""))
    blob_sha = str(spec.get("gitBlobSha", ""))
    return _load_cached(url, blob_sha, version)


def allowed_relationships(
    spec: dict[str, Any], source_type: str, target_type: str
) -> frozenset[str]:
    _, matrix = load_relationship_matrix(spec)
    return matrix.get((source_type, target_type), frozenset())
