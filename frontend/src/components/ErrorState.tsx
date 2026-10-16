import React from 'react';
import { AlertCircle, RotateCcw, Home } from 'lucide-react';

interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
  onReset?: () => void;
}

export const ErrorState: React.FC<ErrorStateProps> = ({ message, onRetry, onReset }) => {
  return (
    <div className="glass-panel rounded-2xl p-8 max-w-xl mx-auto my-12 border border-rose-900/40 bg-rose-950/15 text-center shadow-2xl">
      <div className="w-12 h-12 rounded-full bg-rose-950 text-rose-400 border border-rose-800 flex items-center justify-center mx-auto mb-4">
        <AlertCircle className="w-6 h-6" />
      </div>

      <h2 className="text-xl font-bold text-white mb-2">We Couldn't Complete the Analysis</h2>
      <p className="text-sm text-slate-300 leading-relaxed mb-6">
        {message}
      </p>

      <div className="text-left bg-slate-950/60 p-4 rounded-xl border border-slate-850 text-xs text-slate-400 mb-6">
        <span className="font-semibold text-slate-300 block mb-1">Common causes:</span>
        <ul className="list-disc list-inside space-y-1">
          <li>The repository is private or does not exist</li>
          <li>GitHub API rate limit was reached without a token</li>
          <li>Inference server is busy or timed out</li>
          <li>The repository URL is mistyped</li>
        </ul>
      </div>

      <div className="flex items-center justify-center gap-3">
        {onRetry && (
          <button
            onClick={onRetry}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-sm transition-colors cursor-pointer shadow-lg shadow-cyan-600/20"
          >
            <RotateCcw className="w-4 h-4" /> Try Again
          </button>
        )}
        {onReset && (
          <button
            onClick={onReset}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-sm transition-colors cursor-pointer border border-slate-700"
          >
            <Home className="w-4 h-4" /> Back to Home
          </button>
        )}
      </div>
    </div>
  );
};
