from app.analyzer.structure import StructureAnalyzer
from app.models.repository import TreeEntry


def test_structure_analyzer_filters_noise_and_detects_dirs():
    entries = [
        TreeEntry(path=".git/config", type="blob"),
        TreeEntry(path="node_modules/react/index.js", type="blob"),
        TreeEntry(path="src/components/Header.tsx", type="blob"),
        TreeEntry(path="src/api/routes.ts", type="blob"),
        TreeEntry(path="tests/test_main.py", type="blob"),
        TreeEntry(path="docs/setup.md", type="blob"),
        TreeEntry(path="src/App.tsx", type="blob"),
    ]
    analyzer = StructureAnalyzer(max_entries=100)
    result = analyzer.analyze(entries)

    assert result.total_files == 5  # .git and node_modules ignored
    assert "src" in result.important_directories
    assert "tests" in result.important_directories
    assert "docs" in result.important_directories
    assert "src/App.tsx" in result.likely_entry_points
    assert not result.truncated


def test_structure_analyzer_truncation():
    entries = [TreeEntry(path=f"file_{i}.txt", type="blob") for i in range(10)]
    analyzer = StructureAnalyzer(max_entries=5)
    result = analyzer.analyze(entries)
    assert result.truncated is True
    assert result.total_files == 5
