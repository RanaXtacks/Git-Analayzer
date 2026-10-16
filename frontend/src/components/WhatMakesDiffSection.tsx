import React, { useState } from 'react';
import { 
  Sparkles, 
  CheckCircle2, 
  XCircle, 
  ArrowRight,
  Info
} from 'lucide-react';
import type { CopilotDiffPoint } from '../types/guide';

interface WhatMakesDiffSectionProps {
  diffPoints?: CopilotDiffPoint[];
}

const DEFAULT_DIFF_POINTS: CopilotDiffPoint[] = [
  {
    feature: 'Zero-Hallucination Invariant Grounding',
    copilot_approach: 'Relies on probabilistic text completion; frequently hallucinates non-existent npm/pip packages, deprecated CLI flags, or ghost directories.',
    git_analyzer_advantage: 'Every single file, manifest script, entrypoint, and recommended issue is strictly verified against the repository\'s actual Git tree and commit SHA.',
    technical_reason: 'Invariant verification layer inspects raw GitHub tree metadata and purges any unverifiable claims before output generation.'
  },
  {
    feature: 'Local Secret & PII Shield',
    copilot_approach: 'Sends raw editor buffers, prompt history, and environment configuration uninspected to remote cloud servers.',
    git_analyzer_advantage: 'Local high-entropy sanitizer automatically detects, masks, and neutralizes API tokens, AWS secrets, private keys, and passwords before any AI processing.',
    technical_reason: 'Pre-flight entropy and regex scanners redact secrets in-memory, ensuring zero leak risks.'
  },
  {
    feature: 'Algorithmic Issue Difficulty Intelligence',
    copilot_approach: 'Reads issue titles naively without understanding if an issue is realistic for a newcomer or blocked by complex dependencies.',
    git_analyzer_advantage: 'Multi-factor ranking engine evaluates comment heat, label weights, recency, body specificity, and test touchpoints to rank genuine starter issues.',
    technical_reason: 'Calculates normalized 0-100 onboarding scores with explicit Beginner, Intermediate, and Advanced badges.'
  },
  {
    feature: 'Full-Repository Topological Blueprint',
    copilot_approach: 'Limited to the narrow context window of currently active files or short conversational memory, missing whole-repo architecture.',
    git_analyzer_advantage: 'Synthesizes the entire repository tree, manifest graph, CI workflows, and issue tracker into a cohesive architectural lifecycle.',
    technical_reason: 'Holistic context aggregation collects full tree hierarchies, package dependencies, and build pipeline definitions.'
  },
  {
    feature: 'Multi-Track Actionable Roadmaps',
    copilot_approach: 'Produces generic, open-ended conversational advice (e.g. "fork the repo and submit a PR") with no concrete verification checkpoints.',
    git_analyzer_advantage: 'Generates 4 goal-tailored execution plans (Day 1 Contributor, Deep Architecture, Bug Hunter, System Extender) with step-by-step verification assertions.',
    technical_reason: 'Executable plan model binds exact shell commands, target files, and automated test criteria to each step.'
  },
  {
    feature: '100% Self-Hostable Offline Freedom',
    copilot_approach: 'Tied to closed proprietary cloud subscriptions with continuous telemetry and vendor lock-in.',
    git_analyzer_advantage: 'Runs 100% locally with Ollama, vLLM, or deterministic synthesis with zero external API fees and full privacy.',
    technical_reason: 'Pluggable provider architecture with instant fallback to deterministic heuristic synthesis.'
  }
];

export const WhatMakesDiffSection: React.FC<WhatMakesDiffSectionProps> = ({ diffPoints }) => {
  const points = diffPoints && diffPoints.length > 0 ? diffPoints : DEFAULT_DIFF_POINTS;
  const [activeTab, setActiveTab] = useState<'cards' | 'matrix'>('cards');
  const [selectedPointIndex, setSelectedPointIndex] = useState<number>(0);

  return (
    <section className="glass-panel p-6 sm:p-8 rounded-2xl border border-cyan-500/30 bg-gradient-to-br from-slate-900/90 via-slate-900/60 to-cyan-950/20 mb-8 shadow-xl shadow-cyan-950/20 relative overflow-hidden">
      {/* Decorative background glow */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-96 h-96 bg-purple-500/5 rounded-full blur-3xl pointer-events-none" />

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8 pb-6 border-b border-slate-800">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 mb-2.5">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            <span>Competitive Advantage</span>
          </div>
          <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
            <span>What Makes Git-Analyzer Different</span>
            <span className="text-xs px-2 py-0.5 rounded font-mono font-normal bg-slate-800 text-slate-300 border border-slate-700">
              vs GitHub Copilot
            </span>
          </h2>
          <p className="text-sm text-slate-400 mt-1 max-w-2xl">
            GitHub Copilot generates general conversational text from narrow file buffers. Git-Analyzer reconstructs whole-repository ASTs, guarantees zero hallucination, shields credentials, and generates verified execution blueprints.
          </p>
        </div>

        {/* View Switcher */}
        <div className="flex items-center gap-1.5 p-1 bg-slate-950/80 rounded-xl border border-slate-800 self-start md:self-auto">
          <button
            onClick={() => setActiveTab('cards')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
              activeTab === 'cards'
                ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Interactive Cards
          </button>
          <button
            onClick={() => setActiveTab('matrix')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
              activeTab === 'matrix'
                ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Battle Matrix
          </button>
        </div>
      </div>

      {activeTab === 'cards' ? (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: Feature selector buttons */}
          <div className="lg:col-span-5 flex flex-col gap-2.5">
            {points.map((pt, idx) => {
              const isSelected = selectedPointIndex === idx;
              return (
                <button
                  key={idx}
                  onClick={() => setSelectedPointIndex(idx)}
                  className={`text-left p-3.5 rounded-xl border transition-all cursor-pointer flex items-center justify-between ${
                    isSelected
                      ? 'bg-cyan-950/40 border-cyan-500/50 shadow-md shadow-cyan-950/40 translate-x-1'
                      : 'bg-slate-950/40 border-slate-800/80 hover:border-slate-700 hover:bg-slate-900/60'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div
                      className={`w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold ${
                        isSelected
                          ? 'bg-cyan-500 text-slate-950'
                          : 'bg-slate-800 text-slate-400'
                      }`}
                    >
                      {idx + 1}
                    </div>
                    <div>
                      <h4 className={`text-sm font-semibold ${isSelected ? 'text-cyan-300' : 'text-slate-200'}`}>
                        {pt.feature}
                      </h4>
                      <p className="text-[11px] text-slate-400 line-clamp-1">
                        {pt.git_analyzer_advantage}
                      </p>
                    </div>
                  </div>
                  <ArrowRight className={`w-4 h-4 transition-transform ${isSelected ? 'text-cyan-400 translate-x-0.5' : 'text-slate-600'}`} />
                </button>
              );
            })}
          </div>

          {/* Right Column: Detailed Breakdown of Selected Feature */}
          <div className="lg:col-span-7">
            {points[selectedPointIndex] && (
              <div className="bg-slate-950/80 rounded-xl border border-slate-800 p-6 flex flex-col justify-between h-full">
                <div>
                  <div className="flex items-center justify-between gap-3 mb-4">
                    <h3 className="text-lg font-bold text-white">
                      {points[selectedPointIndex].feature}
                    </h3>
                    <span className="text-xs px-2.5 py-0.5 rounded-full font-mono font-medium bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                      Git-Analyzer Core Invariant
                    </span>
                  </div>

                  {/* Contrast Box */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 my-4">
                    {/* Copilot Approach */}
                    <div className="p-4 rounded-xl bg-rose-950/20 border border-rose-500/20">
                      <div className="flex items-center gap-2 mb-2 text-rose-400 text-xs font-bold uppercase tracking-wider">
                        <XCircle className="w-4 h-4 shrink-0" />
                        <span>GitHub Copilot</span>
                      </div>
                      <p className="text-xs text-rose-200/90 leading-relaxed">
                        {points[selectedPointIndex].copilot_approach}
                      </p>
                    </div>

                    {/* Git-Analyzer Advantage */}
                    <div className="p-4 rounded-xl bg-cyan-950/30 border border-cyan-500/30">
                      <div className="flex items-center gap-2 mb-2 text-cyan-400 text-xs font-bold uppercase tracking-wider">
                        <CheckCircle2 className="w-4 h-4 shrink-0" />
                        <span>Git-Analyzer Advantage</span>
                      </div>
                      <p className="text-xs text-cyan-100/90 leading-relaxed">
                        {points[selectedPointIndex].git_analyzer_advantage}
                      </p>
                    </div>
                  </div>

                  {/* Technical Grounding */}
                  <div className="mt-4 p-3.5 rounded-lg bg-slate-900/90 border border-slate-800 text-xs text-slate-300 flex items-start gap-2.5">
                    <Info className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                    <div>
                      <span className="font-semibold text-slate-200">How Git-Analyzer enforces this: </span>
                      <span className="text-slate-400">{points[selectedPointIndex].technical_reason}</span>
                    </div>
                  </div>
                </div>

                <div className="mt-6 pt-4 border-t border-slate-800 flex items-center justify-between text-[11px] text-slate-500">
                  <span>Guaranteed verifiable evidence</span>
                  <span>Feature {selectedPointIndex + 1} of {points.length}</span>
                </div>
              </div>
            )}
          </div>
        </div>
      ) : (
        /* Battle Matrix Table */
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-950/50">
                <th className="py-3 px-4 font-semibold text-slate-300 w-1/4">Capability / Dimension</th>
                <th className="py-3 px-4 font-semibold text-rose-400/90 w-3/8">GitHub Copilot</th>
                <th className="py-3 px-4 font-semibold text-cyan-400 w-3/8">Git-Analyzer</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {points.map((pt, idx) => (
                <tr key={idx} className="hover:bg-slate-900/40 transition-colors">
                  <td className="py-3.5 px-4 font-semibold text-white">
                    <div className="flex items-center gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
                      <span>{pt.feature}</span>
                    </div>
                  </td>
                  <td className="py-3.5 px-4 text-slate-400 leading-relaxed">
                    <span className="text-rose-300 font-mono text-[10px] block mb-0.5">Probabilistic Chat</span>
                    {pt.copilot_approach}
                  </td>
                  <td className="py-3.5 px-4 text-cyan-100/90 leading-relaxed bg-cyan-950/10">
                    <span className="text-cyan-400 font-mono text-[10px] block mb-0.5">AST & Git Grounded</span>
                    {pt.git_analyzer_advantage}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
};
