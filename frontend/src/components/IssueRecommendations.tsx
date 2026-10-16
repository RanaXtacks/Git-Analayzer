import React from 'react';
import { Sparkles, ExternalLink, Award, CheckCircle } from 'lucide-react';
import { RecommendedIssue } from '../types/guide';
import { EvidenceBadge } from './EvidenceBadge';

interface IssueRecommendationsProps {
  issues: RecommendedIssue[];
  repoUrl?: string;
  defaultBranch?: string;
}

export const IssueRecommendations: React.FC<IssueRecommendationsProps> = ({
  issues,
  repoUrl,
  defaultBranch,
}) => {
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

      {issues.length === 0 ? (
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-sm text-slate-400 text-center">
          No open beginner-labeled issues currently available in this repository. Consider exploring the suggested first contribution roadmap above!
        </div>
      ) : (
        <div className="space-y-4">
          {issues.map((issue) => (
            <div
              key={issue.number}
              className="p-4 sm:p-5 rounded-xl bg-slate-900/60 border border-slate-850 hover:border-slate-750 transition-all flex flex-col md:flex-row md:items-center justify-between gap-4"
            >
              <div className="flex-1">
                <div className="flex flex-wrap items-center gap-2.5 mb-1.5">
                  <span className="text-sm font-bold text-cyan-400 font-mono">
                    #{issue.number}
                  </span>

                  <span
                    className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                      issue.difficulty === 'Beginner'
                        ? 'bg-emerald-950/80 text-emerald-300 border border-emerald-800/60'
                        : issue.difficulty === 'Intermediate'
                        ? 'bg-amber-950/80 text-amber-300 border border-amber-800/60'
                        : 'bg-purple-950/80 text-purple-300 border border-purple-800/60'
                    }`}
                  >
                    {issue.difficulty}
                  </span>

                  {issue.score > 0 && (
                    <span className="inline-flex items-center gap-1 text-[11px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                      <Award className="w-3 h-3 text-cyan-400" /> Score: {issue.score}
                    </span>
                  )}
                </div>

                <h3 className="text-base font-semibold text-white leading-snug">
                  {issue.title}
                </h3>

                <p className="mt-2 text-sm text-slate-300 leading-relaxed">
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
          ))}
        </div>
      )}
    </div>
  );
};
