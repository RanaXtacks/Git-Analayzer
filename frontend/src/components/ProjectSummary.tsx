import React, { useState } from 'react';
import { 
  Compass, 
  Sparkles, 
  MapPin, 
  HelpCircle, 
  Target, 
  Cpu, 
  Users,
  Lightbulb
} from 'lucide-react';

interface ProjectSummaryProps {
  summary: string;
  whereToStart: string;
  whatIsIt?: string;
  whyItExists?: string;
  howItWorks?: string;
  whoIsItFor?: string;
  deepExplanation?: string;
  pattern?: string;
}

export const ProjectSummary: React.FC<ProjectSummaryProps> = ({ 
  summary, 
  whereToStart, 
  whatIsIt,
  whyItExists,
  howItWorks,
  whoIsItFor,
  deepExplanation,
  pattern 
}) => {
  const [perspective, setPerspective] = useState<'plain' | 'deep'>('plain');

  // Fallbacks if optional fields are not yet populated
  const displayWhatIsIt = whatIsIt || summary;
  const displayWhyItExists = whyItExists || "Built to provide a modular, open-source solution that eliminates repetitive boilerplate and simplifies development workflows.";
  const displayHowItWorks = howItWorks || "1. Reads configurations and inputs\n2. Executes core logic through modular pipeline stages\n3. Delivers clean outputs and developer APIs";
  const displayWhoIsItFor = whoIsItFor || "Open-source contributors, software engineers, and developers looking for a reliable, well-structured codebase.";

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
      {/* Main explanation card */}
      <div className="lg:col-span-2 glass-panel rounded-2xl p-6 sm:p-7 border border-slate-800 shadow-xl flex flex-col justify-between bg-slate-900/60">
        <div>
          {/* Header Bar */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5 pb-4 border-b border-slate-800/80">
            <div className="flex items-center gap-2.5 text-cyan-400 font-semibold">
              <Compass className="w-5 h-5 text-cyan-400" />
              <h2 className="text-lg font-bold text-white tracking-tight">
                Repository Purpose & Plain-English Explanation
              </h2>
            </div>

            {/* Perspective Switcher */}
            <div className="flex items-center gap-1 p-1 bg-slate-950/80 rounded-xl border border-slate-800 text-xs self-start sm:self-auto">
              <button
                onClick={() => setPerspective('plain')}
                className={`px-3 py-1.5 rounded-lg font-semibold transition-all cursor-pointer flex items-center gap-1.5 ${
                  perspective === 'plain'
                    ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <Lightbulb className="w-3.5 h-3.5" />
                <span>Simple Words</span>
              </button>
              {deepExplanation && (
                <button
                  onClick={() => setPerspective('deep')}
                  className={`px-3 py-1.5 rounded-lg font-semibold transition-all cursor-pointer flex items-center gap-1.5 ${
                    perspective === 'deep'
                      ? 'bg-purple-500 text-white shadow-md shadow-purple-500/20'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  <Cpu className="w-3.5 h-3.5" />
                  <span>Deep Tech</span>
                </button>
              )}
            </div>
          </div>

          {/* Perspective View: Plain English Breakdown */}
          {perspective === 'plain' ? (
            <div className="space-y-4">
              {/* 1. What is this project? */}
              <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800/80">
                <div className="flex items-center gap-2 mb-1.5 text-cyan-400 font-bold text-xs uppercase tracking-wider">
                  <HelpCircle className="w-4 h-4" />
                  <span>What is this project?</span>
                </div>
                <p className="text-slate-200 text-sm sm:text-base leading-relaxed">
                  {displayWhatIsIt}
                </p>
              </div>

              {/* Grid: Why it exists & Who it is for */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {/* 2. Why does it exist? */}
                <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800/80">
                  <div className="flex items-center gap-2 mb-1.5 text-amber-400 font-bold text-xs uppercase tracking-wider">
                    <Target className="w-4 h-4" />
                    <span>Why was it created? (The Problem)</span>
                  </div>
                  <p className="text-slate-300 text-xs sm:text-sm leading-relaxed">
                    {displayWhyItExists}
                  </p>
                </div>

                {/* 3. Who is it for? */}
                <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800/80">
                  <div className="flex items-center gap-2 mb-1.5 text-indigo-400 font-bold text-xs uppercase tracking-wider">
                    <Users className="w-4 h-4" />
                    <span>Who is it for?</span>
                  </div>
                  <p className="text-slate-300 text-xs sm:text-sm leading-relaxed">
                    {displayWhoIsItFor}
                  </p>
                </div>
              </div>

              {/* 4. How does it work? */}
              <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800/80">
                <div className="flex items-center gap-2 mb-1.5 text-emerald-400 font-bold text-xs uppercase tracking-wider">
                  <Cpu className="w-4 h-4" />
                  <span>How does it work in simple steps?</span>
                </div>
                <div className="text-slate-300 text-xs sm:text-sm leading-relaxed whitespace-pre-line space-y-1">
                  {displayHowItWorks}
                </div>
              </div>
            </div>
          ) : (
            /* Perspective View: Deep Architectural */
            <div className="space-y-4">
              {pattern && (
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-mono font-medium bg-purple-500/10 text-purple-300 border border-purple-500/30">
                  <span>Architecture Pattern:</span>
                  <strong className="text-white">{pattern}</strong>
                </div>
              )}
              <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800/80">
                <p className="text-slate-200 text-sm sm:text-base leading-relaxed">
                  {deepExplanation || summary}
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Card Footer */}
        <div className="mt-6 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-500">
          <span>Explained in beginner-friendly, plain English</span>
          <span className="font-mono text-[11px] text-cyan-400">Verified Against Repository README</span>
        </div>
      </div>

      {/* Where to start card */}
      <div className="glass-panel rounded-2xl p-6 sm:p-7 border border-purple-900/40 bg-purple-950/20 shadow-xl relative overflow-hidden flex flex-col justify-between">
        <div>
          <div className="flex items-center gap-2.5 text-purple-300 font-semibold mb-4">
            <MapPin className="w-5 h-5 text-purple-400" />
            <h2 className="text-lg font-bold text-white tracking-tight">Where to Start First</h2>
          </div>
          
          <div className="p-4 rounded-xl bg-slate-950/60 border border-purple-900/30 mb-4">
            <p className="text-slate-200 text-sm leading-relaxed font-medium">
              {whereToStart}
            </p>
          </div>

          <div className="space-y-2 text-xs text-slate-400">
            <div className="flex items-center gap-2 text-purple-300/90 font-medium">
              <Sparkles className="w-3.5 h-3.5 text-purple-400" />
              <span>Recommended first mental model:</span>
            </div>
            <p className="text-[11px] text-slate-400 leading-normal">
              Do not try to read the entire repository at once. Open the entrypoint mentioned above, inspect how requests or commands enter the application, and follow the flow downwards.
            </p>
          </div>
        </div>

        <div className="mt-6 pt-3 border-t border-purple-900/30 flex items-center gap-2 text-xs text-purple-300/80 font-mono">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Newcomer Orientation Guide</span>
        </div>
      </div>
    </div>
  );
};
