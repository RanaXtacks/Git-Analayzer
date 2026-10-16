import React from 'react';
import { Sparkles, ExternalLink, Award, Zap, BookOpen, Flame, TrendingUp } from 'lucide-react';
import type { RecommendedIssue } from '../types/guide';
import { EvidenceBadge } from './EvidenceBadge';

interface IssueRecommendationsProps {
  issues: RecommendedIssue[];
  repoUrl?: string;
  defaultBranch?: string;
}

const difficultyConfig = {
  Beginner: {
    icon: BookOpen,
    label: 'Beginner',
    tagline: 'Great first issue',
    gradient: 'from-emerald-500/20 to-emerald-900/10',
    border: 'border-emerald-500/40',
    badge: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/50 ring-1 ring-emerald-500/20',
    iconColor: 'text-emerald-400',
    dot: 'bg-emerald-400',
    bar: 'bg-gradient-to-r from-emerald-500 to-emerald-400',
  },
  Intermediate: {
    icon: Zap,
    label: 'Intermediate',
    tagline: 'Some experience needed',
    gradient: 'from-amber-500/20 to-amber-900/10',
    border: 'border-amber-500/40',
    badge: 'bg-amber-500/20 text-amber-300 border-amber-500/50 ring-1 ring-amber-500/20',
    iconColor: 'text-amber-400',
    dot: 'bg-amber-400',
    bar: 'bg-gradient-to-r from-amber-500 to-amber-400',
  },
  Advanced: {
    icon: Flame,
    label: 'Advanced',
    tagline: 'Experienced contributors',
    gradient: 'from-purple-500/20 to-purple-900/10',
    border: 'border-purple-500/40',
    badge: 'bg-purple-500/20 text-purple-300 border-purple-500/50 ring-1 ring-purple-500/20',
    iconColor: 'text-purple-400',
    dot: 'bg-purple-400',
    bar: 'bg-gradient-to-r from-purple-500 to-purple-400',
  },
} as const;

function getDifficultyConfig(difficulty: string) {
  if (difficulty in difficultyConfig) {
    return difficultyConfig[difficulty as keyof typeof difficultyConfig];
  }
  return difficultyConfig.Beginner;
}

export const IssueRecommendations: React.FC<IssueRecommendationsProps> = ({
  issues,
  repoUrl,
  defaultBranch,
}) => {
  // Sort issues by score descending for priority ordering
  const sortedIssues = [...issues].sort((a, b) => b.score - a.score);

  return (
    <div className="glass-panel rounded-2xl p-6 mb-8 border border-slate-800 shadow-lg">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2.5 text-cyan-400 font-semibold">
          <Sparkles className="w-5 h-5 text-cyan-400" />
          <h2 className="text-lg text-white">Recommended Beginner Issues</h2>
        </div>
        <span className="text-xs text-slate-400">
          Ranked deterministically for newcomer friendliness
        </span>
      </div>

      {/* Difficulty Legend */}
      {sortedIssues.length > 0 && (
        <div className="flex flex-wrap gap-3 mb-5 p-3 rounded-xl bg-slate-900/40 border border-slate-800/60">
          {Object.entries(difficultyConfig).map(([key, cfg]) => {
            const Icon = cfg.icon;
            const count = sortedIssues.filter(i => i.difficulty === key).length;
            if (count === 0) return null;
            return (
              <div key={key} className="flex items-center gap-1.5 text-xs text-slate-300">
                <span className={`w-2 h-2 rounded-full ${cfg.dot}`} />
                <Icon className={`w-3.5 h-3.5 ${cfg.iconColor}`} />
                <span className="font-medium">{cfg.label}</span>
                <span className="text-slate-500">({count})</span>
              </div>
            );
          })}
        </div>
      )}

      {sortedIssues.length === 0 ? (
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-sm text-slate-400 text-center">
          No open beginner-labeled issues currently available in this repository. Consider exploring the suggested first contribution roadmap above!
        </div>
      ) : (
        <div className="space-y-4">
          {sortedIssues.map((issue, index) => {
            const cfg = getDifficultyConfig(issue.difficulty);
            const DiffIcon = cfg.icon;
            const maxScore = Math.max(...sortedIssues.map(i => i.score), 1);

            return (
              <div
                key={issue.number}
                className={`relative p-5 rounded-xl bg-gradient-to-r ${cfg.gradient} border ${cfg.border} hover:shadow-md hover:shadow-cyan-950/30 transition-all`}
              >
                {/* Priority number badge */}
                <div className="absolute -top-2.5 -left-2.5 w-7 h-7 rounded-full bg-slate-900 border-2 border-cyan-500 flex items-center justify-center">
                  <span className="text-xs font-bold text-cyan-300">{index + 1}</span>
                </div>

                <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                  <div className="flex-1 pl-4">
                    {/* Top row: issue number + difficulty badge + score */}
                    <div className="flex flex-wrap items-center gap-2.5 mb-2">
                      <span className="text-sm font-bold text-cyan-400 font-mono">
                        #{issue.number}
                      </span>

                      {/* Prominent difficulty badge */}
                      <span
                        className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold border ${cfg.badge}`}
                      >
                        <DiffIcon className="w-3.5 h-3.5" />
                        {issue.difficulty}
                      </span>

                      {issue.score > 0 && (
                        <span className="inline-flex items-center gap-1 text-[11px] px-2 py-0.5 rounded-full bg-slate-800/80 text-slate-300 border border-slate-700">
                          <Award className="w-3 h-3 text-cyan-400" /> Score: {issue.score}
                        </span>
                      )}
                    </div>

                    {/* Issue title */}
                    <h3 className="text-base font-semibold text-white leading-snug mb-1">
                      {issue.title}
                    </h3>

                    {/* Tagline */}
                    <p className="text-[11px] text-slate-500 mb-2 flex items-center gap-1">
                      <TrendingUp className="w-3 h-3" />
                      {cfg.tagline} · Priority #{index + 1}
                    </p>

                    {/* Score progress bar */}
                    {issue.score > 0 && (
                      <div className="w-full max-w-[200px] h-1.5 bg-slate-800 rounded-full overflow-hidden mb-3">
                        <div
                          className={`h-full rounded-full ${cfg.bar} transition-all duration-500`}
                          style={{ width: `${Math.round((issue.score / maxScore) * 100)}%` }}
                        />
                      </div>
                    )}

                    {/* Reason */}
                    <p className="text-sm text-slate-300 leading-relaxed">
                      <strong className="text-slate-200">Why suitable:</strong> {issue.reason}
                    </p>

                    <EvidenceBadge
                      evidence={issue.evidence}
                      repoUrl={repoUrl}
                      defaultBranch={defaultBranch}
                    />
                  </div>

                  <div className="shrink-0 self-start md:self-center">
                    <a
                      href={issue.url}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-cyan-950 hover:bg-cyan-900 text-cyan-300 border border-cyan-800 text-xs sm:text-sm font-semibold transition-colors cursor-pointer shadow-sm"
                    >
                      Open Issue <ExternalLink className="w-3.5 h-3.5" />
                    </a>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
