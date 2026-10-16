import React from 'react';
import { CheckCircle2, Loader2, Circle, XCircle } from 'lucide-react';
import { ProgressItem } from '../types/guide';

interface AnalysisProgressProps {
  stages: ProgressItem[];
  currentDetail?: string;
  onCancel?: () => void;
}

export const AnalysisProgress: React.FC<AnalysisProgressProps> = ({
  stages,
  currentDetail,
  onCancel,
}) => {
  const completedCount = stages.filter((s) => s.status === 'complete').length;
  const progressPercent = Math.round((completedCount / stages.length) * 100);

  return (
    <div className="glass-panel rounded-2xl p-6 sm:p-8 max-w-2xl mx-auto my-12 border border-slate-800 shadow-2xl">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <Loader2 className="w-5 h-5 text-cyan-400 animate-spin" />
          Analyzing Repository...
        </h2>
        <span className="text-sm font-bold font-mono text-cyan-400">
          {progressPercent}%
        </span>
      </div>

      {currentDetail && (
        <p className="text-xs sm:text-sm text-cyan-300 font-mono mb-6 bg-slate-950/80 p-2.5 rounded-lg border border-slate-850 truncate">
          &gt; {currentDetail}
        </p>
      )}

      {/* Progress bar */}
      <div className="w-full h-2 bg-slate-800 rounded-full mb-6 overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-cyan-500 via-teal-400 to-purple-500 transition-all duration-300 ease-out"
          style={{ width: `${progressPercent}%` }}
        />
      </div>

      {/* Stage list */}
      <div className="space-y-3">
        {stages.map((stageItem) => {
          const isComplete = stageItem.status === 'complete';
          const isRunning = stageItem.status === 'running';
          const isError = stageItem.status === 'error';

          return (
            <div
              key={stageItem.stage}
              className={`flex items-center justify-between p-2.5 rounded-lg transition-colors text-xs sm:text-sm ${
                isRunning
                  ? 'bg-cyan-950/40 border border-cyan-800/60 text-white'
                  : isComplete
                  ? 'text-slate-300'
                  : 'text-slate-500 opacity-60'
              }`}
            >
              <div className="flex items-center gap-2.5">
                {isComplete ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                ) : isRunning ? (
                  <Loader2 className="w-4 h-4 text-cyan-400 animate-spin shrink-0" />
                ) : isError ? (
                  <XCircle className="w-4 h-4 text-rose-400 shrink-0" />
                ) : (
                  <Circle className="w-4 h-4 text-slate-600 shrink-0" />
                )}
                <span className={isRunning ? 'font-semibold text-cyan-200' : 'font-medium'}>
                  {stageItem.label}
                </span>
              </div>

              {stageItem.detail && isRunning && (
                <span className="text-[11px] text-cyan-400/80 hidden sm:inline font-mono truncate max-w-xs">
                  {stageItem.detail}
                </span>
              )}
            </div>
          );
        })}
      </div>

      {onCancel && (
        <div className="mt-6 text-center">
          <button
            onClick={onCancel}
            className="text-xs text-slate-400 hover:text-rose-400 transition-colors cursor-pointer"
          >
            Cancel Analysis
          </button>
        </div>
      )}
    </div>
  );
};
