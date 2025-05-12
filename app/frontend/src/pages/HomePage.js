import React from 'react';
import PostCard from '../components/PostCard';
import LoadingSpinner from '../components/LoadingSpinner';
import ProgressBar from '../components/ProgressBar';
import useContentGeneration from '../hooks/useContentGeneration';

const HomePage = () => {
  const {
    url,
    setUrl,
    loading,
    error,
    contentItems,
    generatedPosts,
    currentStep,
    progress,
    generateContentFromUrl
  } = useContentGeneration();

  const handleUrlSubmit = async (e) => {
    e.preventDefault();
    await generateContentFromUrl(url);
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h1 className="text-2xl font-bold mb-6">Social Media Content Generator</h1>
        
        <form onSubmit={handleUrlSubmit} className="mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="Enter a website URL"
              required
              className="flex-grow px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors disabled:opacity-50"
            >
              {loading ? 'Processing...' : 'Generate Content'}
            </button>
          </div>
        </form>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
            <p>{error}</p>
          </div>
        )}

        {loading && (
          <>
            <ProgressBar progress={progress} currentStep={currentStep} />
            <LoadingSpinner message={
              currentStep === 1 ? "Creating content source..." :
              currentStep === 2 ? "Ingesting content from URL..." :
              currentStep === 3 ? "Processing extracted content..." :
              currentStep === 4 ? "Generating social media posts..." :
              "Processing your URL..."
            } />
          </>
        )}

        {generatedPosts.length > 0 && (
          <div className="mt-8">
            <h2 className="text-xl font-semibold mb-4">Generated Social Media Posts</h2>
            <div className="space-y-6">
              {generatedPosts.map((post, index) => (
                <PostCard key={index} post={post} />
              ))}
            </div>
          </div>
        )}

        {contentItems.length > 0 && generatedPosts.length === 0 && !loading && (
          <div className="mt-8">
            <h2 className="text-xl font-semibold mb-4">Extracted Content</h2>
            <div className="space-y-4">
              {contentItems.map((item) => (
                <div key={item.id} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                  <h3 className="text-lg font-medium mb-2">{item.title || 'Untitled Content'}</h3>
                  <p className="text-gray-600">{item.content}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default HomePage; 