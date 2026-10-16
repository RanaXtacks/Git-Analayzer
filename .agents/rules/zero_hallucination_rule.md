# Rule: Zero-Hallucination Principle

When generating any summary or analysis of a repository, **do not fabricate information**. Every fact, file excerpt, or configuration detail must be accompanied by a citation indicating the source file and line range (e.g., `[README.md:12-15]`). If the required information is not present in the repository, explicitly state that it could not be found rather than guessing.

This rule applies to all future analysis workflows, including the `analyse_repository` skill.
