import React, { useState } from 'react';
import TOC from '@theme-original/TOC';

export default function TOCWrapper(props) {
  const [isHidden, setIsHidden] = useState(false);

  const toggleTOC = () => {
    setIsHidden(!isHidden);
    // Apply class to body for CSS styling
    if (!isHidden) {
      document.body.classList.add('toc-hidden');
    } else {
      document.body.classList.remove('toc-hidden');
    }
  };

  return (
    <div style={{ position: 'relative' }}>
      <TOC {...props} />
      {/* Add toggle button similar to left sidebar */}
      <button
        className="toc-toggle-btn"
        onClick={toggleTOC}
        aria-label={isHidden ? 'Show table of contents' : 'Hide table of contents'}
        title={isHidden ? 'Show table of contents' : 'Hide table of contents'}
      >
        {isHidden ? '→' : '←'}
      </button>
    </div>
  );
} 