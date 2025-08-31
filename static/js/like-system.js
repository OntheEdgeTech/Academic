// Like system functionality
document.addEventListener('DOMContentLoaded', function() {
    console.log('Like system initialized');
    
    // Handle like button clicks
    document.querySelectorAll('.like-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const courseId = this.dataset.courseId;
            const isLiked = this.classList.contains('liked');
            
            if (isLiked) {
                unlikeCourse(courseId, this);
            } else {
                likeCourse(courseId, this);
            }
        });
    });
    
    // Load like counts for all courses on the homepage
    loadLikeCounts();
});

function likeCourse(courseId, button) {
    fetch(`/api/courses/${courseId}/like`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateLikeUI(button, data.likes, true);
        } else {
            console.error('Error liking course:', data.error);
        }
    })
    .catch(error => {
        console.error('Error liking course:', error);
    });
}

function unlikeCourse(courseId, button) {
    fetch(`/api/courses/${courseId}/unlike`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateLikeUI(button, data.likes, false);
        } else {
            console.error('Error unliking course:', data.error);
        }
    })
    .catch(error => {
        console.error('Error unliking course:', error);
    });
}

function updateLikeUI(button, likeCount, isLiked) {
    // Update the button state
    if (isLiked) {
        button.classList.add('liked');
        button.innerHTML = `<i class="bi bi-heart-fill me-1"></i>Unlike`;
    } else {
        button.classList.remove('liked');
        button.innerHTML = `<i class="bi bi-heart me-1"></i>Like`;
    }
    
    // Update the like count display
    const countElements = document.querySelectorAll(`[data-course-id="${button.dataset.courseId}"] .like-count`);
    countElements.forEach(el => {
        el.textContent = likeCount;
    });
}

function loadLikeCounts() {
    // Find all elements that need like counts
    const courseElements = document.querySelectorAll('[data-course-id]');
    if (courseElements.length === 0) {
        return;
    }
    
    const courseIds = Array.from(courseElements).map(el => el.dataset.courseId);
    
    // Get unique course IDs
    const uniqueCourseIds = [...new Set(courseIds)];
    
    // Load like counts for each course
    uniqueCourseIds.forEach(courseId => {
        fetch(`/api/courses/${courseId}/likes`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update all elements for this course
                const countElements = document.querySelectorAll(`[data-course-id="${courseId}"] .like-count`);
                countElements.forEach(el => {
                    el.textContent = data.likes;
                });
                
                // Update button states based on like counts
                const buttons = document.querySelectorAll(`[data-course-id="${courseId}"] .like-btn`);
                buttons.forEach(button => {
                    if (data.likes > 0) {
                        button.classList.add('liked');
                        button.innerHTML = `<i class="bi bi-heart-fill me-1"></i>Unlike`;
                    } else {
                        button.classList.remove('liked');
                        button.innerHTML = `<i class="bi bi-heart me-1"></i>Like`;
                    }
                });
            }
        })
        .catch(error => {
            console.error('Error loading like count for course ' + courseId + ':', error);
        });
    });
}