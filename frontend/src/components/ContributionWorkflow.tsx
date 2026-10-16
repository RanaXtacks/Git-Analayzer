import React from 'react';
import { GitPullRequest, ArrowRight } from 'lucide-react';

interface ContributionWorkflowProps {
  workflow: string[];
}

export const ContributionWorkflow: React.FC<ContributionWorkflowProps> = ({ workflow }) => {
  return (
    <div className="glass-panel rounded-2xl p-6 mb-8 border border-slate-800 shadow-lg">
      <div className="flex items-center gap-2.5 text-purple-400 font-semibold mb-6">
        <GitPullRequest className="w-5 h-5 text-purple-400" />
        <h2 className="text-lg text-white">Contribution Workflow</h2>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 relative">
        {workflow.map((item, idx) => (
          <div
            key={idx}
            className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col justify-between"
          >
            <div>
              <span className="flex items-center justify-center w-6 h-6 rounded-full bg-purple-950 text-purple-400 border border-purple-800 text-xs font-bold mb-3">
                {idx + 1}
              </span>
              <p className="text-sm text-slate-200 font-medium leading-relaxed">
                {item}
              </p>
            </div>
            {idx < workflow.length - 1 && (
              <div className="hidden md:flex justify-end mt-2 text-slate-600">
                <ArrowRight className="w-4 h-4" />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
