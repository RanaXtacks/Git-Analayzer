import React, { useState } from 'react';
import { Compass, Heart, Code2 } from 'lucide-react';
import { ThemeToggle } from './components/ThemeToggle';
import { LandingPage } from './pages/LandingPage';
import { GuideView } from './pages/GuideView';
import { AnalysisProgress } from './components/AnalysisProgress';
import { ErrorState } from './components/ErrorState';
import { useAnalysis } from './hooks/useAnalysis';

export const App: React.FC = () => {
  const {
    loading,
    error,
    result,
    stages,
    currentDetail,
    startAnalysis,
    cancelAnalysis,
    reset,
  } = useAnalysis();

  const [activeUrl, setActiveUrl] = useState<string>('');

  const handleStartAnalysis = (url: string) => {
    setActiveUrl(url);
    startAnalysis(url);
  };

  const handleRetry = () => {
    if (activeUrl) {
      startAnalysis(activeUrl);
    } else {
      reset();
    }
  };

  return (
    <div className="min-h-screen flex flex-col justify-between">
      {/* Navigation Header */}
      <header className="sticky top-0 z-50 glass-panel border-b border-slate-800/80">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          <div
            onClick={reset}
            className="flex items-center gap-2.5 cursor-pointer group"
          >
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-purple-600 flex items-center justify-center shadow-md shadow-cyan-500/20 group-hover:scale-105 transition-transform">
              <Compass className="w-5 h-5 text-slate-950 stroke-[2.5]" />
            </div>
            <div className="flex flex-col">
              <span className="font-extrabold text-base tracking-tight text-white group-hover:text-cyan-300 transition-colors">
                Git-<span className="text-cyan-400">Analyzer</span>
              </span>
              <span className="text-[10px] text-slate-400 font-medium -mt-1 hidden sm:inline">
                Open-Source Onboarding Assistant
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <ThemeToggle />
            <a
              href="https://github.com"
              target="_blank"
              rel="noreferrer"
              className="p-2 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 text-slate-300 hover:text-white transition-colors border border-slate-700/50 cursor-pointer"
              title="GitHub"
            >
              <Code2 className="w-4 h-4" />
            </a>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1">
        {loading ? (
          <AnalysisProgress
            stages={stages}
            currentDetail={currentDetail}
            onCancel={cancelAnalysis}
          />
        ) : error ? (
          <ErrorState
            message={error}
            onRetry={handleRetry}
            onReset={reset}
          />
        ) : result ? (
          <GuideView data={result} onReset={reset} />
        ) : (
          <LandingPage onAnalyze={handleStartAnalysis} isLoading={loading} />
        )}
      </main>

      {/* Footer */}
      <footer className="glass-panel border-t border-slate-800/80 py-6 mt-12 text-center text-xs text-slate-500">
        <div className="max-w-6xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-1.5">
            <span>Built with</span>
            <Heart className="w-3.5 h-3.5 text-rose-500 fill-rose-500 inline" />
            <span>for the global open-source community.</span>
          </div>

          <div className="flex items-center gap-4 text-slate-400">
            <span>Apache 2.0 License</span>
            <span>•</span>
            <span>Self-Hostable</span>
            <span>•</span>
            <span>Powered by Qwen3</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
