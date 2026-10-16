from app.analyzer.dependencies import (
    parse_package_json,
    parse_requirements_txt,
    parse_pyproject_toml,
    parse_cargo_toml,
    parse_go_mod,
    parse_pom_xml,
    DependencyAnalyzer,
)


def test_parse_package_json():
    content = """{
        "name": "my-app",
        "packageManager": "pnpm@9.0.0",
        "engines": {"node": ">=20.0.0"},
        "scripts": {
            "dev": "vite",
            "build": "vite build",
            "test": "vitest"
        },
        "dependencies": {
            "react": "^18.3.1",
            "typescript": "^5.5.0"
        }
    }"""
    result = parse_package_json(content)
    assert result.language == "TypeScript"
    assert result.runtime == "Node.js >=20.0.0"
    assert result.package_manager == "pnpm"
    assert result.install_command == "pnpm install"
    assert result.dev_command == "pnpm run dev"
    assert result.build_command == "pnpm run build"
    assert result.test_command == "pnpm run test"
    assert "react" in result.dependencies


def test_parse_requirements_txt():
    content = """
    # Comments
    fastapi>=0.115.0
    pydantic==2.8.2; python_version >= '3.10'
    httpx
    -r other.txt
    """
    result = parse_requirements_txt(content)
    assert result.language == "Python"
    assert result.package_manager == "pip"
    assert "fastapi" in result.dependencies
    assert "pydantic" in result.dependencies
    assert "httpx" in result.dependencies


def test_parse_cargo_toml():
    content = """
    [package]
    name = "ripgrep"
    version = "14.1.0"
    edition = "2021"

    [dependencies]
    clap = "4.4"
    regex = "1.10"
    """
    result = parse_cargo_toml(content)
    assert result.language == "Rust"
    assert result.package_manager == "cargo"
    assert result.install_command == "cargo build"
    assert "clap" in result.dependencies
    assert "regex" in result.dependencies


def test_parse_go_mod():
    content = """
    module github.com/gin-gonic/gin

    go 1.21

    require (
        github.com/stretchr/testify v1.8.4
        golang.org/x/net v0.19.0
    )
    """
    result = parse_go_mod(content)
    assert result.language == "Go"
    assert result.runtime == "Go 1.21"
    assert result.package_manager == "go modules"
    assert "github.com/stretchr/testify" in result.dependencies


def test_parse_pom_xml():
    content = """
    <project>
        <dependencies>
            <dependency>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-starter-web</artifactId>
            </dependency>
        </dependencies>
    </project>
    """
    result = parse_pom_xml(content)
    assert result.language == "Java"
    assert result.package_manager == "Maven"
    assert "org.springframework.boot:spring-boot-starter-web" in result.dependencies


def test_dependency_analyzer_priority():
    analyzer = DependencyAnalyzer()
    raw_files = {
        "package.json": '{"name": "root", "scripts": {"dev": "npm run dev"}}',
        "requirements.txt": "requests==2.31.0",
    }
    # package.json should take precedence over requirements.txt when both present at root
    res = analyzer.analyze(raw_files)
    assert res.language == "JavaScript / TypeScript"
