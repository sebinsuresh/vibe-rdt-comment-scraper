(() => {
  const link = document.querySelector('.thing.link');
  const scoreEl = link.querySelector('.score.unvoted') || link.querySelector('.score');
  return JSON.stringify({
    id: link.getAttribute('data-fullname'),
    title: (link.querySelector('a.title') || { textContent: '' }).textContent,
    author: link.getAttribute('data-author'),
    score: scoreEl ? parseInt(scoreEl.textContent.replace(/[^0-9-]/g, ''), 10) || 0 : 0,
    subreddit: link.getAttribute('data-subreddit-prefixed'),
    body: (document.querySelector('.expando .usertext-body') || { innerText: '' }).innerText.trim(),
    declaredCommentCount: (link.querySelector('.comments') || { textContent: null }).textContent,
  });
})()
