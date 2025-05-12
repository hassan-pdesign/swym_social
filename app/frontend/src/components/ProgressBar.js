import React from 'react';

const ProgressBar = ({ progress, steps = [], currentStep = 0 }) => {
  // Default steps if none provided
  const defaultSteps = [
    'Creating source',
    'Ingesting content',
    'Processing content',
    'Generating posts'
  ];
  
  const displaySteps = steps.length > 0 ? steps : defaultSteps;
  
  return (
    <div className="mb-8">
      <div className="w-full bg-gray-200 rounded-full h-2.5 mb-4">
        <div 
          className="bg-primary-600 h-2.5 rounded-full transition-all duration-300 ease-in-out" 
          style={{ width: `${progress}%` }}
        ></div>
      </div>
      
      {displaySteps.length > 0 && (
        <div className="flex justify-between">
          {displaySteps.map((step, index) => (
            <div 
              key={index}
              className={`text-xs ${index === currentStep - 1 
                ? 'text-primary-700 font-semibold' 
                : index < currentStep - 1 
                  ? 'text-primary-500' 
                  : 'text-gray-400'}`}
            >
              {step}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ProgressBar; 