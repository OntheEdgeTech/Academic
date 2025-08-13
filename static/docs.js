(async function(){
  const sidebar = document.getElementById('sidebar');
  const toggle = document.getElementById('sidebarToggle');
  const searchInput = document.getElementById('searchInput');
  const docList = document.getElementById('docList');

  const isMobile = () => window.matchMedia('(max-width: 960px)').matches;
  const setOpen = (open) => {
    if (!sidebar) return;
    sidebar.classList.toggle('open', open);
    toggle?.setAttribute('aria-expanded', String(open));
  };

  // Sidebar init
  setOpen(!isMobile());
  window.addEventListener('resize', () => {
    setOpen(!isMobile());
  });

  toggle?.addEventListener('click', () => setOpen(!sidebar.classList.contains('open')));

  // Keyboard shortcuts
  window.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'b') {
      e.preventDefault(); setOpen(!sidebar.classList.contains('open'));
    }
    if ((e.ctrlKey || e.metaKey) && e.key === '/') {
      e.preventDefault(); searchInput?.focus();
    }
  });

  // Load Fuse.js dynamically (CDN)
  const fuseScript = document.createElement('script');
  fuseScript.src = "https://cdn.jsdelivr.net/npm/fuse.js/dist/fuse.min.js";
  document.head.appendChild(fuseScript);

  fuseScript.onload = () => {
    const items = Array.from(docList?.querySelectorAll('li') || []).map(li => {
      return { text: li.textContent.trim(), element: li };
    });

    const fuse = new Fuse(items, {
      keys: ['text'],
      threshold: 0.4,  // lower = stricter, higher = fuzzier
      includeMatches: true,
    });

    let selectedIndex = -1;

    const renderResults = (query) => {
      items.forEach(({ element }) => element.style.display = 'none');
      if (!query) {
        items.forEach(({ element }) => {
          element.style.display = '';
          element.innerHTML = element.innerHTML; // reset highlighting
        });
        return;
      }

      const results = fuse.search(query);
      results.forEach(({ item, matches }, i) => {
        const el = item.element;
        el.style.display = '';
        
        // Highlight matches
        let highlightedText = item.text;
        matches.forEach(m => {
          m.indices.slice().reverse().forEach(([start, end]) => {
            highlightedText = 
              highlightedText.slice(0, start) + 
              '<mark>' + highlightedText.slice(start, end + 1) + '</mark>' + 
              highlightedText.slice(end + 1);
          });
        });
        el.querySelector('.t').innerHTML = highlightedText;
      });
      selectedIndex = -1;
    };

    searchInput?.addEventListener('input', (e) => {
      renderResults(e.target.value.trim());
    });

    searchInput?.addEventListener('keydown', (e) => {
      const visibleItems = items.filter(({ element }) => element.style.display !== 'none');
      if (!visibleItems.length) return;

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        selectedIndex = (selectedIndex + 1) % visibleItems.length;
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        selectedIndex = (selectedIndex - 1 + visibleItems.length) % visibleItems.length;
      } else if (e.key === 'Enter') {
        e.preventDefault();
        visibleItems[selectedIndex >= 0 ? selectedIndex : 0].element.querySelector('a').click();
      }

      // Highlight active selection
      visibleItems.forEach(({ element }, i) => {
        element.classList.toggle('active-search', i === selectedIndex);
      });
    });
  };
})();
