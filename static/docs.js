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
  
  // Initialize features when DOM is loaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      initAllFeatures();
    });
  } else {
    initAllFeatures();
  }
})();

// Initialize all features
function initAllFeatures() {
  // Initialize code copy buttons
  initCodeCopyButtons();
  
  // Initialize image lightbox
  initImageLightbox();
  
  // Initialize mobile TOC
  initMobileToc();
  
  // Initialize recently viewed documents
  initRecentlyViewed();
  
  // Initialize global search
  initGlobalSearch();
  
  // Initialize keyboard navigation
  initKeyboardNavigation();
}

// Code copy buttons
function initCodeCopyButtons() {
  const codeBlocks = document.querySelectorAll('pre code');
  codeBlocks.forEach((codeBlock, index) => {
    const pre = codeBlock.parentElement;
    const button = document.createElement('button');
    button.className = 'code-copy-btn';
    button.textContent = 'Copy';
    button.setAttribute('aria-label', 'Copy code to clipboard');
    
    button.addEventListener('click', () => {
      const text = codeBlock.textContent;
      navigator.clipboard.writeText(text).then(() => {
        button.textContent = 'Copied!';
        button.classList.add('copied');
        setTimeout(() => {
          button.textContent = 'Copy';
          button.classList.remove('copied');
        }, 2000);
      });
    });
    
    pre.style.position = 'relative';
    pre.appendChild(button);
  });
}

// Image lightbox
function initImageLightbox() {
  const images = document.querySelectorAll('.doc-content img');
  const lightbox = document.createElement('div');
  lightbox.className = 'lightbox';
  lightbox.innerHTML = `
    <span class="lightbox-close">&times;</span>
    <img class="lightbox-content" src="" alt="">
  `;
  document.body.appendChild(lightbox);
  
  const closeBtn = lightbox.querySelector('.lightbox-close');
  const lightboxImg = lightbox.querySelector('.lightbox-content');
  
  closeBtn.addEventListener('click', () => {
    lightbox.style.display = 'none';
  });
  
  lightbox.addEventListener('click', (e) => {
    if (e.target === lightbox) {
      lightbox.style.display = 'none';
    }
  });
  
  images.forEach(img => {
    img.addEventListener('click', () => {
      lightboxImg.src = img.src;
      lightboxImg.alt = img.alt;
      lightbox.style.display = 'flex';
    });
  });
}

// Mobile TOC
function initMobileToc() {
  // Only on mobile devices
  if (window.innerWidth > 960) return;
  
  const tocContainer = document.getElementById('toc-container');
  if (!tocContainer) return;
  
  // Create mobile TOC toggle button
  const tocToggle = document.createElement('button');
  tocToggle.className = 'mobile-toc-toggle';
  tocToggle.innerHTML = '☰';
  tocToggle.setAttribute('aria-label', 'Toggle table of contents');
  document.body.appendChild(tocToggle);
  
  // Create mobile TOC container
  const mobileToc = document.createElement('div');
  mobileToc.className = 'mobile-toc';
  mobileToc.innerHTML = `
    <div class="label">Table of Contents</div>
    ${tocContainer.innerHTML}
  `;
  document.body.appendChild(mobileToc);
  
  // Toggle mobile TOC
  tocToggle.addEventListener('click', () => {
    mobileToc.classList.toggle('open');
  });
  
  // Close mobile TOC when clicking outside
  document.addEventListener('click', (e) => {
    if (!tocToggle.contains(e.target) && !mobileToc.contains(e.target)) {
      mobileToc.classList.remove('open');
    }
  });
}

// Recently viewed documents
function initRecentlyViewed() {
  // Get current document info
  const course = document.body.dataset.course;
  const activeFile = document.body.dataset.activeFile;
  
  if (course && activeFile) {
    const docInfo = {
      course: course,
      file: activeFile.replace('.md', ''),
      title: document.title,
      url: window.location.href,
      timestamp: new Date().toISOString()
    };
    
    // Get existing recently viewed from localStorage
    let recentlyViewed = JSON.parse(localStorage.getItem('recentlyViewed') || '[]');
    
    // Remove if already exists
    recentlyViewed = recentlyViewed.filter(item => 
      !(item.course === docInfo.course && item.file === docInfo.file)
    );
    
    // Add to beginning
    recentlyViewed.unshift(docInfo);
    
    // Keep only last 10
    recentlyViewed = recentlyViewed.slice(0, 10);
    
    // Save back to localStorage
    localStorage.setItem('recentlyViewed', JSON.stringify(recentlyViewed));
    
    // Display recently viewed (if on a document page)
    displayRecentlyViewed(recentlyViewed);
  }
}

function displayRecentlyViewed(recentlyViewed) {
  // Only show on document pages
  if (!document.body.dataset.course) return;
  
  const contentInner = document.querySelector('.content-inner');
  if (!contentInner) return;
  
  const recentlyViewedContainer = document.createElement('div');
  recentlyViewedContainer.className = 'recently-viewed';
  recentlyViewedContainer.innerHTML = `
    <div class="label">Recently Viewed</div>
    <div class="recently-viewed-list">
      ${recentlyViewed.map(item => 
        `<div class="recently-viewed-item">
          <a href="/docs/${encodeURIComponent(item.course)}/${encodeURIComponent(item.file)}">
            ${item.file} (${item.course})
          </a>
        </div>`
      ).join('')}
    </div>
  `;
  
  contentInner.appendChild(recentlyViewedContainer);
}

// Global search
function initGlobalSearch() {
  const searchInputs = document.querySelectorAll('#searchInput, #heroSearch, #courseSearch');
  
  searchInputs.forEach(searchInput => {
    if (!searchInput) return;
    
    const resultsContainerId = searchInput.id + 'Results';
    const resultsContainer = document.getElementById(resultsContainerId);
    
    if (!resultsContainer) return;
    
    let searchTimeout;
    
    searchInput.addEventListener('input', () => {
      clearTimeout(searchTimeout);
      const query = searchInput.value.trim();
      
      if (query.length > 2) {
        // Show loading spinner
        resultsContainer.innerHTML = `
          <div class="search-result-item">
            <div class="loading-spinner" style="margin: 10px auto;"></div>
          </div>
        `;
        resultsContainer.style.display = 'block';
        
        // Debounce search requests
        searchTimeout = setTimeout(() => {
          fetch(`/api/search?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(results => {
              if (results.length > 0) {
                let html = '';
                results.slice(0, 10).forEach(result => {
                  html += `
                  <div class="search-result-item" onclick="window.location.href='/docs/${encodeURIComponent(result.course)}/${encodeURIComponent(result.document)}'">
                    <div class="search-result-title">${result.document}</div>
                    <div class="search-result-course">${result.course}</div>
                    <div class="search-result-excerpt">${result.excerpt.substring(0, 100)}...</div>
                  </div>
                  `;
                });
                resultsContainer.innerHTML = html;
              } else {
                resultsContainer.innerHTML = '<div class="search-result-item">No results found</div>';
              }
            })
            .catch(() => {
              resultsContainer.innerHTML = '<div class="search-result-item">Error searching</div>';
            });
        }, 300);
      } else {
        resultsContainer.style.display = 'none';
      }
    });
    
    // Hide search results when clicking outside
    document.addEventListener('click', (e) => {
      if (!searchInput.contains(e.target) && !resultsContainer.contains(e.target)) {
        resultsContainer.style.display = 'none';
      }
    });
  });
}

// Keyboard navigation
function initKeyboardNavigation() {
  document.addEventListener('keydown', (e) => {
    // Focus search with Ctrl+/
    if ((e.ctrlKey || e.metaKey) && e.key === '/') {
      e.preventDefault();
      const searchInput = document.getElementById('searchInput') || 
                         document.getElementById('heroSearch') || 
                         document.getElementById('courseSearch');
      if (searchInput) {
        searchInput.focus();
      }
    }
    
    // Toggle sidebar with Ctrl+B
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'b') {
      e.preventDefault();
      const sidebar = document.getElementById('sidebar');
      const toggle = document.getElementById('sidebarToggle');
      if (sidebar && toggle) {
        const isOpen = sidebar.classList.contains('open');
        sidebar.classList.toggle('open', !isOpen);
        toggle.setAttribute('aria-expanded', String(!isOpen));
      }
    }
  });
}

// Toast notifications
function showToast(message, type = 'info') {
  const toastContainer = document.querySelector('.toast-container') || 
    (() => {
      const container = document.createElement('div');
      container.className = 'toast-container';
      document.body.appendChild(container);
      return container;
    })();
  
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  
  let icon = 'ℹ️';
  if (type === 'success') icon = '✅';
  if (type === 'error') icon = '❌';
  
  toast.innerHTML = `
    <span class="toast-icon">${icon}</span>
    <div class="toast-content">${message}</div>
    <button class="toast-close">&times;</button>
  `;
  
  const closeBtn = toast.querySelector('.toast-close');
  closeBtn.addEventListener('click', () => {
    toast.remove();
  });
  
  toastContainer.appendChild(toast);
  
  // Auto remove after 5 seconds
  setTimeout(() => {
    if (toast.parentNode) {
      toast.remove();
    }
  }, 5000);
}

// Export for global use
window.showToast = showToast;