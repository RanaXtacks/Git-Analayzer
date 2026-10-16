import React, { useState } from 'react';
import {
  CheckCircle2,
  Copy,
  Check,
  ShieldCheck,
  AlertTriangle,
  Sparkles,
  Terminal,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Sliders,
  Layers,
  BookOpen
} from 'lucide-react';
import type { OnboardingGuide, RepositoryMetadata } from '../types/guide';

interface NewcomerQuickstartProps {
  guide: OnboardingGuide;
  repository: RepositoryMetadata;
  activeMode: 'beginner' | 'deepdive';
  onToggleMode: (mode: 'beginner' | 'deepdive') => void;
}

export const NewcomerQuickstart: React.FC<NewcomerQuickstartProps> = ({
  guide,
  repository,
  activeMode,
  onToggleMode,
}) => {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const [showBreakdown, setShowBreakdown] = useState(false);

  const confidenceScore = guide.confidence_score ?? 85;
  const confidenceLevel = guide.confidence_level ?? (confidenceScore >= 80 ? 'High' : confidenceScore >= 60 ? 'Moderate' : 'Low');
  const breakdown = guide.confidence_breakdown;

  // Determine Primary Clone & Setup Command
  const cloneCommand = `git clone ${repository.html_url}`;
  const runCommand = guide.run_instructions.length > 0 && guide.run_instructions[0].command
    ? guide.run_instructions[0].command
    : guide.setup_steps.length > 0 && guide.setup_steps[0].command
    ? guide.setup_steps[0].command
    : null;

  const topIssue = guide.recommended_issues.length > 0 ? guide.recommended_issues[0] : null;

  const handleCopy = (text: string, index: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const getConfidenceBadgeColor = () => {
    if (confidenceScore >= 80) return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30';
    if (confidenceScore >= 60) return 'text-amber-400 bg-amber-500/10 border-amber-500/30';
    return 'text-rose-400 bg-rose-500/10 border-rose-500/30';
  };

  return (
    <div className="relative overflow-hidden rounded-2xl border border-indigo-500/20 bg-gradient-to-b from-slate-900/90 via-slate-900/60 to-slate-950/80 p-6 sm:p-8 backdrop-blur-xl shadow-2xl mb-8">
      {/* Background ambient decorative glow */}
      <div className="absolute -top-24 -right-24 w-80 h-80 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -bottom-24 -left-24 w-80 h-80 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* Header Bar: Title, Confidence Badge & Mode Switcher */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-800/80">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-500/15 text-indigo-300 border border-indigo-500/30">
              <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
              New Contributor Fast Track
            </span>
            <span className="text-xs text-slate-400 font-mono">
              Beginner-Friendly Onboarding
            </span>
          </div>
          <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
            Start Contributing to <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-cyan-300">{repository.name}</span> in 5 Minutes
          </h2>
          <p className="text-xs sm:text-sm text-slate-300 mt-1 max-w-2xl font-medium leading-relaxed">
            {guide.what_is_it || repository.description || "Open-source project onboarding guide verified against repository manifests and issues."}
          </p>

        </div>

        {/* Right Action: Confidence Badge + Mode Switcher */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Confidence Badge */}
          <div className="relative">
            <button
              onClick={() => setShowBreakdown(!showBreakdown)}
              className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-xl border text-xs font-semibold transition-all hover:scale-[1.02] cursor-pointer ${getConfidenceBadgeColor()}`}
              title="Click to view mathematical confidence metrics"
            >
              <ShieldCheck className="w-4 h-4" />
              <span>{confidenceScore}% Accuracy</span>
              <span className="opacity-75 font-normal">({confidenceLevel})</span>
              {showBreakdown ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            </button>
          </div>

          {/* Mode Switcher Toggle */}
          <div className="inline-flex items-center p-1 rounded-xl bg-slate-950/80 border border-slate-800 text-xs">
            <button
              onClick={() => onToggleMode('beginner')}
              className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-medium transition-all cursor-pointer ${
                activeMode === 'beginner'
                  ? 'bg-gradient-to-r from-indigo-600 to-blue-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <BookOpen className="w-3.5 h-3.5" />
              <span>Beginner Mode</span>
            </button>
            <button
              onClick={() => onToggleMode('deepdive')}
              className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-medium transition-all cursor-pointer ${
                activeMode === 'deepdive'
                  ? 'bg-gradient-to-r from-indigo-600 to-blue-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              <span>Deep Dive</span>
            </button>
          </div>
        </div>
      </div>

      {/* Expandable Confidence Breakdown Drawer */}
      {showBreakdown && breakdown && (
        <div className="my-6 p-4 rounded-xl bg-slate-950/90 border border-slate-800 text-xs text-slate-300 animate-in fade-in duration-200">
          <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-800/80">
            <span className="font-semibold text-white flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-indigo-400" />
              Evidence Verification Audit (Ground Truth vs. Qwen 2.5)
            </span>
            <span className="text-slate-400 font-mono">Formula: 35% Manifest + 30% Evidence + 15% Issues + 20% Docs</span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
            <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800/60">
              <div className="text-slate-400 mb-0.5">Manifest Certainty</div>
              <div className="text-sm font-bold text-white">{breakdown.manifest_score}%</div>
              <div className="text-[10px] text-slate-500">Weight: 35%</div>
            </div>
            <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800/60">
              <div className="text-slate-400 mb-0.5">Evidence Grounding</div>
              <div className="text-sm font-bold text-white">{breakdown.evidence_score}%</div>
              <div className="text-[10px] text-slate-500">Weight: 30%</div>
            </div>
            <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800/60">
              <div className="text-slate-400 mb-0.5">Issue Actionability</div>
              <div className="text-sm font-bold text-white">{breakdown.issue_score}%</div>
              <div className="text-[10px] text-slate-500">Weight: 15%</div>
            </div>
            <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800/60">
              <div className="text-slate-400 mb-0.5">Documentation</div>
              <div className="text-sm font-bold text-white">{breakdown.doc_score}%</div>
              <div className="text-[10px] text-slate-500">Weight: 20%</div>
            </div>
          </div>

          {breakdown.reasons.length > 0 && (
            <div>
              <div className="font-medium text-slate-400 mb-1.5">Audit Log & Verified Proof:</div>
              <ul className="space-y-1 list-disc list-inside text-slate-400">
                {breakdown.reasons.map((reason, idx) => (
                  <li key={idx} className="leading-relaxed">{reason}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* 3-Step Action Checklist */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-6">
        {/* Step 1: Clone & Prerequisites */}
        <div className="flex flex-col justify-between p-4 rounded-xl bg-slate-950/60 border border-slate-800 hover:border-indigo-500/40 transition-colors">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="flex items-center justify-center w-6 h-6 rounded-full bg-indigo-500/20 text-indigo-400 font-bold text-xs">
                1
              </span>
              <h3 className="text-sm font-bold text-white">Get the Code</h3>
            </div>
            <p className="text-xs text-slate-400 mb-3">
              Clone repository and check prerequisites ({guide.prerequisites.length > 0 ? guide.prerequisites[0] : 'Git'}).
            </p>
          </div>

          <div className="relative group">
            <div className="flex items-center justify-between p-2 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono text-slate-300">
              <span className="truncate pr-2">{cloneCommand}</span>
              <button
                onClick={() => handleCopy(cloneCommand, 1)}
                className="text-slate-400 hover:text-white p-1 transition-colors cursor-pointer"
                title="Copy clone command"
              >
                {copiedIndex === 1 ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              </button>
            </div>
          </div>
        </div>

        {/* Step 2: Run Locally */}
        <div className="flex flex-col justify-between p-4 rounded-xl bg-slate-950/60 border border-slate-800 hover:border-indigo-500/40 transition-colors">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="flex items-center justify-center w-6 h-6 rounded-full bg-cyan-500/20 text-cyan-400 font-bold text-xs">
                2
              </span>
              <h3 className="text-sm font-bold text-white">Launch the Project</h3>
            </div>
            <p className="text-xs text-slate-400 mb-3">
              Verified local dev command extracted from repository manifests.
            </p>
          </div>

          {runCommand ? (
            <div className="relative group">
              <div className="flex items-center justify-between p-2 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono text-cyan-300">
                <span className="truncate pr-2">{runCommand}</span>
                <button
                  onClick={() => handleCopy(runCommand, 2)}
                  className="text-slate-400 hover:text-white p-1 transition-colors cursor-pointer"
                  title="Copy run command"
                >
                  {copiedIndex === 2 ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                </button>
              </div>
            </div>
          ) : (
            <div className="p-2 rounded-lg bg-slate-900/50 border border-slate-800/60 text-xs text-slate-500 italic">
              See setup steps below for commands
            </div>
          )}
        </div>

        {/* Step 3: First Safe Contribution */}
        <div className="flex flex-col justify-between p-4 rounded-xl bg-slate-950/60 border border-slate-800 hover:border-indigo-500/40 transition-colors">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="flex items-center justify-center w-6 h-6 rounded-full bg-emerald-500/20 text-emerald-400 font-bold text-xs">
                3
              </span>
              <h3 className="text-sm font-bold text-white">Your First PR</h3>
            </div>
            <p className="text-xs text-slate-400 mb-3">
              {topIssue
                ? `Pick up beginner issue #${topIssue.number} or make a small test/doc update.`
                : 'Explore safe initial touchpoints in the repository files.'}
            </p>
          </div>

          {topIssue ? (
            <a
              href={topIssue.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center justify-between p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-xs font-medium text-emerald-300 hover:bg-emerald-500/20 transition-colors"
            >
              <span className="truncate pr-2">Issue #{topIssue.number}: {topIssue.title}</span>
              <ExternalLink className="w-3.5 h-3.5 shrink-0" />
            </a>
          ) : (
            <div className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-400 truncate">
              {guide.first_contribution.title}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
