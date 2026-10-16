import React, { useState } from 'react';
import { FileText, ExternalLink } from 'lucide-react';
import { Evidence } from '../types/guide';

interface EvidenceBadgeProps {
  evidence?: Evidence[];
  repoUrl?: string;
  defaultBranch?: string;
}

export const EvidenceBadge: React.FC<EvidenceBadgeProps> = ({
  evidence,
  repoUrl,
  defaultBranch = 'main',
}) => {
  const [open, setOpen] = useState(false);

  if (!evidence || evidence.length === 0) return null;

  return (
    <div className="relative inline-block text-left mt-2">
      <button
        onClick={() => setOpen(!open)}
        className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-cyan-950/60 text-cyan-300 border border-cyan-800/60 hover:bg-cyan-900/60 hover:border-cyan-700 transition-colors cursor-pointer"
        title="Inspect supporting evidence for this item"
      >
        <FileText className="w-3 h-3 text-cyan-400" />
        <span>Evidence ({evidence.length})</span>
      </button>

      {open && (
        <>
          <div
            className="fixed inset-0 z-40"
            onClick={() => setOpen(false)}
            aria-hidden="true"
          />
          <div className="absolute left-0 mt-2 w-80 max-w-sm rounded-xl glass-panel p-3.5 z-50 shadow-2xl border border-cyan-800/40 text-xs">
            <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-700/60">
              <span className="font-semibold text-cyan-300 flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5" /> Verified Repository Evidence
              </span>
              <button
                onClick={() => setOpen(false)}
                className="text-slate-400 hover:text-white font-bold px-1"
              >
                ✕
              </button>
            </div>
            <div className="space-y-2.5 max-h-60 overflow-y-auto pr-1">
              {evidence.map((item, idx) => {
                let githubLink = '';
                if (repoUrl && item.source && !item.source.startsWith('http')) {
                  const cleanedSource = item.source.trim();
                  if (cleanedSource.includes('.')) {
                    githubLink = `${repoUrl}/blob/${defaultBranch}/${cleanedSource}`;
                  }
                }

                return (
                  <div key={idx} className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                    <div className="flex items-center justify-between text-slate-300 font-medium">
                      <span className="text-cyan-400">{item.source}</span>
                      {githubLink && (
                        <a
                          href={githubLink}
                          target="_blank"
                          rel="noreferrer"
                          className="text-slate-400 hover:text-cyan-300 flex items-center gap-0.5"
                          title="Open in GitHub"
                        >
                          View <ExternalLink className="w-2.5 h-2.5" />
                        </a>
                      )}
                    </div>
                    {item.location && (
                      <div className="text-slate-400 text-[11px] mt-0.5">
                        Location: <span className="text-slate-300">{item.location}</span>
                      </div>
                    )}
                    {item.detail && (
                      <div className="mt-1 font-mono text-[11px] text-emerald-300 bg-slate-950/60 p-1.5 rounded border border-slate-800 break-words">
                        {item.detail}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </>
      )}
    </div>
  );
};
