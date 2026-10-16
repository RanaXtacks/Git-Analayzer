import React, { useState } from 'react';
import { Search, Sparkles, Check, ArrowRight, ShieldCheck, Cpu, Database } from 'lucide-react';

interface LandingPageProps {
  onAnalyze: (url: string) => void;
  isLoading: boolean;
}

const DEMO_REPOSITORIES = [
  'https://github.com/fastapi/fastapi',
  'https://github.com/facebook/react',
  'https://github.com/pallets/flask',
  'https://github.com/expressjs/express',
];

export const LandingPage: React.FC<LandingPageProps> = ({ onAnalyze, isLoading }) => {
  const [urlInput, setUrlInput] = useState('');
  const [validationError, setValidationError] = useState<string | null>(null);

  const validateUrl = (value: string): boolean => {
    if (!value.trim()) {
      setValidationError(null);
      return false;
    }
    const clean = value.trim();
    const githubRegex = /^https?:\/\/(?:www\.)?github\.com\/[a-zA-Z0-9_.-]+\/[a-zA-Z0-9_.-]+(?:\/)?(?:\.git)?$/;
    if (!githubRegex.test(clean)) {
      setValidationError('Please enter a valid GitHub repository URL: https://github.com/owner/repo');
      return false;
    }
    setValidationError(null);
    return true;
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setUrlInput(val);
    validateUrl(val);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateUrl(urlInput)) {
      onAnalyze(urlInput.trim());
    }
  };

  const handleDemoSelect = (demoUrl: string) => {
    setUrlInput(demoUrl);
    setValidationError(null);
    onAnalyze(demoUrl);
  };

  return (
    <div className="min-h-[85vh] flex flex-col justify-center items-center px-4 sm:px-6 relative">
      {/* Background radial gradients */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[400px] bg-cyan-600/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute top-1/3 left-1/3 w-[300px] h-[300px] bg-purple-600/10 rounded-full blur-[100px] pointer-events-none" />

      <div className="relative z-10 max-w-4xl w-full text-center py-12">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-cyan-950/70 border border-cyan-800/60 text-cyan-300 text-xs font-semibold mb-6 shadow-sm">
          <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
          <span>Open Source AI Repository Onboarding Assistant</span>
        </div>

        {/* Hero Title */}
        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white mb-4">
          Git-<span className="text-gradient">Analyzer</span>
        </h1>

        {/* Tagline */}
        <p className="text-xl sm:text-2xl font-semibold text-slate-200 mb-4">
          Find your way into any open-source project.
        </p>

        {/* Description */}
        <p className="text-slate-400 text-base sm:text-lg max-w-2xl mx-auto mb-10 leading-relaxed">
          Enter any public GitHub repository URL and receive an evidence-backed, AI-generated onboarding roadmap for making your very first open-source contribution.
        </p>

        {/* Search / Input Form */}
        <form onSubmit={handleSubmit} className="max-w-2xl mx-auto mb-6">
          <div className="relative flex flex-col sm:flex-row items-center gap-2 p-2 rounded-2xl glass-panel border border-slate-700/80 shadow-2xl focus-within:border-cyan-500/80 transition-colors">
            <div className="relative flex-1 w-full flex items-center pl-3">
              <Search className="w-5 h-5 text-slate-400 shrink-0 mr-2" />
              <input
                type="url"
                value={urlInput}
                onChange={handleInputChange}
                placeholder="https://github.com/owner/repository"
                disabled={isLoading}
                required
                className="w-full bg-transparent text-white placeholder-slate-500 text-sm sm:text-base focus:outline-none py-2"
              />
            </div>
            <button
              type="submit"
              disabled={isLoading || !urlInput.trim() || !!validationError}
              className="w-full sm:w-auto px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 via-teal-500 to-cyan-600 hover:from-cyan-400 hover:to-teal-500 text-slate-950 font-bold text-sm transition-all shadow-lg shadow-cyan-500/25 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer flex items-center justify-center gap-2 shrink-0"
            >
              <span>Analyze Repository</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          {validationError && (
            <p className="text-xs text-rose-400 mt-2 text-left pl-3 font-medium">
              {validationError}
            </p>
          )}
        </form>

        {/* Quick Demo Repositories */}
        <div className="flex flex-wrap items-center justify-center gap-2 mb-14 text-xs text-slate-400">
          <span className="font-semibold text-slate-500 mr-1">Try example:</span>
          {DEMO_REPOSITORIES.map((demo) => {
            const shortName = demo.replace('https://github.com/', '');
            return (
              <button
                key={demo}
                onClick={() => handleDemoSelect(demo)}
                disabled={isLoading}
                className="px-2.5 py-1 rounded-lg bg-slate-900/80 hover:bg-slate-800 text-slate-300 hover:text-cyan-300 border border-slate-800 transition-colors cursor-pointer font-mono"
              >
                {shortName}
              </button>
            );
          })}
        </div>

        {/* Feature Highlights Grid */}
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-left max-w-3xl mx-auto">
          {[
            { title: 'Understand the project', desc: 'Clear, high-level beginner summary.' },
            { title: 'Discover prerequisites', desc: 'Verified runtimes and engines.' },
            { title: 'Find important files', desc: 'Architecture & entry points mapped.' },
            { title: 'Beginner-friendly issues', desc: 'Deterministic newcomer ranking.' },
            { title: 'First contribution roadmap', desc: 'Achievable small task spotlight.' },
            { title: 'Zero hallucinations', desc: 'Every claim backed by repo evidence.' },
          ].map((feat, idx) => (
            <div
              key={idx}
              className="p-3.5 rounded-xl bg-slate-900/40 border border-slate-850 hover:border-slate-800 transition-colors"
            >
              <div className="flex items-center gap-1.5 text-cyan-400 font-semibold text-xs mb-1">
                <Check className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                <span>{feat.title}</span>
              </div>
              <p className="text-slate-400 text-xs leading-relaxed">{feat.desc}</p>
            </div>
          ))}
        </div>

        {/* Open source architecture pill */}
        <div className="mt-14 inline-flex flex-wrap items-center justify-center gap-6 text-xs text-slate-500 font-medium">
          <div className="flex items-center gap-1.5">
            <Cpu className="w-4 h-4 text-cyan-400" />
            <span>Open-weight Qwen3 (Ollama / vLLM)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>No proprietary AI API required</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Database className="w-4 h-4 text-purple-400" />
            <span>Self-hostable via Docker Compose</span>
          </div>
        </div>
      </div>
    </div>
  );
};
