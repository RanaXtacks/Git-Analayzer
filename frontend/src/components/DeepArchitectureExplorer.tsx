import React, { useState } from 'react';
import { 
  Layers, 
  Workflow, 
  FileCode, 
  ExternalLink, 
  Network, 
  ChevronRight,
  ShieldAlert
} from 'lucide-react';
import type { DeepArchitecture } from '../types/guide';

interface DeepArchitectureExplorerProps {
  architecture?: DeepArchitecture | null;
  repoUrl: string;
  defaultBranch?: string;
}

export const DeepArchitectureExplorer: React.FC<DeepArchitectureExplorerProps> = ({
  architecture,
  repoUrl,
  defaultBranch = 'main'
}) => {
  const [selectedStageIndex, setSelectedStageIndex] = useState<number>(0);

  if (!architecture) {
    return null;
  }

  const { pattern, explanation, lifecycle_stages, data_flow_summary, hotspots_and_gotchas } = architecture;
  const activeStage = lifecycle_stages[selectedStageIndex] || lifecycle_stages[0];

  return (
    <section className="glass-panel p-6 sm:p-8 rounded-2xl border border-slate-800 mb-8 bg-slate-900/50">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 mb-2">
            <Workflow className="w-3.5 h-3.5" />
            <span>Under The Hood</span>
          </div>
          <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
            <span>Deep Architectural Blueprint</span>
          </h2>
          <p className="text-sm text-slate-400 mt-0.5">
            Execution lifecycles, data flows, and subsystem boundaries reconstructed from the repository tree.
          </p>
        </div>

        {/* Pattern Badge */}
        <div className="self-start sm:self-auto px-3.5 py-1.5 rounded-xl bg-cyan-950/40 border border-cyan-500/30 text-cyan-300 text-xs font-semibold flex items-center gap-2">
          <Layers className="w-4 h-4 text-cyan-400" />
          <span>{pattern}</span>
        </div>
      </div>

      {/* Narrative Explanation */}
      <div className="p-4 sm:p-5 rounded-xl bg-slate-950/70 border border-slate-800 text-xs sm:text-sm text-slate-300 leading-relaxed mb-6">
        {explanation}
      </div>

      {/* Visual Interactive Lifecycle Pipeline */}
      {lifecycle_stages && lifecycle_stages.length > 0 && (
        <div className="mb-6">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
            <Network className="w-4 h-4 text-cyan-400" />
            <span>Interactive Request & Execution Lifecycle Pipeline</span>
          </h3>

          {/* Stepper Bar */}
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 mb-4">
            {lifecycle_stages.map((st, idx) => {
              const isSelected = selectedStageIndex === idx;
              return (
                <button
                  key={idx}
                  onClick={() => setSelectedStageIndex(idx)}
                  className={`p-3 rounded-xl border text-left transition-all cursor-pointer flex flex-col justify-between ${
                    isSelected
                      ? 'bg-cyan-500 text-slate-950 border-cyan-400 shadow-lg shadow-cyan-500/20'
                      : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:text-white hover:bg-slate-900/80 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between text-[11px] font-bold opacity-80 mb-1">
                    <span>STAGE {st.stage}</span>
                    <ChevronRight className={`w-3.5 h-3.5 ${isSelected ? 'text-slate-950' : 'text-slate-600'}`} />
                  </div>
                  <span className={`text-xs font-semibold leading-tight line-clamp-2 ${isSelected ? 'text-slate-950 font-bold' : 'text-slate-200'}`}>
                    {st.name}
                  </span>
                </button>
              );
            })}
          </div>

          {/* Active Stage Detailed Panel */}
          {activeStage && (
            <div className="p-5 rounded-xl bg-slate-950/90 border border-cyan-500/20 flex flex-col gap-3">
              <div className="flex items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded-md bg-cyan-500/20 text-cyan-300 text-xs font-bold flex items-center justify-center">
                    {activeStage.stage}
                  </div>
                  <h4 className="text-sm font-bold text-white">
                    {activeStage.name}
                  </h4>
                </div>
                <span className="text-[11px] text-slate-500 font-mono">
                  Stage {activeStage.stage} of {lifecycle_stages.length}
                </span>
              </div>

              <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
                {activeStage.description}
              </p>

              {/* Representative Files */}
              {activeStage.representative_files && activeStage.representative_files.length > 0 && (
                <div className="pt-2 flex flex-wrap items-center gap-2 text-xs">
                  <span className="text-slate-400 font-medium">Representative Code:</span>
                  {activeStage.representative_files.map((file, fIdx) => (
                    <a
                      key={fIdx}
                      href={`${repoUrl}/blob/${defaultBranch}/${file}`}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center gap-1 px-2.5 py-1 rounded font-mono text-[11px] bg-slate-900 hover:bg-slate-800 text-cyan-300 border border-slate-800 transition-colors cursor-pointer"
                    >
                      <FileCode className="w-3 h-3 text-cyan-400" />
                      <span>{file}</span>
                      <ExternalLink className="w-3 h-3 text-slate-500" />
                    </a>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Data Flow Summary */}
      {data_flow_summary && (
        <div className="mb-6 p-4 rounded-xl bg-cyan-950/10 border border-cyan-500/20 text-xs sm:text-sm text-cyan-100/90 leading-relaxed">
          <strong className="text-cyan-400 font-semibold block mb-1">Data Flow & State Propagation:</strong>
          {data_flow_summary}
        </div>
      )}

      {/* Hotspots & Gotchas */}
      {hotspots_and_gotchas && hotspots_and_gotchas.length > 0 && (
        <div className="p-4 sm:p-5 rounded-xl bg-amber-950/20 border border-amber-500/20">
          <h4 className="text-xs font-bold text-amber-400 uppercase tracking-wider mb-2.5 flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-amber-400" />
            <span>Critical Hotspots, Invariants & Architectural Gotchas</span>
          </h4>
          <div className="space-y-2">
            {hotspots_and_gotchas.map((gotcha, gIdx) => (
              <div key={gIdx} className="flex items-start gap-2.5 text-xs text-amber-200/90 leading-relaxed">
                <span className="text-amber-400 font-bold">•</span>
                <span>{gotcha}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
};
