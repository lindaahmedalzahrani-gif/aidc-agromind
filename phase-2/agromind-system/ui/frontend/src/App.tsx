import { useState } from 'react';
import { Header } from './components/Header/Header';
import { Hero } from './components/Hero/Hero';
import { DiagnosePanel } from './components/Diagnose/DiagnosePanel';
import { ChatPanel } from './components/Chat/ChatPanel';
import { AboutSection } from './components/About/AboutSection';
import { Footer } from './components/Footer/Footer';
import type { DiagnosisContext } from './types';

export default function App() {
  // Lifted here so a completed diagnosis can be passed as context into the
  // chat panel, per the brief's requirement that crop/disease automatically
  // carry over into the RAG conversation.
  const [diagnosisContext, setDiagnosisContext] = useState<DiagnosisContext | null>(null);

  return (
    <>
      <Header />
      <main>
        <Hero />
        <DiagnosePanel onDiagnosed={setDiagnosisContext} />
        <ChatPanel context={diagnosisContext} />
        <AboutSection />
      </main>
      <Footer />
    </>
  );
}
