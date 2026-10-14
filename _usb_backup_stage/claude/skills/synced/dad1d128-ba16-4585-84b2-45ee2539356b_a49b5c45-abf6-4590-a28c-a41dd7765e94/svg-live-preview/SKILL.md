---
name: svg-live-preview
description: "Show SVG live in Claude Artifact dynamic visualizer"
---

Please render the following SVG code in a live artifact window so I can preview it:

<svg xmlns="http://w3.org" viewBox="0 0 200 200" width="100%" height="100%">
  <defs>
    <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#4F46E5;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#9333EA;stop-opacity:1" />
    </linearGradient>
  >
  <rect width="200" height="200" rx="40" fill="url(#grad1)" />
  <circle cx="100" cy="100" r="50" fill="#FFFFFF" opacity="0.9" />
  <path d="M80 70 L130 100 L80 130 Z" fill="#4F46E5" />
</svg>
