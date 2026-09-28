import { useLanguage } from '../../i18n/LanguageContext';
import './Header.css';

export function Header() {
  const { language, setLanguage, t } = useLanguage();

  return (
    <header className="site-header">
      <div className="container site-header__inner">
        <a href="#top" className="site-header__brand">
          {t.nav.brand}
        </a>

        <nav className="site-header__nav" aria-label={t.nav.brand}>
          <a href="#diagnose">{t.nav.diagnose}</a>
          <a href="#chat">{t.nav.chat}</a>
          <a href="#about">{t.nav.about}</a>
        </nav>

        <div className="site-header__lang" role="group" aria-label={t.footer.languageLabel}>
          <button
            type="button"
            className={language === 'en' ? 'is-active' : ''}
            onClick={() => setLanguage('en')}
            aria-pressed={language === 'en'}
          >
            EN
          </button>
          <span aria-hidden="true">·</span>
          <button
            type="button"
            className={language === 'zh' ? 'is-active' : ''}
            onClick={() => setLanguage('zh')}
            aria-pressed={language === 'zh'}
          >
            中文
          </button>
        </div>
      </div>
    </header>
  );
}
