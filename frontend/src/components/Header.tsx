import React from 'react';

export const Header = () => {
  return (
    <header className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg">
      <div className="container mx-auto px-6 py-8 max-w-7xl">
        <h1 className="text-4xl font-bold text-center">Parasha Study Creator</h1>
        <p className="mt-3 text-xl text-center text-blue-100">
          Gere estudos profundos da Torá com IA
        </p>
      </div>
    </header>
  );
};
