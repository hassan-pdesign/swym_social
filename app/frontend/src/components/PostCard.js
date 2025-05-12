import React from 'react';

const PostCard = ({ post }) => {
  // Define platform-specific styling
  const getPlatformStyles = () => {
    switch (post.platform) {
      case 'linkedin':
        return {
          bgColor: 'bg-blue-50',
          borderColor: 'border-blue-200',
          iconClass: 'fab fa-linkedin text-blue-700'
        };
      case 'twitter':
        return {
          bgColor: 'bg-sky-50',
          borderColor: 'border-sky-200',
          iconClass: 'fab fa-twitter text-sky-500'
        };
      case 'instagram':
        return {
          bgColor: 'bg-purple-50',
          borderColor: 'border-purple-200',
          iconClass: 'fab fa-instagram text-purple-600'
        };
      default:
        return {
          bgColor: 'bg-gray-50',
          borderColor: 'border-gray-200',
          iconClass: 'fas fa-share-alt text-gray-600'
        };
    }
  };

  const { bgColor, borderColor, iconClass } = getPlatformStyles();

  return (
    <div className={`border ${borderColor} rounded-lg p-4 ${bgColor} shadow-sm`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center">
          <i className={`${iconClass} mr-2`}></i>
          <h3 className="text-lg font-medium capitalize">{post.platform} Post</h3>
        </div>
        <span className="bg-primary-100 text-primary-800 text-xs px-2 py-1 rounded-full uppercase">
          {post.status}
        </span>
      </div>
      <div className="bg-white border border-gray-200 rounded p-4 whitespace-pre-line">
        {post.text_content}
      </div>
      
      {post.image_path && (
        <div className="mt-3">
          <img 
            src={post.image_path} 
            alt={`${post.platform} post image`}
            className="w-full h-auto rounded-md border border-gray-200"
          />
        </div>
      )}
      
      {post.published_time && (
        <div className="mt-2 text-xs text-gray-500">
          Published: {new Date(post.published_time).toLocaleString()}
        </div>
      )}
    </div>
  );
};

export default PostCard; 