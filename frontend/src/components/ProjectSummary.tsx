import React from 'react';
import { Compass, Sparkles, MapPin } from 'lucide-react';

interface ProjectSummaryProps {
  summary: string;
  whereToStart: string;
}

export const ProjectSummary: React.FC<ProjectSummaryProps> = ({ summary, whereToStart }) => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
      {/* Main summary card */}
      <div className="lg:col-span-2 glass-panel rounded-2xl p-6 border border-slate-800 shadow-lg">
        <div className="flex items-center gap-2.5 text-cyan-400 font-semibold mb-3">
          <Compass className="w-5 h-5 text-cyan-400" />
          <h2 className="text-lg text-white">Project Overview</h2>
        </div>
        <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
          {summary}
        </p>
      </div>

      {/* Where to start card */}
      <div className="glass-panel rounded-2xl p-6 border border-purple-900/40 bg-purple-950/20 shadow-lg relative overflow-hidden">
        <div className="flex items-center gap-2.5 text-purple-300 font-semibold mb-3">
          <MapPin className="w-5 h-5 text-purple-400" />
          <h2 className="text-lg text-white">Where to Start</h2>
        </div>
        <p className="text-slate-200 text-sm leading-relaxed font-medium">
          {whereToStart}
        </p>
        <div className="mt-4 flex items-center gap-2 text-xs text-purple-300/80 font-mono">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Recommended entry point for newcomers</span>
        </div>
      </div>
    </div>
  );
};
