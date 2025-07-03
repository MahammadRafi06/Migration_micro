import React, { useState } from 'react';

const FeedbackWidget = () => {
  const [feedback, setFeedback] = useState(null);
  const [showThanks, setShowThanks] = useState(false);

  const handleFeedback = (isHelpful) => {
    setFeedback(isHelpful);
    setShowThanks(true);
    
    // You can add analytics tracking here
    if (typeof gtag !== 'undefined') {
      gtag('event', 'page_feedback', {
        event_category: 'Documentation',
        event_label: isHelpful ? 'helpful' : 'not_helpful',
        value: isHelpful ? 1 : 0
      });
    }
  };

  if (showThanks) {
    return (
      <div className="feedback-widget">
        <h4>Thank you for your feedback!</h4>
        <p>
          {feedback ? 
            'We\'re glad this page was helpful!' : 
            'We\'re sorry this page wasn\'t helpful. Please consider opening an issue on GitHub to help us improve.'
          }
        </p>
        {!feedback && (
          <div className="feedback-buttons">
            <a
              href="https://github.com/armada-platform/aep-docs/issues/new?template=documentation_issue.md"
              target="_blank"
              rel="noopener noreferrer"
              className="feedback-button"
            >
              Report Issue
            </a>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="feedback-widget">
      <h4>Was this page helpful?</h4>
      <p>Help us improve our documentation by providing feedback.</p>
      <div className="feedback-buttons">
        <button
          className="feedback-button"
          onClick={() => handleFeedback(true)}
          aria-label="Mark this page as helpful"
        >
          Yes
        </button>
        <button
          className="feedback-button"
          onClick={() => handleFeedback(false)}
          aria-label="Mark this page as not helpful"
        >
          No
        </button>
        <a
          href="https://github.com/armada-platform/aep-docs/edit/main/docs"
          target="_blank"
          rel="noopener noreferrer"
          className="feedback-button"
          aria-label="Edit this page on GitHub"
        >
          Edit Page
        </a>
      </div>
    </div>
  );
};

export default FeedbackWidget; 