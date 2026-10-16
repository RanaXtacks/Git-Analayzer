import React from 'react';
import { ArrowLeft, Compass, RotateCcw } from 'lucide-react';
import { AnalysisResponse } from '../types/guide';
import { RepositoryHeader } from '../components/RepositoryHeader';
import { ProjectSummary } from '../components/ProjectSummary';
import { Prerequisites } from '../components/Prerequisites';
import { SetupGuide } from '../components/SetupGuide';
import { RunInstructions } from '../components/RunInstructions';
import { FirstContribution } from '../components/FirstContribution';
import { IssueRecommendations } from '../components/IssueRecommendations';
import { DirectoryExplorer } from '../components/DirectoryExplorer';
import { ContributionWorkflow } from '../components/ContributionWorkflow';
import { WarningPanel } from '../components/WarningPanel';

interface GuideViewProps {
  data: AnalysisResponse;
  onReset: () => void;
}

export const GuideView: React.FC<GuideViewProps> = ({ data, onReset }) => {
  const { repository, guide, metadata } = data;

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
      {/* Top back bar */}
      <div className="flex items-center justify-between mb-6">
        <button
          onClick={onReset}
          className="inline-flex items-center gap-2 text-xs sm:text-sm font-medium text-slate-400 hover:text-white transition-colors cursor-pointer"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Analyze another repository</span>
        </button>

        <div className="flex items-center gap-2 text-xs text-slate-500 font-mono">
          <span>Analysis generated in {metadata.duration_seconds || '—'}s</span>
        </div>
      </div>

      {/* 1. Repository Header */}
      <RepositoryHeader repository={repository} metadata={metadata} />

      {/* 2. Project Summary & Where to Start */}
      <ProjectSummary
        summary={guide.project_summary}
        whereToStart={guide.where_to_start}
      />

      {/* 3. Prerequisites */}
      <Prerequisites prerequisites={guide.prerequisites} />

      {/* 4. First Contribution Spotlight */}
      <FirstContribution
        firstContribution={guide.first_contribution}
        repoUrl={repository.html_url}
        defaultBranch={repository.default_branch}
      />

      {/* 5. Recommended Beginner Issues */}
      <IssueRecommendations
        issues={guide.recommended_issues}
        repoUrl={repository.html_url}
        defaultBranch={repository.default_branch}
      />

      {/* 6. Setup Guide */}
      <SetupGuide
        steps={guide.setup_steps}
        repoUrl={repository.html_url}
        defaultBranch={repository.default_branch}
      />

      {/* 7. Run Locally */}
      <RunInstructions
        instructions={guide.run_instructions}
        repoUrl={repository.html_url}
        defaultBranch={repository.default_branch}
      />

      {/* 8. Important Directories & Architecture */}
      <DirectoryExplorer
        directories={guide.important_directories}
        repoUrl={repository.html_url}
        defaultBranch={repository.default_branch}
      />

      {/* 9. Contribution Workflow */}
      <ContributionWorkflow workflow={guide.contribution_workflow} />

      {/* 10. Warnings & Uncertainties */}
      <WarningPanel warnings={guide.warnings} />

      {/* Bottom CTA */}
      <div className="text-center py-12 border-t border-slate-800/80 mt-12">
        <h3 className="text-lg font-bold text-white mb-2">Ready to explore another codebase?</h3>
        <p className="text-sm text-slate-400 mb-6">
          Git-Analyzer can guide you through any public GitHub repository.
        </p>
        <button
          onClick={onReset}
          className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-sm transition-colors cursor-pointer shadow-lg shadow-cyan-600/20"
        >
          <RotateCcw className="w-4 h-4" /> Analyze Another Repository
        </button>
      </div>
    </div>
  );
};
