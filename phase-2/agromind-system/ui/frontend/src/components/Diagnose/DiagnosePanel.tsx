import { useEffect, useRef, useState } from 'react';
import { useLanguage } from '../../i18n/LanguageContext';
import { ImageDropzone } from './ImageDropzone';
import { DiagnosisResult } from './DiagnosisResult';
import {
  DiagnosisServiceError,
  isImageFileValid,
  requestDiagnosis,
} from '../../services/diagnosisService';
import type { DiagnosePanelStatus, DiagnosisContext, DiagnosisResult as DiagnosisResultType } from '../../types';
import './DiagnosePanel.css';

interface DiagnosePanelProps {
  onDiagnosed: (context: DiagnosisContext) => void;
}

export function DiagnosePanel({ onDiagnosed }: DiagnosePanelProps) {
  const { t, language } = useLanguage();
  const [status, setStatus] = useState<DiagnosePanelStatus>('idle');
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [result, setResult] = useState<DiagnosisResultType | null>(null);
  const objectUrlRef = useRef<string | null>(null);

  useEffect(() => {
    return () => {
      if (objectUrlRef.current) URL.revokeObjectURL(objectUrlRef.current);
    };
  }, []);

  const handleFileSelected = (selected: File) => {
    setResult(null);

    if (!isImageFileValid(selected)) {
      setFile(null);
      if (objectUrlRef.current) {
        URL.revokeObjectURL(objectUrlRef.current);
        objectUrlRef.current = null;
      }
      setPreviewUrl(null);
      setStatus('invalid');
      return;
    }

    if (objectUrlRef.current) URL.revokeObjectURL(objectUrlRef.current);
    const url = URL.createObjectURL(selected);
    objectUrlRef.current = url;

    setFile(selected);
    setPreviewUrl(url);
    setStatus('ready');
  };

  const handleDiagnose = async () => {
    if (!file) return;
    setStatus('analyzing');
    try {
      const diagnosis = await requestDiagnosis({ image: file, language });
      setResult(diagnosis);
      if (!diagnosis.crop && !diagnosis.disease) {
        setStatus('unknown');
      } else {
        setStatus('success');
        onDiagnosed({ crop: diagnosis.crop, disease: diagnosis.disease });
      }
    } catch (err) {
      if (err instanceof DiagnosisServiceError) {
        setStatus('error');
      } else {
        setStatus('error');
      }
    }
  };

  const handleReset = () => {
    if (objectUrlRef.current) {
      URL.revokeObjectURL(objectUrlRef.current);
      objectUrlRef.current = null;
    }
    setFile(null);
    setPreviewUrl(null);
    setResult(null);
    setStatus('idle');
  };

  const scrollToChat = () => {
    document.getElementById('chat')?.scrollIntoView({ behavior: 'smooth' });
  };

  const showPreview = previewUrl && (status === 'ready' || status === 'analyzing' || status === 'success' || status === 'unknown' || status === 'error');

  return (
    <section id="diagnose" className="section diagnose">
      <div className="container">
        <h2 className="diagnose__heading">{t.diagnose.heading}</h2>

        <div className="diagnose__layout">
          <div className="diagnose__upload">
            {showPreview ? (
              <div className="preview">
                <img src={previewUrl} alt="" className="preview__image" />
                <div className="preview__actions">
                  <button type="button" className="preview__change" onClick={handleReset} disabled={status === 'analyzing'}>
                    {t.diagnose.changeImage}
                  </button>
                  {(status === 'ready' || status === 'error') && (
                    <button type="button" className="preview__diagnose" onClick={handleDiagnose}>
                      {t.diagnose.diagnoseButton}
                    </button>
                  )}
                  {status === 'analyzing' && (
                    <span className="preview__analyzing">
                      <span className="preview__spinner" aria-hidden="true" />
                      {t.diagnose.analyzing}
                    </span>
                  )}
                </div>
              </div>
            ) : (
              <ImageDropzone onFileSelected={handleFileSelected} />
            )}

            {status === 'invalid' && (
              <DiagnosisResult status={status} result={null} onAskAboutThis={scrollToChat} onTryAgain={handleReset} />
            )}
          </div>

          <div className="diagnose__result">
            {(status === 'success' || status === 'unknown' || status === 'error') && (
              <DiagnosisResult status={status} result={result} onAskAboutThis={scrollToChat} onTryAgain={handleDiagnose} />
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
