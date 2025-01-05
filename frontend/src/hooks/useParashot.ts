import { useState, useEffect } from 'react';
import { Parasha } from '../types';

export const useParashot = () => {
  const [parashot, setParashot] = useState<Parasha[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchParashot = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/parashot');
        const data = await response.json();
        if (data.success) {
          setParashot(data.data);
        } else {
          setError('Failed to load parashot list');
        }
      } catch (err) {
        setError('Server connection error');
      }
    };

    fetchParashot();
  }, []);

  return { parashot, error };
};
