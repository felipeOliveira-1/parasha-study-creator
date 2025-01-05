import React from 'react';
import { Study } from '../types';

interface StudySectionProps {
  study: Study;
}

export const StudySection = ({ study }: StudySectionProps) => {
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
                {study.summary}
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
                {study.themes}
              </div>
            </div>
          </div>
        </section>

        {/* Topics Section */}
        <section>
          <h3 className="text-2xl font-semibold mb-4 text-gray-800">Tópicos de Estudo</h3>
          <div className="bg-gray-50 rounded-lg p-6">
            <div className="text-gray-900 leading-relaxed text-justify whitespace-pre-wrap">
              {study.topics
                .replace(/\*\*/g, '')  // Remove marcadores de negrito
                .replace(/###/g, '')   // Remove marcadores de título
              }
            </div>
          </div>
        </section>

        {/* Mussar Analysis Section */}
        {study.mussar_analysis && (
          <section>
            <h3 className="text-2xl font-semibold mb-4 text-gray-800">Análise Mussar</h3>
            <div className="bg-gray-50 rounded-lg p-6">
              <div className="text-gray-900 leading-relaxed text-justify whitespace-pre-wrap">
                {study.mussar_analysis
                  .replace(/\*\*/g, '')  // Remove marcadores de negrito
                  .replace(/###/g, '')   // Remove marcadores de título
                }
              </div>
            </div>
          </section>
        )}
      </div>
    </div>
  );
};
