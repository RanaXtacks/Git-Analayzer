import React, { useState } from 'react';
import { 
  Rocket, 
  Layers, 
  Bug, 
  GitPullRequest, 
  Clock, 
  CheckCircle2, 
  ExternalLink, 
  Copy, 
  Check, 
  Lightbulb, 
  Terminal,
  Target
} from 'lucide-react';
import type { ExecutionPlan } from '../types/guide';

interface ExecutionPlansProps {
  plans?: ExecutionPlan[];
  repoUrl: string;
  defaultBranch?: string;
}

export const ExecutionPlans: React.FC<ExecutionPlansProps> = ({ 
  plans = [], 
  repoUrl, 
  defaultBranch = 'main' 
}) => {
  const [selectedPlanId, setSelectedPlanId] = useState<string>(
    plans.length > 0 ? plans[0].id : 'day_one'
  );
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  if (!plans || plans.length === 0) {
    return null;
  }

  const activePlan = plans.find((p) => p.id === selectedPlanId) || plans[0];

  const handleCopy = (command: string, idx: number) => {
    navigator.clipboard.writeText(command);
    setCopiedIndex(idx);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const getPlanIcon = (id: string) => {
    switch (id) {
      case 'day_one':
        return <Rocket className="w-4 h-4 text-cyan-400" />;
      case 'deep_architecture':
        return <Layers className="w-4 h-4 text-purple-400" />;
      case 'bug_hunt':
        return <Bug className="w-4 h-4 text-emerald-400" />;
      case 'system_extender':
        return <GitPullRequest className="w-4 h-4 text-amber-400" />;
      default:
        return <Target className="w-4 h-4 text-cyan-400" />;
    }
  };

  const getDifficultyBadge = (difficulty: string) => {
    const diff = difficulty.toLowerCase();
    if (diff.includes('beginner')) {
      return (
        <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
          Beginner Friendly
        </span>
      );
    }
    if (diff.includes('intermediate')) {
      return (
        <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
          Intermediate
        </span>
      );
    }
    return (
      <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-purple-500/10 text-purple-400 border border-purple-500/20">
        Advanced
      </span>
    );
  };

  return (
    <section className="glass-panel p-6 sm:p-8 rounded-2xl border border-slate-800 mb-8 bg-slate-900/50">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-purple-500/10 text-purple-400 border border-purple-500/20 mb-2">
            <Target className="w-3.5 h-3.5" />
            <span>Targeted Execution Roadmaps</span>
          </div>
          <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
            Adjustable Action Plans
          </h2>
          <p className="text-sm text-slate-400 mt-0.5">
            Choose your objective: from a 30-minute first PR to deep architectural tracing or bug triage.
          </p>
        </div>

        {/* Plan Switcher Pills */}
        <div className="flex flex-wrap gap-2 p-1.5 bg-slate-950/80 rounded-xl border border-slate-800 self-start md:self-auto">
          {plans.map((p) => {
            const isSelected = p.id === activePlan.id;
            return (
              <button
                key={p.id}
                onClick={() => setSelectedPlanId(p.id)}
                className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                  isSelected
                    ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20'
                    : 'text-slate-400 hover:text-white hover:bg-slate-900'
                }`}
              >
                {getPlanIcon(p.id)}
                <span>{p.title.split(' ')[0]} {p.title.split(' ')[1] || ''}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Active Plan Detail Box */}
      <div className="p-5 sm:p-6 rounded-xl bg-slate-950/70 border border-slate-800/90 mb-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-800/70">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center">
              {getPlanIcon(activePlan.id)}
            </div>
            <div>
              <h3 className="text-base sm:text-lg font-bold text-white">
                {activePlan.title}
              </h3>
              <span className="text-xs text-slate-400">
                Persona: <strong className="text-slate-300 font-medium">{activePlan.target_persona}</strong>
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2 self-start sm:self-auto">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono font-medium bg-slate-900 text-slate-300 border border-slate-800">
              <Clock className="w-3.5 h-3.5 text-cyan-400" />
              <span>{activePlan.time_estimate}</span>
            </div>
            {getDifficultyBadge(activePlan.difficulty)}
          </div>
        </div>

        {/* Goal */}
        <div className="py-4 text-xs sm:text-sm text-slate-300 leading-relaxed">
          <strong className="text-cyan-400 font-semibold">Objective: </strong>
          {activePlan.goal}
        </div>

        {/* Key Files Strip */}
        {activePlan.key_files && activePlan.key_files.length > 0 && (
          <div className="pt-2 flex flex-wrap items-center gap-2 text-xs">
            <span className="text-slate-400 font-medium">Key Focus Files:</span>
            {activePlan.key_files.map((file, fIdx) => (
              <a
                key={fIdx}
                href={`${repoUrl}/blob/${defaultBranch}/${file}`}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md font-mono text-[11px] bg-slate-900 hover:bg-slate-800 text-cyan-300 border border-slate-800 transition-colors cursor-pointer"
              >
                <span>{file}</span>
                <ExternalLink className="w-3 h-3 text-slate-500" />
              </a>
            ))}
          </div>
        )}
      </div>

      {/* Step-by-Step Execution Sequence */}
      <div className="space-y-4">
        <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
          Step-by-Step Execution Checklist ({activePlan.steps.length} Steps)
        </h4>

        {activePlan.steps.map((st, idx) => (
          <div 
            key={idx}
            className="p-4 sm:p-5 rounded-xl bg-slate-950/50 border border-slate-800/80 hover:border-slate-700/80 transition-all flex flex-col gap-3"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-start gap-3">
                <div className="w-7 h-7 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 flex items-center justify-center text-xs font-bold shrink-0 mt-0.5">
                  {st.step}
                </div>
                <div>
                  <h5 className="text-sm font-semibold text-white leading-snug">
                    {st.action}
                  </h5>
                  {st.target_files && st.target_files.length > 0 && (
                    <div className="flex flex-wrap items-center gap-1.5 mt-1.5">
                      {st.target_files.map((tf, tfIdx) => (
                        <a
                          key={tfIdx}
                          href={`${repoUrl}/blob/${defaultBranch}/${tf}`}
                          target="_blank"
                          rel="noreferrer"
                          className="text-[11px] font-mono text-cyan-400/90 hover:text-cyan-300 underline decoration-cyan-500/40"
                        >
                          {tf}
                        </a>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Command Box if present */}
            {st.command && (
              <div className="flex items-center justify-between gap-2 p-3 rounded-lg bg-slate-900 border border-slate-800/90 text-xs font-mono text-cyan-300">
                <div className="flex items-center gap-2 overflow-x-auto py-0.5">
                  <Terminal className="w-4 h-4 text-slate-500 shrink-0" />
                  <span className="select-all">{st.command}</span>
                </div>
                <button
                  onClick={() => handleCopy(st.command!, idx)}
                  className="p-1.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors cursor-pointer shrink-0"
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

            {/* Verification Checkpoint */}
            <div className="flex items-center gap-2 text-xs text-slate-400 bg-slate-900/40 p-2.5 rounded-lg border border-slate-800/40">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
              <span>
                <strong className="text-slate-300 font-medium">Verification: </strong>
                {st.verification}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Pro Tips Box */}
      {activePlan.tips && activePlan.tips.length > 0 && (
        <div className="mt-6 p-4 rounded-xl bg-purple-950/20 border border-purple-500/20 text-xs text-purple-200/90 flex items-start gap-3">
          <Lightbulb className="w-4 h-4 text-purple-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <span className="font-bold text-purple-300 block">Pro Tips for this Plan:</span>
            {activePlan.tips.map((tip, tIdx) => (
              <p key={tIdx} className="text-purple-200/80 leading-relaxed">• {tip}</p>
            ))}
          </div>
        </div>
      )}
    </section>
  );
};
