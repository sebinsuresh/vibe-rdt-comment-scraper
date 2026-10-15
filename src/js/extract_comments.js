(() => {
  const comments = [];
  const elements = Array.from(document.querySelectorAll('.commentarea .comment'));

  // Deleted/removed comments have data-fullname=null, and their bylink can point at
  // an unrelated comment's permalink, so the slug is not a safe id. Synthesize ids
  // that cannot collide with real t1_<base36> fullnames.
  const idByElement = new Map();
  elements.forEach((el, index) => {
    idByElement.set(el, el.getAttribute('data-fullname') || `t1_missing_${index}`);
  });

  for (const el of elements) {
    const parentEl = el.parentElement.closest('.comment');
    const scoreEl = el.querySelector('.score.unvoted') || el.querySelector('.score');
    comments.push({
      id: idByElement.get(el),
      parent: parentEl ? idByElement.get(parentEl) : null,
      author: el.getAttribute('data-author') || '[deleted]',
      score: scoreEl ? parseInt(scoreEl.textContent.replace(/[^0-9-]/g, ''), 10) || 0 : 0,
      body: (el.querySelector('.usertext-body') || { innerText: '' }).innerText.trim(),
      permalink: (el.querySelector('a.bylink') || { getAttribute: () => null }).getAttribute('href'),
    });
  }
  return JSON.stringify(comments);
})()
