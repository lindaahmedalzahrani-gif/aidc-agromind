import { useLanguage } from '../../i18n/LanguageContext';
import './AboutSection.css';

export function AboutSection() {
  const { t } = useLanguage();

  return (
    <section id="about" className="section about">
      <div className="container about__inner">
        <h2 className="about__heading">{t.about.heading}</h2>
        <p className="about__body">{t.about.body}</p>

        <div className="about__points">
          {t.about.points.map((point) => (
            <div className="about__point" key={point.title}>
              <h3>{point.title}</h3>
              <p>{point.body}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
