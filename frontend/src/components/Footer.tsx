import React from 'react';

export const Footer = () => {
  return (
    <footer className="mt-12 py-6 bg-gray-800 text-gray-300">
      <div className="container mx-auto px-6 text-center max-w-7xl">
        <p>&copy; {new Date().getFullYear()} Parasha Study Creator</p>
      </div>
    </footer>
  );
};
