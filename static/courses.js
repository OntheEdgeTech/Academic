
// Course search functionality
document.addEventListener('DOMContentLoaded', function () {
    const courseSearch = document.getElementById('courseSearch');
    const courseCards = document.querySelectorAll('.course-card');
    const resultsContainer = document.getElementById('courseSearchResults');

    if (courseSearch && courseCards.length > 0 && resultsContainer) {
        let searchTimeout;

        courseSearch.addEventListener('input', function () {
            clearTimeout(searchTimeout);
            const searchTerm = this.value.toLowerCase();

            if (searchTerm.length > 2) {
                // Show loading spinner
                resultsContainer.innerHTML = `
                            <div class="search-result-item">
                                <div class="loading-spinner" style="margin: 10px auto;"></div>
                            </div>
                        `;
                resultsContainer.style.display = 'block';

                // Debounce search requests
                searchTimeout = setTimeout(() => {
                    // Search across all documents
                    fetch(`/api/search?q=${encodeURIComponent(searchTerm)}`)
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
                // Hide search results
                resultsContainer.style.display = 'none';

                // Filter courses by name/description
                courseCards.forEach(card => {
                    const courseName = card.getAttribute('data-course').toLowerCase();
                    const courseDescription = card.querySelector('p').textContent.toLowerCase();

                    if (courseName.includes(searchTerm) || courseDescription.includes(searchTerm)) {
                        card.style.display = '';
                    } else {
                        card.style.display = 'none';
                    }
                });
            }
        });

        // Hide search results when clicking outside
        document.addEventListener('click', function (e) {
            if (courseSearch && resultsContainer &&
                !courseSearch.contains(e.target) && !resultsContainer.contains(e.target)) {
                resultsContainer.style.display = 'none';
            }
        });
    }

    // Top bar search functionality
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('topSearchResults');

    if (searchInput && searchResults) {
        let searchTimeout;

        searchInput.addEventListener('input', function () {
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
            if (searchInput && searchResults &&
                !searchInput.contains(e.target) && !searchResults.contains(e.target)) {
                searchResults.style.display = 'none';
            }
        });
    }
});
