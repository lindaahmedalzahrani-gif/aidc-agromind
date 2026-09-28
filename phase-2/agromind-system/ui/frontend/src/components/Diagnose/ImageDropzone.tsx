import { useRef, useState } from 'react';
import type { DragEvent } from 'react';
import { useLanguage } from '../../i18n/LanguageContext';

interface ImageDropzoneProps {
  onFileSelected: (file: File) => void;
  disabled?: boolean;
}

export function ImageDropzone({ onFileSelected, disabled }: ImageDropzoneProps) {
  const { t } = useLanguage();
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragActive, setIsDragActive] = useState(false);

  const handleFiles = (files: FileList | null) => {
    if (!files || files.length === 0 || disabled) return;
    onFileSelected(files[0]);
  };

  const handleDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragActive(false);
    handleFiles(event.dataTransfer.files);
  };

  return (
    <div
      className={`dropzone${isDragActive ? ' is-drag-active' : ''}${disabled ? ' is-disabled' : ''}`}
      onDragOver={(e) => {
        e.preventDefault();
        if (!disabled) setIsDragActive(true);
      }}
      onDragLeave={() => setIsDragActive(false)}
      onDrop={handleDrop}
      onClick={() => !disabled && inputRef.current?.click()}
      role="button"
      tabIndex={disabled ? -1 : 0}
      aria-disabled={disabled}
      onKeyDown={(e) => {
        if (!disabled && (e.key === 'Enter' || e.key === ' ')) {
          e.preventDefault();
          inputRef.current?.click();
        }
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png"
        hidden
        onChange={(e) => handleFiles(e.target.files)}
      />
      <div className="dropzone__icon" aria-hidden="true">
        <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
          <path
            d="M20 26V8M20 8l-7 7M20 8l7 7"
            stroke="var(--color-moss)"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <path
            d="M7 26v4a3 3 0 0 0 3 3h20a3 3 0 0 0 3-3v-4"
            stroke="var(--color-moss)"
            strokeWidth="2"
            strokeLinecap="round"
          />
        </svg>
      </div>
      <p className="dropzone__title">{t.diagnose.dropzoneTitle}</p>
      <p className="dropzone__hint">{t.diagnose.dropzoneHint}</p>
      <p className="dropzone__formats">{t.diagnose.dropzoneFormats}</p>
    </div>
  );
}
