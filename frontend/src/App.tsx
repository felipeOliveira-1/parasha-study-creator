import { useState, useEffect } from 'react'
import './App.css'

interface Parasha {
  name: string;
  book: string;
  reference: string;
}

interface Study {
  summary: string;
  themes: string;
  topics: string;
  mussar_analysis?: string;
  references: any[];
  generated_at: string;
}

function App() {
  const [parashot, setParashot] = useState<Parasha[]>([])
  const [selectedParasha, setSelectedParasha] = useState('')
  const [study, setStudy] = useState<Study | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>('')

  useEffect(() => {
    fetchParashot()
  }, [])

  const fetchParashot = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/parashot')
      const data = await response.json()
      if (data.success) {
        setParashot(data.data)
      } else {
        setError('Failed to load parashot list')
      }
    } catch (err) {
      setError('Server connection error')
    }
  }

  // Agrupa as parashiot por livro
  const parashotByBook = parashot.reduce((acc: { [key: string]: Parasha[] }, parasha) => {
    if (!acc[parasha.book]) {
      acc[parasha.book] = [];
    }
    acc[parasha.book].push(parasha);
    return acc;
  }, {});

  // Tradução dos nomes dos livros
  const bookTranslations: { [key: string]: string } = {
    'Genesis': 'Bereshit (Gênesis)',
    'Exodus': 'Shemot (Êxodo)',
    'Leviticus': 'Vayikra (Levítico)',
    'Numbers': 'Bamidbar (Números)',
    'Deuteronomy': 'Devarim (Deuteronômio)'
  };

  const generateStudy = async () => {
    if (!selectedParasha) return

    setLoading(true)
    setError(null)

    try {
      const requestData = {
        parasha: selectedParasha,
        study_type: 'default'
      };
      console.log('Sending request with data:', requestData);

      const response = await fetch('http://localhost:5000/api/studies/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(requestData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to generate study');
      }

      const data = await response.json();
      console.log('Received response:', data);

      if (data.success) {
        setStudy(data.data.content)
        setError(null)
      } else {
        setError(data.error || 'Failed to generate study')
      }
    } catch (error) {
      console.error('Error generating study:', error);
      setError(error instanceof Error ? error.message : 'Failed to generate study')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg">
        <div className="container mx-auto px-6 py-8 max-w-7xl">
          <h1 className="text-4xl font-bold text-center">Parasha Study Creator</h1>
          <p className="mt-3 text-xl text-center text-blue-100">Gere estudos profundos da Torá com IA</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-12 max-w-7xl">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Selection Section */}
          <div className="lg:col-span-4">
            <div className="bg-white rounded-lg shadow-md p-8 sticky top-8">
              <label htmlFor="parasha" className="block text-lg font-semibold text-gray-700 mb-3">
                Selecione uma Parashá
              </label>
              <select
                id="parasha"
                value={selectedParasha}
                onChange={(e) => setSelectedParasha(e.target.value)}
                className="block w-full p-3 text-lg border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200"
              >
                <option value="">Escolha uma parashá...</option>
                {Object.entries(parashotByBook).map(([book, bookParashot]) => (
                  <optgroup key={book} label={bookTranslations[book] || book}>
                    {bookParashot.map((p) => (
                      <option key={p.name} value={p.name}>
                        {p.name}
                      </option>
                    ))}
                  </optgroup>
                ))}
              </select>

              <button
                onClick={generateStudy}
                disabled={!selectedParasha || loading}
                className={`mt-6 w-full px-6 py-3 rounded-lg text-white font-medium text-lg transition-all duration-200 ${
                  !selectedParasha || loading
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-indigo-600 hover:bg-indigo-700 hover:shadow-lg transform hover:-translate-y-0.5'
                }`}
              >
                {loading ? (
                  <div className="flex items-center justify-center">
                    <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      />
                    </svg>
                    Gerando Estudo...
                  </div>
                ) : (
                  'Gerar Estudo'
                )}
              </button>

              {error && (
                <div className="mt-6 bg-red-50 border-l-4 border-red-500 p-4 rounded-r-lg">
                  <div className="flex">
                    <div className="flex-shrink-0">
                      <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="ml-3">
                      <p className="text-red-700">{error}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Study Content */}
          <div className="lg:col-span-8">
            {study && (
              <div className="bg-white rounded-lg shadow-md p-8">
                <h2 className="text-3xl font-bold mb-8 text-gray-800 border-b pb-4">Estudo Gerado</h2>

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
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-12 py-6 bg-gray-800 text-gray-300">
        <div className="container mx-auto px-6 text-center max-w-7xl">
          <p>&copy; {new Date().getFullYear()} Parasha Study Creator</p>
        </div>
      </footer>
    </div>
  )
}

export default App
