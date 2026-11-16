// Copyright (c) 2026 CoreStory, Inc.
// SPDX-License-Identifier: Apache-2.0
// No remote resource is created until the native button is activated.
(() => {
  'use strict';
  const panel = document.querySelector('[data-explainer-video]');
  if (!panel) return;
  const button = panel.querySelector('[data-video-load]');
  const stage = panel.querySelector('[data-video-stage]');
  const status = panel.querySelector('[data-video-status]');
  if (!button || !stage || !status) return;
  let activated = false;
  button.addEventListener('click', () => {
    if (activated) return;
    try {
      const frame = document.createElement('iframe');
      frame.setAttribute('title', 'Tell the CoreStory of your system - Ontologies Explainer');
      // YouTube requires a referring origin; do not change the page-wide policy.
      frame.setAttribute('referrerpolicy', 'strict-origin-when-cross-origin');
      frame.setAttribute('allow', 'encrypted-media; picture-in-picture; fullscreen');
      frame.setAttribute('allowfullscreen', '');
      frame.setAttribute('src', 'https://www.youtube-nocookie.com/embed/gQVNWIBSrEY?autoplay=0');
      stage.replaceChildren(frame);
      activated = true;
      status.textContent = 'YouTube player requested. If it does not appear or play, use the YouTube link below.';
      frame.focus();
    } catch (_) {
      status.textContent = 'The player could not be loaded. Use the YouTube link below.';
    }
  });
  button.hidden = false;
})();
