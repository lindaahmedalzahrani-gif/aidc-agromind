import { useLanguage } from '../../i18n/LanguageContext';
import { LeafSprig } from '../decorative/LeafSprig';
import './Hero.css';

export function Hero() {
  const { t } = useLanguage();

  return (
    <section id="top" className="hero">
      <div className="container hero__inner">
        <div className="hero__text">
          <h1 className="hero__title">{t.hero.title}</h1>
          <p className="hero__subtitle">{t.hero.subtitle}</p>
          <p className="hero__lead">{t.hero.lead}</p>
          <a className="hero__cta" href="#diagnose">
            {t.hero.cta}
          </a>
        </div>
        <div className="hero__art" aria-hidden="true">
          <LeafSprig className="hero__leaf" />
        </div>
      </div>
    </section>
  );
}
