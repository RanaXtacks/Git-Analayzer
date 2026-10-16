import React from 'react';
import { CheckCircle2, AlertTriangle, Layers } from 'lucide-react';

interface PrerequisitesProps {
  prerequisites: string[];
}

export const Prerequisites: React.FC<PrerequisitesProps> = ({ prerequisites }) => {
  return (
    <div className="glass-panel rounded-2xl p-6 mb-8 border border-slate-800 shadow-lg">
      <div className="flex items-center gap-2.5 text-cyan-400 font-semibold mb-4">
        <Layers className="w-5 h-5 text-cyan-400" />
        <h2 className="text-lg text-white">System Prerequisites</h2>
      </div>

      {prerequisites.length === 0 ? (
        <div className="flex items-center gap-2 text-sm text-slate-400 italic">
          <AlertTriangle className="w-4 h-4 text-amber-400" />
          No specific environment prerequisites were explicitly declared in manifests.
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
          {prerequisites.map((prereq, idx) => (
            <div
              key={idx}
              className="flex items-start gap-3 p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition-colors"
            >
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <span className="text-sm text-slate-200 font-medium">{prereq}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
