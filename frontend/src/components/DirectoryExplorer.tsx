import React from 'react';
import { FolderGit2, Info } from 'lucide-react';
import { DirectoryInfo } from '../types/guide';
import { EvidenceBadge } from './EvidenceBadge';

interface DirectoryExplorerProps {
  directories: DirectoryInfo[];
  repoUrl?: string;
  defaultBranch?: string;
}

export const DirectoryExplorer: React.FC<DirectoryExplorerProps> = ({
  directories,
  repoUrl,
  defaultBranch,
}) => {
  return (
    <div className="glass-panel rounded-2xl p-6 mb-8 border border-slate-800 shadow-lg">
      <div className="flex items-center gap-2.5 text-cyan-400 font-semibold mb-6">
        <FolderGit2 className="w-5 h-5 text-cyan-400" />
        <h2 className="text-lg text-white">Important Directories & Architecture</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {directories.map((dir, idx) => (
          <div
            key={idx}
            className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition-colors flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center gap-2 font-mono text-sm font-semibold text-cyan-300">
                <span className="px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800/60 text-xs">
                  {dir.path}
                </span>
              </div>
              <p className="mt-2 text-sm text-slate-200 font-medium leading-relaxed">
                {dir.description}
              </p>
              <div className="mt-2.5 text-xs text-slate-400 bg-slate-950/60 p-2.5 rounded-lg border border-slate-850 flex items-start gap-2">
                <Info className="w-3.5 h-3.5 text-cyan-400 shrink-0 mt-0.5" />
                <span>
                  <strong className="text-slate-300">Why it matters:</strong> {dir.reason_to_care}
                </span>
              </div>
            </div>

            <div className="mt-3">
              <EvidenceBadge
                evidence={dir.evidence}
                repoUrl={repoUrl}
                defaultBranch={defaultBranch}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
