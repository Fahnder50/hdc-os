from pathlib import Path
from typing import Iterable

from .contracts import KnowledgeItem, RetrievalSource


class RepositoryKnowledgeRetriever:
    """Reads only the explicitly allow-listed v0.1 source paths."""

    def __init__(self, root: Path, reports: Path, history: Path):
        self.root, self.reports, self.history = Path(root), Path(reports), Path(history)

    def retrieve(self, terms: tuple[str, ...]) -> tuple[KnowledgeItem, ...]:
        paths = {
            RetrievalSource.ACCEPTED_ARCHITECTURE: self._accepted(self.root / "10-Engineering" / "Architecture"),
            RetrievalSource.PROCUREMENT_CASES: (self.root / "30-Procurement" / "cases").glob("*.md"),
            RetrievalSource.PROCUREMENT_REPORTS: self.reports.glob("*.json"),
            RetrievalSource.PROCUREMENT_HISTORY: self.history.glob("*.json"),
            RetrievalSource.ASSET_STATUS: (self.root / "20-Operations" / "assets" / "records").glob("*.yaml"),
            RetrievalSource.GOVERNANCE_RULES: [self.root / "00-Foundation" / "Constitution.md", self.root / "Repository-Documentation-Governance.md"],
            RetrievalSource.CURRENT_SPRINT: [self.root / "Project.md"],
            RetrievalSource.CURRENT_BOTTLENECK: [self.root / "Project-Status.md"],
            RetrievalSource.CURRENT_DEPLOYMENT_STATE: [self.root / "20-Operations" / "WO-0041-First-Deployment-Readiness.md"],
        }
        items = []
        lowered = tuple(term.lower() for term in terms if term)
        for source, candidates in paths.items():
            for path in sorted(candidates):
                if not path.is_file():
                    continue
                content = path.read_text(encoding="utf-8", errors="replace")
                excerpt = self._relevant_excerpt(content, lowered)
                if excerpt:
                    items.append(KnowledgeItem(source, path.relative_to(self.root).as_posix() if path.is_relative_to(self.root) else path.name, excerpt))
        return tuple(items)

    @staticmethod
    def _accepted(directory: Path) -> Iterable[Path]:
        return (path for path in directory.glob("*.md") if "status: Accepted" in path.read_text(encoding="utf-8", errors="replace")[:500])

    @staticmethod
    def _relevant_excerpt(content: str, terms: tuple[str, ...]) -> str:
        lines = content.splitlines()
        selected = [line for line in lines if any(term in line.lower() for term in terms)]
        return "\n".join(selected[:80])
