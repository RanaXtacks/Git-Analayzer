import React, { useState } from 'react';
import { 
  ArrowLeft, 
  RotateCcw, 
  Sliders, 
  Zap, 
  BookOpen, 
  Layers, 
  Sparkles 
} from 'lucide-react';
import type { AnalysisResponse } from '../types/guide';
import { RepositoryHeader } from '../components/RepositoryHeader';
import { NewcomerQuickstart } from '../components/NewcomerQuickstart';
import { ProjectSummary } from '../components/ProjectSummary';
import { Prerequisites } from '../components/Prerequisites';
import { SetupGuide } from '../components/SetupGuide';
import { RunInstructions } from '../components/RunInstructions';
import { FirstContribution } from '../components/FirstContribution';
import { IssueRecommendations } from '../components/IssueRecommendations';
import { DirectoryExplorer } from '../components/DirectoryExplorer';
import { ContributionWorkflow } from '../components/ContributionWorkflow';
import { WarningPanel } from '../components/WarningPanel';
import { WhatMakesDiffSection } from '../components/WhatMakesDiffSection';
import { ExecutionPlans } from '../components/ExecutionPlans';
import { DeepArchitectureExplorer } from '../components/DeepArchitectureExplorer';

interface GuideViewProps {
  data: AnalysisResponse;
  onReset: () => void;
}

type DepthMode = 'all' | 'tldr' | 'standard' | 'deep';

export const GuideView: React.FC<GuideViewProps> = ({ data, onReset }) => {
  const { repository, guide, metadata } = data;
  const [depthMode, setDepthMode] = useState<DepthMode>('all');
  const [quickstartMode, setQuickstartMode] = useState<'beginner' | 'deepdive'>('beginner');

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

      {/* 2. Newcomer Fast Track & Accuracy Gauge */}
      <NewcomerQuickstart
        guide={guide}
        repository={repository}
        activeMode={quickstartMode}
        onToggleMode={(mode) => {
          setQuickstartMode(mode);
          if (mode === 'deepdive') {
            setDepthMode('deep');
          } else {
            setDepthMode('standard');
          }
        }}
      />

      {/* 3. Adjustable Depth Mode Bar */}
      <div className="mb-8 p-3 sm:p-4 rounded-2xl glass-panel border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-3 bg-slate-900/40">
        <div className="flex items-center gap-2.5">
          <Sliders className="w-4 h-4 text-cyan-400 shrink-0" />
          <div>
            <span className="text-xs font-bold text-white uppercase tracking-wider block">
              Adjustable Explanation Depth
            </span>
            <span className="text-[11px] text-slate-400">
              Customize the level of detail and execution focus
            </span>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-1.5 p-1 bg-slate-950/80 rounded-xl border border-slate-800">
          <button
            onClick={() => setDepthMode('all')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer flex items-center gap-1.5 ${
              depthMode === 'all'
                ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Complete Guide</span>
          </button>
          <button
            onClick={() => setDepthMode('tldr')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer flex items-center gap-1.5 ${
              depthMode === 'tldr'
                ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Zap className="w-3.5 h-3.5" />
            <span>TL;DR (1-Min)</span>
          </button>
          <button
            onClick={() => setDepthMode('standard')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer flex items-center gap-1.5 ${
              depthMode === 'standard'
                ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <BookOpen className="w-3.5 h-3.5" />
            <span>Contributor Fast Track</span>
          </button>
          <button
            onClick={() => setDepthMode('deep')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer flex items-center gap-1.5 ${
              depthMode === 'deep'
                ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>Deep Architectural</span>
          </button>
        </div>
      </div>

      {/* 4. What Makes Our Project Different (Highlighted in All and Deep modes) */}
      {(depthMode === 'all' || depthMode === 'deep') && guide.differentiation_matrix && guide.differentiation_matrix.length > 0 && (
        <WhatMakesDiffSection diffPoints={guide.differentiation_matrix} />
      )}

      {/* 5. Project Summary & Where to Start */}
      <ProjectSummary
        summary={guide.project_summary}
        whereToStart={guide.where_to_start}
        whatIsIt={guide.what_is_it}
        whyItExists={guide.why_it_exists}
        howItWorks={guide.how_it_works}
        whoIsItFor={guide.who_is_it_for}
        deepExplanation={guide.deep_architecture?.explanation}
        pattern={guide.deep_architecture?.pattern}
      />


      {/* 6. Deep Architectural Explorer (Lifecycle pipeline) */}
      {(depthMode === 'all' || depthMode === 'deep') && guide.deep_architecture && (
        <DeepArchitectureExplorer
          architecture={guide.deep_architecture}
          repoUrl={repository.html_url}
          defaultBranch={repository.default_branch}
        />
      )}

      {/* 7. Targeted Execution Plans (Multi-track action roadmaps) */}
      {(depthMode === 'all' || depthMode === 'deep' || depthMode === 'standard') && guide.execution_plans && guide.execution_plans.length > 0 && (
        <ExecutionPlans
          plans={guide.execution_plans}
          repoUrl={repository.html_url}
          defaultBranch={repository.default_branch}
        />
      )}

      {/* 8. Prerequisites */}
      {(depthMode === 'all' || depthMode === 'standard' || depthMode === 'tldr') && (
        <Prerequisites prerequisites={guide.prerequisites} />
      )}

      {/* 9. First Contribution Spotlight */}
      <FirstContribution
        firstContribution={guide.first_contribution}
        repoUrl={repository.html_url}
        defaultBranch={repository.default_branch}
      />

      {/* 10. Recommended Beginner Issues */}
      {(depthMode === 'all' || depthMode === 'standard' || depthMode === 'deep') && (
        <IssueRecommendations
          issues={guide.recommended_issues}
          repoUrl={repository.html_url}
          defaultBranch={repository.default_branch}
        />
      )}

      {/* 11. Setup Guide */}
      <SetupGuide
        steps={guide.setup_steps}
        repoUrl={repository.html_url}
        defaultBranch={repository.default_branch}
      />

      {/* 12. Run Locally */}
      <RunInstructions
        instructions={guide.run_instructions}
        repoUrl={repository.html_url}
        defaultBranch={repository.default_branch}
      />

      {/* 13. Important Directories & Architecture */}
      {(depthMode === 'all' || depthMode === 'standard' || depthMode === 'deep') && (
        <DirectoryExplorer
          directories={guide.important_directories}
          repoUrl={repository.html_url}
          defaultBranch={repository.default_branch}
        />
      )}

      {/* 14. Contribution Workflow */}
      {(depthMode === 'all' || depthMode === 'standard') && (
        <ContributionWorkflow workflow={guide.contribution_workflow} />
      )}

      {/* 15. Warnings & Uncertainties */}
      <WarningPanel warnings={guide.warnings} />

      {/* Bottom CTA */}
      <div className="text-center py-12 border-t border-slate-800/80 mt-12">
        <h3 className="text-lg font-bold text-white mb-2">Ready to explore another codebase?</h3>
        <p className="text-sm text-slate-400 mb-6">
          Git-Analyzer can guide you through any public GitHub repository with verified ground truth.
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
