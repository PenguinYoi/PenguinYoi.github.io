(() => {
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  if (!reduceMotion.matches && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.04 });
    document.querySelectorAll('.reveal').forEach(element => observer.observe(element));
    document.documentElement.classList.add('motion');
  }
  const bar = document.querySelector('.reading-progress');
  let scheduled = false;
  const update = () => {
    const max = document.documentElement.scrollHeight - window.innerHeight;
    if (bar) bar.style.transform = `scaleX(${max > 0 ? Math.min(1, Math.max(0, window.scrollY / max)) : 0})`;
    scheduled = false;
  };
  window.addEventListener('scroll', () => {
    if (!scheduled) { scheduled = true; window.requestAnimationFrame(update); }
  }, { passive: true });
  window.addEventListener('resize', update);
  update();
})();
