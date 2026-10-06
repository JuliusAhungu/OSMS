document.documentElement.classList.add('js');

const menuButton = document.querySelector('.menu-toggle');
const navigation = document.querySelector('#main-nav');

if (menuButton && navigation) {
  menuButton.addEventListener('click', () => {
    const isOpen = menuButton.getAttribute('aria-expanded') === 'true';
    menuButton.setAttribute('aria-expanded', String(!isOpen));
    navigation.classList.toggle('is-open', !isOpen);
  });

  navigation.addEventListener('click', (event) => {
    if (event.target.closest('a')) {
      menuButton.setAttribute('aria-expanded', 'false');
      navigation.classList.remove('is-open');
    }
  });
}

const revealItems = document.querySelectorAll([
  '.reveal',
  'main > section:not(.hero)',
  '.section-kicker',
  '.intro-grid > *',
  '.value-item',
  '.program-heading',
  '.program-row',
  '.story-photo-wrap',
  '.story-copy',
  '.notices-head',
  '.notice-item',
  '.event-item',
  '.visit-copy',
  '.visit-form',
  '.page-heading',
  '.metric',
  '.dashboard-grid > .desk-panel',
  '.attendance-row',
  '.record-panel',
  '.fees-layout > .desk-panel',
  '.inquiry-card',
  '.login-image',
  '.login-panel',
].join(', '));

revealItems.forEach((item) => {
  item.classList.add('reveal-on-scroll');
  const siblingIndex = Array.prototype.indexOf.call(item.parentElement.children, item);
  item.style.setProperty('--reveal-delay', `${Math.min(siblingIndex, 4) * 85}ms`);
});

if ('IntersectionObserver' in window) {
  const revealObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.14 });

  revealItems.forEach((item) => revealObserver.observe(item));
} else {
  revealItems.forEach((item) => item.classList.add('is-visible'));
}
