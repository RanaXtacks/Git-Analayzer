import React from 'react';
import { Compass, Sparkles, MapPin } from 'lucide-react';

interface ProjectSummaryProps {
  summary: string;
  whereToStart: string;
  deepExplanation?: string;
  pattern?: string;
}

export const ProjectSummary: React.FC<ProjectSummaryProps> = ({ 
  summary, 
  whereToStart, 
  deepExplanation,
  pattern 
}) => {
  const [perspective, setPerspective] = React.useState<'overview' | 'deep'>('overview');

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
      {/* Main summary card */}
      <div className="lg:col-span-2 glass-panel rounded-2xl p-6 border border-slate-800 shadow-lg flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between gap-3 mb-3">
            <div className="flex items-center gap-2.5 text-cyan-400 font-semibold">
              <Compass className="w-5 h-5 text-cyan-400" />
              <h2 className="text-lg text-white">Project Explanation</h2>
            </div>

            {/* Adjustable Perspective Pills */}
            {deepExplanation && (
              <div className="flex items-center gap-1 p-1 bg-slate-950/80 rounded-lg border border-slate-800 text-xs">
                <button
                  onClick={() => setPerspective('overview')}
                  className={`px-2.5 py-1 rounded font-medium transition-all cursor-pointer ${
                    perspective === 'overview'
                      ? 'bg-cyan-500 text-slate-950 font-bold'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  Overview
                </button>
                <button
                  onClick={() => setPerspective('deep')}
                  className={`px-2.5 py-1 rounded font-medium transition-all cursor-pointer ${
                    perspective === 'deep'
                      ? 'bg-purple-500 text-white font-bold'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  Deep Architecture
                </button>
              </div>
            )}
          </div>

          {perspective === 'overview' ? (
            <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
              {summary}
            </p>
          ) : (
            <div className="space-y-3">
              {pattern && (
                <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-mono font-medium bg-purple-500/10 text-purple-300 border border-purple-500/30">
                  <span>Architecture Pattern:</span>
                  <strong className="text-white">{pattern}</strong>
                </div>
              )}
              <p className="text-slate-200 text-sm sm:text-base leading-relaxed">
                {deepExplanation}
              </p>
            </div>
          )}
        </div>

        <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-500">
          <span>Verified against repository metadata & AST</span>
          <span className="font-mono text-[11px] text-cyan-400">Zero Hallucinations</span>
        </div>
      </div>

      {/* Where to start card */}
      <div className="glass-panel rounded-2xl p-6 border border-purple-900/40 bg-purple-950/20 shadow-lg relative overflow-hidden flex flex-col justify-between">
        <div>
          <div className="flex items-center gap-2.5 text-purple-300 font-semibold mb-3">
            <MapPin className="w-5 h-5 text-purple-400" />
            <h2 className="text-lg text-white">Where to Start</h2>
          </div>
          <p className="text-slate-200 text-sm leading-relaxed font-medium">
            {whereToStart}
          </p>
        </div>
        <div className="mt-4 flex items-center gap-2 text-xs text-purple-300/80 font-mono">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Recommended entry point for newcomers</span>
        </div>
      </div>
    </div>
  );
};
