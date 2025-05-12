import React from 'react';

const LoadingSpinner = ({ message = 'Loading...' }) => {
  return (
    <div className="text-center py-8">
      <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-primary-500 border-t-transparent"></div>
      <p className="mt-2 text-gray-600">{message}</p>
    </div>
  );
};

export default LoadingSpinner; 