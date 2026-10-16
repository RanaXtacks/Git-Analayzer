import React from 'react';
import { Star, GitFork, AlertCircle, BookOpen, ExternalLink, GitBranch, ShieldCheck } from 'lucide-react';
import { RepositoryMetadata, AnalysisMetadata } from '../types/guide';

interface RepositoryHeaderProps {
  repository: RepositoryMetadata;
  metadata?: AnalysisMetadata;
}

export const RepositoryHeader: React.FC<RepositoryHeaderProps> = ({ repository, metadata }) => {
  return (
    <div className="glass-panel rounded-2xl p-6 sm:p-8 mb-8 border border-slate-800 shadow-xl relative overflow-hidden">
      {/* Decorative gradient blur background */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20" />
      <div className="absolute bottom-0 left-0 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl pointer-events-none -ml-20 -mb-20" />

      <div className="relative z-10">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800/80">
          <div>
            <div className="flex items-center gap-2 text-sm text-slate-400 font-medium mb-1">
              <span>{repository.owner}</span>
              <span>/</span>
              <span className="text-white font-semibold">{repository.name}</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white flex items-center gap-3">
              {repository.name}
              {repository.license && (
                <span className="text-xs font-medium px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                  {repository.license}
                </span>
              )}
            </h1>
          </div>

          <div className="flex items-center gap-3">
            <a
              href={repository.html_url}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white border border-slate-700 text-sm font-medium transition-colors shadow-sm"
            >
              <ExternalLink className="w-4 h-4" />
              View on GitHub
            </a>
          </div>
        </div>

        {repository.description && (
          <p className="mt-4 text-slate-300 text-base leading-relaxed max-w-3xl">
            {repository.description}
          </p>
        )}

        {/* Metadata badges bar */}
        <div className="mt-6 flex flex-wrap items-center gap-3 text-xs sm:text-sm">
          {repository.language && (
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-cyan-950/40 text-cyan-300 border border-cyan-800/50 font-medium">
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
              {repository.language}
            </div>
          )}

          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800/60 text-slate-300 border border-slate-700/50">
            <Star className="w-3.5 h-3.5 text-amber-400 fill-amber-400/30" />
            <span>{repository.stars.toLocaleString()} stars</span>
          </div>

          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800/60 text-slate-300 border border-slate-700/50">
            <GitFork className="w-3.5 h-3.5 text-purple-400" />
            <span>{repository.forks.toLocaleString()} forks</span>
          </div>

          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800/60 text-slate-300 border border-slate-700/50">
            <AlertCircle className="w-3.5 h-3.5 text-emerald-400" />
            <span>{repository.open_issues_count} open issues</span>
          </div>

          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800/60 text-slate-400 border border-slate-700/50">
            <GitBranch className="w-3.5 h-3.5 text-slate-400" />
            <span>branch: {repository.default_branch}</span>
          </div>

          {metadata && (
            <div className="ml-auto flex items-center gap-2 text-xs text-slate-400 font-mono">
              <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" />
              <span>Model: {metadata.model}</span>
              {metadata.cached && (
                <span className="px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-400 border border-emerald-800/60 text-[10px]">
                  CACHED
                </span>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
