
// Landing page search functionality
document.addEventListener('DOMContentLoaded', function () {
    const heroSearch = document.getElementById('heroSearch');
    const searchResults = document.getElementById('heroSearchResults');

    if (heroSearch && searchResults) {
        let searchTimeout;

        heroSearch.addEventListener('input', function () {
            clearTimeout(searchTimeout);
            const query = this.value.trim();

            if (query.length > 2) {
                // Show loading spinner
                searchResults.innerHTML = `
                            <div class="search-result-item">
                                <div class="loading-spinner" style="margin: 10px auto;"></div>
                            </div>
                        `;
                searchResults.style.display = 'block';

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
                                searchResults.innerHTML = html;
                            } else {
                                searchResults.innerHTML = '<div class="search-result-item">No results found</div>';
                            }
                        })
                        .catch(() => {
                            searchResults.innerHTML = '<div class="search-result-item">Error searching</div>';
                        });
                }, 300);
            } else {
                searchResults.style.display = 'none';
            }
        });

        // Hide search results when clicking outside
        document.addEventListener('click', function (e) {
            if (!heroSearch.contains(e.target) && !searchResults.contains(e.target)) {
                searchResults.style.display = 'none';
            }
        });
    }

    // Simple animation for feature cards on scroll
    const featureCards = document.querySelectorAll('.feature-card');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = 1;
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });

    featureCards.forEach(card => {
        card.style.opacity = 0;
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(card);
    });
});
