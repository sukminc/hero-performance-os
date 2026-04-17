from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


DEFAULT_OLD_REPO_ROOT = Path("/Users/chrisyoon/GitHub/opb-poker")
RAW_TXT_GLOBS = (
    "data/tmp_uploads/zip_intake_runs/**/*.txt",
    "data/tmp_uploads/**/*.txt",
)


@dataclass(frozen=True, slots=True)
class LegacyCorpusFile:
    path: Path
    source_kind: str


def _looks_like_raw_gg_hand_history(path: Path) -> bool:
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for _ in range(80):
                line = handle.readline()
                if not line:
                    break
                if line.startswith("Poker Hand #"):
                    return True
    except OSError:
        return False
    return False


def iter_legacy_raw_gg_files(old_repo_root: Path | None = None) -> Iterable[LegacyCorpusFile]:
    root = (old_repo_root or DEFAULT_OLD_REPO_ROOT).expanduser().resolve()
    seen: set[Path] = set()

    for pattern in RAW_TXT_GLOBS:
        for path in sorted(root.glob(pattern)):
            resolved = path.resolve()
            if resolved in seen or not path.is_file():
                continue
            if not _looks_like_raw_gg_hand_history(path):
                continue
            seen.add(resolved)
            yield LegacyCorpusFile(path=resolved, source_kind="raw_gg_txt")


def collect_legacy_raw_gg_files(old_repo_root: Path | None = None) -> list[LegacyCorpusFile]:
    return list(iter_legacy_raw_gg_files(old_repo_root=old_repo_root))


def build_legacy_corpus_summary(old_repo_root: Path | None = None) -> dict[str, object]:
    root = (old_repo_root or DEFAULT_OLD_REPO_ROOT).expanduser().resolve()
    files = collect_legacy_raw_gg_files(old_repo_root=root)

    return {
        "old_repo_root": str(root),
        "raw_gg_txt_count": len(files),
        "sample_files": [str(item.path) for item in files[:10]],
    }
