import React from 'react';
import { Study } from '../types';

interface StudySectionProps {
  study: Study;
}

export const StudySection = React.memo(({ study }: StudySectionProps) => {
  // Verificação de segurança
  if (!study || typeof study !== 'object') {
    return <div>Dados de estudo inválidos</div>;
  }

  // Função para processar o conteúdo
  const processContent = (content: string | undefined) => {
    if (!content) return '';
    return content
      .replace(/\*\*/g, '')
      .replace(/###/g, '')
      .trim();
  };
  return (
    <div className="bg-white rounded-lg shadow-md p-8">
      <h2 className="text-3xl font-bold mb-8 text-gray-800 border-b pb-4">
        Estudo Gerado
      </h2>

      <div className="space-y-8">
        {/* Summary Section */}
        <section>
          <h3 className="text-2xl font-semibold mb-4 text-gray-800">Resumo</h3>
          <div className="bg-gray-50 rounded-lg p-6">
            <div className="prose prose-lg max-w-none">
              <div className="text-gray-900 leading-relaxed text-justify">
                {processContent(study.summary)}
              </div>
            </div>
          </div>
        </section>

        {/* Themes Section */}
        <section>
          <h3 className="text-2xl font-semibold mb-4 text-gray-800">Temas Principais</h3>
          <div className="bg-gray-50 rounded-lg p-6">
            <div className="prose prose-lg max-w-none">
              <div className="text-gray-900 leading-relaxed text-justify">
                {processContent(study.themes)}
              </div>
            </div>
          </div>
        </section>

        {/* Topics Section */}
        <section>
          <h3 className="text-2xl font-semibold mb-4 text-gray-800">Tópicos de Estudo</h3>
          <div className="bg-gray-50 rounded-lg p-6">
            <div className="text-gray-900 leading-relaxed text-justify whitespace-pre-wrap">
              {processContent(study.topics)}
            </div>
          </div>
        </section>

        {/* Mussar Analysis Section */}
        {study.mussar_analysis && (
          <section>
            <h3 className="text-2xl font-semibold mb-4 text-gray-800">Análise Mussar</h3>
            <div className="bg-gray-50 rounded-lg p-6">
              <div className="text-gray-900 leading-relaxed text-justify whitespace-pre-wrap">
                {processContent(study.mussar_analysis)}
              </div>
            </div>
          </section>
        )}
      </div>
    </div>
  );
});

StudySection.displayName = 'StudySection';
