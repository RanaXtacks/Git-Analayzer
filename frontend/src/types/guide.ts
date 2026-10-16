export interface Evidence {
  source: string;
  location: string;
  detail: string;
}

export interface SetupStep {
  step: number;
  description: string;
  command?: string | null;
  evidence: Evidence[];
}

export interface DirectoryInfo {
  path: string;
  description: string;
  reason_to_care: string;
  evidence: Evidence[];
}

export interface RecommendedIssue {
  number: number;
  title: string;
  url: string;
  difficulty: "Beginner" | "Intermediate" | "Advanced" | string;
  reason: string;
  score: number;
  evidence: Evidence[];
}

export interface FirstContribution {
  title: string;
  description: string;
  suggested_files: string[];
  reasoning: string;
  evidence: Evidence[];
}

export interface ConfidenceBreakdown {
  manifest_score: number;
  evidence_score: number;
  issue_score: number;
  doc_score: number;
  hallucination_penalty: number;
  reasons: string[];
}

export interface OnboardingGuide {
  project_summary: string;
  prerequisites: string[];
  setup_steps: SetupStep[];
  run_instructions: SetupStep[];
  important_directories: DirectoryInfo[];
  where_to_start: string;
  recommended_issues: RecommendedIssue[];
  first_contribution: FirstContribution;
  contribution_workflow: string[];
  warnings: string[];
  confidence_score?: number;
  confidence_level?: "High" | "Moderate" | "Low" | string;
  confidence_breakdown?: ConfidenceBreakdown;
}


export interface RepositoryMetadata {
  owner: string;
  name: string;
  full_name: string;
  description?: string;
  language?: string | null;
  stars: number;
  forks: number;
  watchers: number;
  default_branch: string;
  license?: string | null;
  open_issues_count: number;
  html_url: string;
  created_at?: string | null;
  updated_at?: string | null;
  head_sha?: string | null;
}

export interface AnalysisMetadata {
  commit_sha?: string | null;
  model: string;
  provider: string;
  generated_at: string;
  cached: boolean;
  duration_seconds?: number | null;
}

export interface AnalysisResponse {
  repository: RepositoryMetadata;
  guide: OnboardingGuide;
  metadata: AnalysisMetadata;
}

export type ProgressStage =
  | "init"
  | "metadata"
  | "readme"
  | "contributing"
  | "structure"
  | "dependencies"
  | "configuration"
  | "issues"
  | "generating"
  | "validating"
  | "cache"
  | "complete";

export interface ProgressItem {
  stage: ProgressStage;
  status: "pending" | "running" | "complete" | "error";
  label: string;
  detail?: string;
}
