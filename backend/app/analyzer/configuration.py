import re
from typing import Dict, List
from app.models.repository import ConfigurationAnalysisResult


class ConfigurationAnalyzer:
    """Analyzes Docker, Makefile, .env.example, and CI configuration files."""

    def analyze(self, raw_files: Dict[str, str]) -> ConfigurationAnalysisResult:
        dockerfile_found = "Dockerfile" in raw_files
        docker_compose_found = any(
            f in raw_files for f in ("docker-compose.yml", "docker-compose.yaml", "compose.yaml")
        )
        makefile_found = "Makefile" in raw_files
        env_example_found = ".env.example" in raw_files

        env_vars: List[str] = []
        if env_example_found:
            env_vars = self._extract_env_vars(raw_files[".env.example"])

        ci_workflows: List[str] = []
        ci_commands: List[str] = []
        for path, content in raw_files.items():
            if path.startswith(".github/workflows/"):
                ci_workflows.append(path.split("/")[-1])
                ci_commands.extend(self._extract_ci_commands(content))

        # Makefile targets
        if makefile_found:
            make_targets = self._extract_make_targets(raw_files["Makefile"])
            for t in make_targets:
                if t in ("test", "build", "run", "dev", "lint", "check", "setup", "install"):
                    ci_commands.append(f"make {t}")

        return ConfigurationAnalysisResult(
            docker_support=dockerfile_found or docker_compose_found,
            dockerfile_found=dockerfile_found,
            docker_compose_found=docker_compose_found,
            makefile_found=makefile_found,
            env_example_found=env_example_found,
            env_variables=sorted(list(set(env_vars)))[:30],
            ci_workflows=sorted(ci_workflows)[:10],
            ci_commands=sorted(list(set(ci_commands)))[:20],
        )

    def _extract_env_vars(self, content: str) -> List[str]:
        vars_found: List[str] = []
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                var_name = line.split("=")[0].strip()
                if re.match(r"^[A-Z0-9_]+$", var_name):
                    vars_found.append(var_name)
        return vars_found

    def _extract_ci_commands(self, content: str) -> List[str]:
        commands: List[str] = []
        for line in content.splitlines():
            line = line.strip()
            if line.startswith("run:"):
                cmd = line[4:].strip().strip('"\'')
                # Only take concise single-line commands
                if cmd and not cmd.startswith("|") and len(cmd) < 80:
                    commands.append(cmd)
        return commands

    def _extract_make_targets(self, content: str) -> List[str]:
        targets: List[str] = []
        for line in content.splitlines():
            match = re.match(r"^([a-zA-Z0-9_-]+):", line)
            if match:
                targets.append(match.group(1))
        return targets
