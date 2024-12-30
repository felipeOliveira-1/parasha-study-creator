import React, { useState, useEffect } from 'react';

interface Study {
  parasha: string;
  date: string;
  file_path: string;
}

interface StudyHistoryProps {
  onSelectStudy: (parasha: string) => void;
}

const StudyHistory: React.FC<StudyHistoryProps> = ({ onSelectStudy }) => {
  const [studies, setStudies] = useState<Study[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadRecentStudies();
  }, []);

  const loadRecentStudies = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch('/api/studies/recent');
      const data = await response.json();
      
      if (data.success) {
        setStudies(data.studies);
      } else {
        setError(data.error || 'Erro ao carregar estudos');
      }
    } catch (e) {
      setError('Erro ao conectar com o servidor');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (isoDate: string) => {
    const date = new Date(isoDate);
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-4">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-r-lg">
        <p className="text-red-700">{error}</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-xl font-semibold mb-4 text-gray-800">Estudos Recentes</h3>
      {studies.length === 0 ? (
        <p className="text-gray-600">Nenhum estudo encontrado</p>
      ) : (
        <div className="space-y-2">
          {studies.map((study) => (
            <div
              key={study.file_path}
              className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg cursor-pointer transition-colors"
              onClick={() => onSelectStudy(study.parasha)}
            >
              <div>
                <h4 className="font-medium text-gray-900">Parashá {study.parasha}</h4>
                <p className="text-sm text-gray-600">{formatDate(study.date)}</p>
              </div>
              <button
                className="text-indigo-600 hover:text-indigo-800 text-sm font-medium"
                onClick={(e) => {
                  e.stopPropagation();
                  onSelectStudy(study.parasha);
                }}
              >
                Ver Estudo
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default StudyHistory;
