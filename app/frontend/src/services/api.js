import axios from 'axios';

// Create axios instance with common settings
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor for debugging
api.interceptors.response.use(
  response => {
    console.log(`API Response [${response.config.method.toUpperCase()} ${response.config.url}]:`, response.data);
    return response;
  },
  error => {
    console.error('API Error:', error);
    console.error('Error Response:', error.response?.data);
    console.error('Request Config:', error.config);
    return Promise.reject(error);
  }
);

// API service for content-related operations
export const contentService = {
  // Create a new content source from a URL
  createContentSource: async (name, url, contentType = 'website') => {
    try {
      const response = await api.post('/content/sources', {
        name,
        url,
        content_type: contentType,
        is_active: true
      });
      return response.data;
    } catch (error) {
      console.error('Error creating content source:', error);
      throw error;
    }
  },

  // Ingest content from a source
  ingestContent: async (sourceId) => {
    try {
      const response = await api.post(`/content/sources/${sourceId}/ingest`);
      return response.data;
    } catch (error) {
      console.error(`Error ingesting content for source ${sourceId}:`, error);
      throw error;
    }
  },

  // Get content items for a source
  getContentItems: async (sourceId, skip = 0, limit = 100) => {
    try {
      const response = await api.get('/content/items', {
        params: {
          source_id: sourceId,
          skip,
          limit
        }
      });
      return response.data;
    } catch (error) {
      console.error(`Error getting content items for source ${sourceId}:`, error);
      throw error;
    }
  },

  // Classify a content item
  classifyContent: async (itemId) => {
    try {
      const response = await api.post(`/content/items/${itemId}/classify`);
      return response.data;
    } catch (error) {
      console.error(`Error classifying content item ${itemId}:`, error);
      throw error;
    }
  }
};

// API service for post-related operations
export const postService = {
  // Generate a post from a content item
  generatePost: async (contentItemId, platform = 'linkedin') => {
    try {
      const response = await api.post('/posts/generate', {
        content_item_id: contentItemId,
        platform
      });
      return response.data;
    } catch (error) {
      console.error(`Error generating post for content item ${contentItemId} on ${platform}:`, error);
      throw error;
    }
  },

  // Get all posts with optional filtering
  getPosts: async (status, platform, skip = 0, limit = 100) => {
    try {
      const params = { skip, limit };
      if (status) params.status = status;
      if (platform) params.platform = platform;

      const response = await api.get('/posts', { params });
      return response.data;
    } catch (error) {
      console.error('Error getting posts:', error);
      throw error;
    }
  },

  // Generate an image for a post
  generateImage: async (postId, templateType = 'general') => {
    try {
      const response = await api.post(`/posts/${postId}/generate-image`, null, {
        params: { template_type_str: templateType }
      });
      return response.data;
    } catch (error) {
      console.error(`Error generating image for post ${postId}:`, error);
      throw error;
    }
  },

  // Schedule a post for publication
  schedulePost: async (postId, publishTime) => {
    try {
      const response = await api.post(`/posts/${postId}/schedule`, {
        publish_time: publishTime
      });
      return response.data;
    } catch (error) {
      console.error(`Error scheduling post ${postId}:`, error);
      throw error;
    }
  },

  // Publish a post immediately
  publishPost: async (postId) => {
    try {
      const response = await api.post(`/posts/${postId}/publish`);
      return response.data;
    } catch (error) {
      console.error(`Error publishing post ${postId}:`, error);
      throw error;
    }
  }
};

export default {
  contentService,
  postService
}; 