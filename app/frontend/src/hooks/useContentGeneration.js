import { useState } from 'react';
import { contentService, postService } from '../services/api';

/**
 * Custom hook for managing content generation flow from URL to social media posts
 */
const useContentGeneration = () => {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [contentSource, setContentSource] = useState(null);
  const [contentItems, setContentItems] = useState([]);
  const [generatedPosts, setGeneratedPosts] = useState([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [progress, setProgress] = useState(0);

  // Reset all state
  const resetState = () => {
    setError(null);
    setContentSource(null);
    setContentItems([]);
    setGeneratedPosts([]);
    setCurrentStep(0);
    setProgress(0);
  };

  // Handle URL submission and content generation
  const generateContentFromUrl = async (submittedUrl) => {
    console.log('Starting content generation for URL:', submittedUrl);
    setLoading(true);
    resetState();
    setUrl(submittedUrl);

    try {
      // Step 1: Create content source (25% progress)
      console.log('Step 1: Creating content source');
      setCurrentStep(1);
      setProgress(25);
      const sourceData = await contentService.createContentSource(
        `Content from ${submittedUrl}`,
        submittedUrl
      );
      console.log('Content source created:', sourceData);
      setContentSource(sourceData);

      // Step 2: Ingest content (50% progress)
      console.log('Step 2: Ingesting content');
      setCurrentStep(2);
      setProgress(50);
      const ingestResult = await contentService.ingestContent(sourceData.id);
      console.log('Content ingestion result:', ingestResult);
      
      // Step 3: Get content items (75% progress)
      console.log('Step 3: Getting content items');
      setCurrentStep(3);
      setProgress(75);
      const items = await contentService.getContentItems(sourceData.id);
      console.log('Content items retrieved:', items);
      setContentItems(items);

      // Step 4: Generate posts if we have content items (100% progress)
      if (items.length > 0) {
        console.log('Step 4: Generating posts');
        setCurrentStep(4);
        
        const contentItemId = items[0].id;
        const platforms = ['linkedin', 'twitter', 'instagram'];
        const posts = [];
        
        // Generate a post for each platform
        for (let i = 0; i < platforms.length; i++) {
          const platform = platforms[i];
          // Update progress for each platform (75-100%)
          setProgress(75 + ((i + 1) / platforms.length) * 25);
          console.log(`Generating post for ${platform}`);
          
          try {
            const post = await postService.generatePost(contentItemId, platform);
            console.log(`${platform} post generated:`, post);
            posts.push(post);
          } catch (platformErr) {
            console.error(`Error generating post for ${platform}:`, platformErr);
          }
        }
        
        setGeneratedPosts(posts);
        setProgress(100);
      } else {
        console.log('No content items found to generate posts');
      }

      return true;
    } catch (err) {
      console.error('Error processing URL:', err);
      console.error('Error details:', err.response?.data);
      setError(err.response?.data?.detail || err.message || 'An error occurred while processing the URL');
      return false;
    } finally {
      setLoading(false);
    }
  };

  return {
    url,
    setUrl,
    loading,
    error,
    contentSource,
    contentItems,
    generatedPosts,
    currentStep,
    progress,
    generateContentFromUrl,
    resetState
  };
};

export default useContentGeneration; 