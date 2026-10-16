import React from 'react';
import { AlertTriangle } from 'lucide-react';

interface WarningPanelProps {
  warnings: string[];
}

export const WarningPanel: React.FC<WarningPanelProps> = ({ warnings }) => {
  if (!warnings || warnings.length === 0) return null;

  return (
    <div className="glass-panel rounded-2xl p-6 mb-8 border border-amber-900/40 bg-amber-950/10 shadow-lg">
      <div className="flex items-center gap-2.5 text-amber-400 font-semibold mb-3">
        <AlertTriangle className="w-5 h-5 text-amber-400" />
        <h2 className="text-lg text-white">Repository Observations & Uncertainties</h2>
      </div>

      <p className="text-xs text-slate-400 mb-3">
        The following areas could not be conclusively verified from available repository evidence or were sanitized:
      </p>

      <ul className="space-y-1.5 list-disc list-inside text-sm text-amber-200/90">
        {warnings.map((warning, idx) => (
          <li key={idx} className="leading-relaxed">
            {warning}
          </li>
        ))}
      </ul>
    </div>
  );
};
