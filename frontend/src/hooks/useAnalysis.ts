import { useState, useCallback, useRef } from 'react';
import type { AnalysisResponse, ProgressItem, ProgressStage } from '../types/guide';
import type { ProgressCallbackData } from '../services/api';
import { analyzeRepositoryStream } from '../services/api';

const STAGES: { stage: ProgressStage; label: string }[] = [
  { stage: 'metadata', label: 'Repository metadata' },
  { stage: 'readme', label: 'README extraction' },
  { stage: 'contributing', label: 'Contribution guidelines' },
  { stage: 'structure', label: 'Project structure' },
  { stage: 'dependencies', label: 'Dependencies & manifests' },
  { stage: 'configuration', label: 'Configuration & CI workflows' },
  { stage: 'issues', label: 'GitHub issues & ranking' },
  { stage: 'generating', label: 'Generating onboarding guide' },
  { stage: 'validating', label: 'Validating recommendations' },
];

export function useAnalysis() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [stages, setStages] = useState<ProgressItem[]>(
    STAGES.map((s) => ({
      stage: s.stage,
      status: 'pending',
      label: s.label,
    }))
  );
  const [currentDetail, setCurrentDetail] = useState<string>('');

  const abortControllerRef = useRef<AbortController | null>(null);

  const startAnalysis = useCallback((url: string) => {
    setLoading(true);
    setError(null);
    setResult(null);
    setCurrentDetail('Connecting to analyzer...');

    // Reset stages
    setStages(
      STAGES.map((s) => ({
        stage: s.stage,
        status: 'pending',
        label: s.label,
      }))
    );

    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();

    analyzeRepositoryStream(
      url,
      (data: ProgressCallbackData) => {
        const { stage, status, detail } = data;
        if (detail) setCurrentDetail(detail);

        setStages((prev) =>
          prev.map((item) => {
            if (item.stage === stage) {
              return {
                ...item,
                status: status === 'complete' ? 'complete' : status === 'running' ? 'running' : 'pending',
                detail,
              };
            }
            return item;
          })
        );
      },
      (response: AnalysisResponse) => {
        setResult(response);
        setLoading(false);
        setCurrentDetail('Analysis complete!');
        setStages((prev) => prev.map((s) => ({ ...s, status: 'complete' })));
      },
      (errorMessage: string) => {
        setError(errorMessage);
        setLoading(false);
        setCurrentDetail('');
      },
      abortControllerRef.current.signal
    );
  }, []);

  const cancelAnalysis = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setLoading(false);
    setCurrentDetail('Analysis cancelled by user.');
  }, []);

  const reset = useCallback(() => {
    cancelAnalysis();
    setResult(null);
    setError(null);
    setStages(
      STAGES.map((s) => ({
        stage: s.stage,
        status: 'pending',
        label: s.label,
      }))
    );
    setCurrentDetail('');
  }, [cancelAnalysis]);

  return {
    loading,
    error,
    result,
    stages,
    currentDetail,
    startAnalysis,
    cancelAnalysis,
    reset,
  };
}
