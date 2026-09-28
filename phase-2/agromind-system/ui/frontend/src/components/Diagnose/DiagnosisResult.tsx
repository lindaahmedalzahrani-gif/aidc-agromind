import { useLanguage } from '../../i18n/LanguageContext';
import type { DiagnosePanelStatus, DiagnosisResult as DiagnosisResultType } from '../../types';

interface DiagnosisResultProps {
  status: DiagnosePanelStatus;
  result: DiagnosisResultType | null;
  onAskAboutThis: () => void;
  onTryAgain: () => void;
}

export function DiagnosisResult({ status, result, onAskAboutThis, onTryAgain }: DiagnosisResultProps) {
  const { t } = useLanguage();

  if (status === 'success' && result) {
    const healthLabel =
      result.isHealthy === true
        ? t.diagnose.healthy
        : result.isHealthy === false
          ? t.diagnose.notHealthy
          : t.diagnose.healthUnknown;

    return (
      <div className="result-panel result-panel--success" role="status">
        <h3 className="result-panel__title">{t.diagnose.resultTitle}</h3>
        <dl className="result-panel__grid">
          <div>
            <dt>{t.diagnose.crop}</dt>
            <dd>{result.crop ?? '—'}</dd>
          </div>
          <div>
            <dt>{t.diagnose.diseaseOrPest}</dt>
            <dd>{result.disease ?? '—'}</dd>
          </div>
          <div>
            <dt>{t.diagnose.health}</dt>
            <dd>
              <span className={`health-tag health-tag--${result.isHealthy === false ? 'alert' : 'ok'}`}>
                {healthLabel}
              </span>
            </dd>
          </div>
        </dl>
        {result.modelResponse && (
          <div className="result-panel__raw">
            <p className="result-panel__raw-label">{t.diagnose.modelResponse}</p>
            <p className="result-panel__raw-text">{result.modelResponse}</p>
          </div>
        )}
        <button type="button" className="result-panel__ask" onClick={onAskAboutThis}>
          {t.diagnose.askAboutThis}
        </button>
      </div>
    );
  }

  if (status === 'unknown') {
    return (
      <div className="result-panel result-panel--muted" role="status">
        <h3 className="result-panel__title">{t.diagnose.unknownTitle}</h3>
        <p>{t.diagnose.unknownBody}</p>
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div className="result-panel result-panel--clay" role="alert">
        <h3 className="result-panel__title">{t.diagnose.errorTitle}</h3>
        <p>{t.diagnose.errorBody}</p>
        <button type="button" className="result-panel__retry" onClick={onTryAgain}>
          {t.diagnose.tryAgain}
        </button>
      </div>
    );
  }

  if (status === 'invalid') {
    return (
      <div className="result-panel result-panel--clay" role="alert">
        <h3 className="result-panel__title">{t.diagnose.invalidTitle}</h3>
        <p>{t.diagnose.invalidBody}</p>
      </div>
    );
  }

  return null;
}
