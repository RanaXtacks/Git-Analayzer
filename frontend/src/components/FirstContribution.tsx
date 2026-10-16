import React from 'react';
import { Target, FileCode, CheckCircle, Lightbulb } from 'lucide-react';
import { FirstContribution as FirstContribType } from '../types/guide';
import { EvidenceBadge } from './EvidenceBadge';

interface FirstContributionProps {
  firstContribution: FirstContribType;
  repoUrl?: string;
  defaultBranch?: string;
}

export const FirstContribution: React.FC<FirstContributionProps> = ({
  firstContribution,
  repoUrl,
  defaultBranch,
}) => {
  return (
    <div className="glass-panel rounded-2xl p-6 sm:p-8 mb-8 border border-cyan-800/60 bg-gradient-to-br from-cyan-950/20 via-slate-900/60 to-purple-950/20 shadow-2xl relative overflow-hidden">
      {/* Decorative accent */}
      <div className="absolute top-0 left-0 w-2 h-full bg-gradient-to-b from-cyan-400 via-teal-400 to-purple-500" />

      <div className="flex items-center gap-2.5 text-cyan-400 font-semibold mb-4">
        <Target className="w-6 h-6 text-cyan-400" />
        <h2 className="text-xl text-white">Suggested First Contribution</h2>
      </div>

      <h3 className="text-lg font-bold text-slate-100 mb-2">
        {firstContribution.title}
      </h3>

      <p className="text-slate-300 text-sm sm:text-base leading-relaxed mb-4">
        {firstContribution.description}
      </p>

      {/* Suggested files */}
      {firstContribution.suggested_files && firstContribution.suggested_files.length > 0 && (
        <div className="mb-4">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
            Suggested Files to Inspect / Modify
          </span>
          <div className="flex flex-wrap gap-2">
            {firstContribution.suggested_files.map((file, idx) => {
              const fileLink = repoUrl ? `${repoUrl}/blob/${defaultBranch || 'main'}/${file}` : '';
              return (
                <a
                  key={idx}
                  href={fileLink || '#'}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-950 font-mono text-xs text-cyan-300 border border-slate-800 hover:border-cyan-700 hover:bg-slate-900 transition-colors"
                >
                  <FileCode className="w-3.5 h-3.5 text-cyan-400" />
                  <span>{file}</span>
                </a>
              );
            })}
          </div>
        </div>
      )}

      {/* Reasoning card */}
      <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800/80 mb-4 flex items-start gap-2.5 text-xs sm:text-sm">
        <Lightbulb className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
        <span className="text-slate-300 leading-relaxed">
          <strong className="text-amber-300">Why this first:</strong> {firstContribution.reasoning}
        </span>
      </div>

      <EvidenceBadge
        evidence={firstContribution.evidence}
        repoUrl={repoUrl}
        defaultBranch={defaultBranch}
      />
    </div>
  );
};
