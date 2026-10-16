import json
import logging
import re
from typing import Dict, List, Optional
import xml.etree.ElementTree as ET

# Python 3.11+ includes tomllib in standard library
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        tomllib = None  # type: ignore

from app.models.repository import DependencyAnalysisResult

logger = logging.getLogger("git_analyzer.analyzer.dependencies")


def parse_package_json(content: str) -> DependencyAnalysisResult:
    """Extract runtime, scripts, package manager, and dependencies from package.json."""
    result = DependencyAnalysisResult(
        language="JavaScript / TypeScript",
        runtime="Node.js",
        package_manager="npm",
        install_command="npm install",
        raw_manifests_found=["package.json"],
    )
    try:
        data = json.loads(content)
    except Exception as e:
        logger.warning(f"Failed to parse package.json: {e}")
        return result

    # Check packageManager field (e.g., pnpm@8.1.0, yarn@1.22.19, bun@1.0.0)
    pm = data.get("packageManager", "")
    if "pnpm" in pm:
        result.package_manager = "pnpm"
        result.install_command = "pnpm install"
    elif "yarn" in pm:
        result.package_manager = "yarn"
        result.install_command = "yarn install"
    elif "bun" in pm:
        result.package_manager = "bun"
        result.install_command = "bun install"

    # Engines
    engines = data.get("engines", {})
    if isinstance(engines, dict):
        result.engines = {k: str(v) for k, v in engines.items()}
        if "node" in engines:
            result.runtime = f"Node.js {engines['node']}"

    # Scripts
    scripts = data.get("scripts", {})
    if isinstance(scripts, dict):
        pm_run = f"{result.package_manager} run" if result.package_manager != "yarn" else "yarn"
        if "dev" in scripts:
            result.dev_command = f"{pm_run} dev"
        elif "start" in scripts:
            result.start_command = f"{pm_run} start"

        if "build" in scripts:
            result.build_command = f"{pm_run} build"
        if "test" in scripts:
            result.test_command = f"{pm_run} test"
        if "lint" in scripts:
            result.lint_command = f"{pm_run} lint"

    # Dependencies
    deps = data.get("dependencies", {})
    if isinstance(deps, dict):
        result.dependencies = list(deps.keys())[:50]
        if "typescript" in deps:
            result.language = "TypeScript"

    dev_deps = data.get("devDependencies", {})
    if isinstance(dev_deps, dict):
        result.dev_dependencies = list(dev_deps.keys())[:50]
        if "typescript" in dev_deps:
            result.language = "TypeScript"

    return result


def parse_requirements_txt(content: str) -> DependencyAnalysisResult:
    """Parse Python requirements.txt."""
    result = DependencyAnalysisResult(
        language="Python",
        runtime="Python",
        package_manager="pip",
        install_command="pip install -r requirements.txt",
        raw_manifests_found=["requirements.txt"],
    )
    deps: List[str] = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-r") or line.startswith("-i"):
            continue
        # Extract package name before operators like ==, >=, <=, ~=, <, >
        pkg_name = re.split(r"[><=~!;]", line)[0].strip()
        if pkg_name:
            deps.append(pkg_name)
    result.dependencies = deps[:50]
    return result


def parse_pyproject_toml(content: str) -> DependencyAnalysisResult:
    """Parse Python pyproject.toml."""
    result = DependencyAnalysisResult(
        language="Python",
        runtime="Python",
        package_manager="pip",
        install_command="pip install .",
        raw_manifests_found=["pyproject.toml"],
    )
    if not tomllib:
        return result

    try:
        data = tomllib.loads(content)
    except Exception as e:
        logger.warning(f"Failed to parse pyproject.toml: {e}")
        return result

    # Poetry
    poetry = data.get("tool", {}).get("poetry", {})
    if poetry:
        result.package_manager = "poetry"
        result.install_command = "poetry install"
        result.dev_command = "poetry run python main.py"
        result.test_command = "poetry run pytest"
        poetry_deps = poetry.get("dependencies", {})
        if isinstance(poetry_deps, dict):
            result.dependencies = [k for k in poetry_deps.keys() if k != "python"][:50]
            if "python" in poetry_deps:
                result.runtime = f"Python {poetry_deps['python']}"
        dev_deps = poetry.get("group", {}).get("dev", {}).get("dependencies", {})
        if isinstance(dev_deps, dict):
            result.dev_dependencies = list(dev_deps.keys())[:50]
        return result

    # Standard PEP 621 project table
    project = data.get("project", {})
    if project:
        requires_python = project.get("requires-python")
        if requires_python:
            result.runtime = f"Python {requires_python}"
        deps = project.get("dependencies", [])
        if isinstance(deps, list):
            result.dependencies = [re.split(r"[><=~!;]", d)[0].strip() for d in deps if isinstance(d, str)][:50]
        opt_deps = project.get("optional-dependencies", {})
        if isinstance(opt_deps, dict):
            all_opt = []
            for group in opt_deps.values():
                if isinstance(group, list):
                    all_opt.extend([re.split(r"[><=~!;]", d)[0].strip() for d in group if isinstance(d, str)])
            result.dev_dependencies = all_opt[:50]

    # Hatch / Flit / Pdm
    build_sys = data.get("build-system", {}).get("build-backend", "")
    if "pdm" in build_sys:
        result.package_manager = "pdm"
        result.install_command = "pdm install"
    elif "hatch" in build_sys:
        result.package_manager = "hatch"
        result.install_command = "hatch env create"

    return result


def parse_cargo_toml(content: str) -> DependencyAnalysisResult:
    """Parse Rust Cargo.toml."""
    result = DependencyAnalysisResult(
        language="Rust",
        runtime="Rust / Cargo",
        package_manager="cargo",
        install_command="cargo build",
        dev_command="cargo run",
        build_command="cargo build",
        test_command="cargo test",
        raw_manifests_found=["Cargo.toml"],
    )
    if not tomllib:
        return result

    try:
        data = tomllib.loads(content)
        deps = data.get("dependencies", {})
        if isinstance(deps, dict):
            result.dependencies = list(deps.keys())[:50]
        dev_deps = data.get("dev-dependencies", {})
        if isinstance(dev_deps, dict):
            result.dev_dependencies = list(dev_deps.keys())[:50]
        edition = data.get("package", {}).get("edition")
        if edition:
            result.engines = {"edition": str(edition)}
    except Exception as e:
        logger.warning(f"Failed to parse Cargo.toml: {e}")
    return result


def parse_go_mod(content: str) -> DependencyAnalysisResult:
    """Parse Go go.mod."""
    result = DependencyAnalysisResult(
        language="Go",
        runtime="Go",
        package_manager="go modules",
        install_command="go mod download",
        dev_command="go run .",
        build_command="go build ./...",
        test_command="go test ./...",
        raw_manifests_found=["go.mod"],
    )
    deps: List[str] = []
    in_require = False
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("go "):
            result.runtime = f"Go {line[3:].strip()}"
        elif line.startswith("require ("):
            in_require = True
        elif in_require and line == ")":
            in_require = False
        elif in_require:
            parts = line.split()
            if parts and not parts[0].startswith("//"):
                deps.append(parts[0])
        elif line.startswith("require "):
            parts = line[8:].strip().split()
            if parts:
                deps.append(parts[0])
    result.dependencies = deps[:50]
    return result


def parse_pom_xml(content: str) -> DependencyAnalysisResult:
    """Parse Java Maven pom.xml."""
    result = DependencyAnalysisResult(
        language="Java",
        runtime="JVM / Java",
        package_manager="Maven",
        install_command="mvn clean install",
        build_command="mvn compile",
        test_command="mvn test",
        raw_manifests_found=["pom.xml"],
    )
    try:
        # Strip default namespaces for easier element access
        clean_xml = re.sub(r'\sxmlns="[^"]+"', '', content, count=1)
        root = ET.fromstring(clean_xml)
        deps: List[str] = []
        for dep in root.findall(".//dependency"):
            group = dep.find("groupId")
            artifact = dep.find("artifactId")
            if group is not None and artifact is not None and group.text and artifact.text:
                deps.append(f"{group.text}:{artifact.text}")
        result.dependencies = deps[:50]
    except Exception as e:
        logger.warning(f"Failed to parse pom.xml: {e}")
    return result


def parse_gemfile(content: str) -> DependencyAnalysisResult:
    """Parse Ruby Gemfile."""
    result = DependencyAnalysisResult(
        language="Ruby",
        runtime="Ruby",
        package_manager="bundler",
        install_command="bundle install",
        dev_command="bundle exec rake",
        test_command="bundle exec rspec",
        raw_manifests_found=["Gemfile"],
    )
    deps: List[str] = []
    for line in content.splitlines():
        line = line.strip()
        match = re.match(r"^gem\s+['\"]([^'\"]+)['\"]", line)
        if match:
            deps.append(match.group(1))
    result.dependencies = deps[:50]
    return result


def parse_composer_json(content: str) -> DependencyAnalysisResult:
    """Parse PHP composer.json."""
    result = DependencyAnalysisResult(
        language="PHP",
        runtime="PHP",
        package_manager="Composer",
        install_command="composer install",
        raw_manifests_found=["composer.json"],
    )
    try:
        data = json.loads(content)
        req = data.get("require", {})
        if isinstance(req, dict):
            result.dependencies = list(req.keys())[:50]
            if "php" in req:
                result.runtime = f"PHP {req['php']}"
        dev_req = data.get("require-dev", {})
        if isinstance(dev_req, dict):
            result.dev_dependencies = list(dev_req.keys())[:50]
    except Exception as e:
        logger.warning(f"Failed to parse composer.json: {e}")
    return result


class DependencyAnalyzer:
    """Aggregates manifest parsers to detect project dependencies and commands."""

    def analyze(self, raw_files: Dict[str, str]) -> DependencyAnalysisResult:
        # Check priority manifests in order
        if "package.json" in raw_files:
            return parse_package_json(raw_files["package.json"])
        elif "pyproject.toml" in raw_files:
            return parse_pyproject_toml(raw_files["pyproject.toml"])
        elif "requirements.txt" in raw_files:
            return parse_requirements_txt(raw_files["requirements.txt"])
        elif "Cargo.toml" in raw_files:
            return parse_cargo_toml(raw_files["Cargo.toml"])
        elif "go.mod" in raw_files:
            return parse_go_mod(raw_files["go.mod"])
        elif "pom.xml" in raw_files:
            return parse_pom_xml(raw_files["pom.xml"])
        elif "Gemfile" in raw_files:
            return parse_gemfile(raw_files["Gemfile"])
        elif "composer.json" in raw_files:
            return parse_composer_json(raw_files["composer.json"])

        return DependencyAnalysisResult()
