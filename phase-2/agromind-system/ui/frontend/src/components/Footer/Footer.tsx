import { useLanguage } from '../../i18n/LanguageContext';
import './Footer.css';

export function Footer() {
  const { t } = useLanguage();

  return (
    <footer className="site-footer">
      <div className="container site-footer__inner">
        <svg width="18" height="18" viewBox="0 0 32 32" aria-hidden="true">
          <path
            d="M16 25c-5-1.5-8-5.5-8-11 5 0 8.5 2 10 5 1-4 4-6 8-6.5C25.5 18.5 21.5 24 16 25Z"
            fill="var(--color-sage)"
          />
        </svg>
        <p>{t.footer.note}</p>
      </div>
    </footer>
  );
}
