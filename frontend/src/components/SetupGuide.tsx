import React, { useState } from 'react';
import { Terminal, Copy, Check, Wrench } from 'lucide-react';
import { SetupStep } from '../types/guide';
import { EvidenceBadge } from './EvidenceBadge';

interface SetupGuideProps {
  steps: SetupStep[];
  repoUrl?: string;
  defaultBranch?: string;
}

export const SetupGuide: React.FC<SetupGuideProps> = ({ steps, repoUrl, defaultBranch }) => {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const copyToClipboard = (cmd: string, index: number) => {
    navigator.clipboard.writeText(cmd);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  return (
    <div className="glass-panel rounded-2xl p-6 mb-8 border border-slate-800 shadow-lg">
      <div className="flex items-center gap-2.5 text-cyan-400 font-semibold mb-6">
        <Wrench className="w-5 h-5 text-cyan-400" />
        <h2 className="text-lg text-white">Local Setup Instructions</h2>
      </div>

      <div className="space-y-4">
        {steps.map((step, idx) => (
          <div
            key={idx}
            className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 hover:border-slate-700/80 transition-colors"
          >
            <div className="flex items-start gap-3">
              <span className="flex items-center justify-center w-6 h-6 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800 text-xs font-bold shrink-0 mt-0.5">
                {step.step || idx + 1}
              </span>
              <div className="flex-1">
                <p className="text-sm text-slate-200 font-medium leading-relaxed">
                  {step.description}
                </p>

                {step.command && (
                  <div className="mt-3 relative group">
                    <pre className="p-3 pr-12 rounded-lg bg-slate-950 font-mono text-xs sm:text-sm text-cyan-300 border border-slate-850 overflow-x-auto flex items-center">
                      <Terminal className="w-3.5 h-3.5 text-slate-500 mr-2 shrink-0" />
                      <code>{step.command}</code>
                    </pre>
                    <button
                      onClick={() => copyToClipboard(step.command!, idx)}
                      className="absolute right-2.5 top-2.5 p-1.5 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors cursor-pointer border border-slate-700/60"
                      title="Copy command"
                    >
                      {copiedIndex === idx ? (
                        <Check className="w-3.5 h-3.5 text-emerald-400" />
                      ) : (
                        <Copy className="w-3.5 h-3.5" />
                      )}
                    </button>
                  </div>
                )}

                <EvidenceBadge
                  evidence={step.evidence}
                  repoUrl={repoUrl}
                  defaultBranch={defaultBranch}
                />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
