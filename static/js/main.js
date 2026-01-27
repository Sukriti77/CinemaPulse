// ===============================================
// CinemaPulse - Interactive JavaScript
// ===============================================

// === LOGIN VALIDATION ===
async function validateLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    
    // Basic validation
    if (!email || !password) {
        showError('Please fill in all fields');
        return false;
    }
    
    // Email format check
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        showError('Please enter a valid email address');
        return false;
    }
    
    // Call backend API for authentication
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Redirect based on role
            if (data.user.role === 'admin') {
                window.location.href = '/admin';
            } else {
                window.location.href = '/dashboard';
            }
        } else {
            showError(data.message || 'Invalid email or password');
        }
    } catch (error) {
        console.error('Login error:', error);
        showError('Login failed. Please try again.');
    }
    
    return false;
}

// === STAR RATING SYSTEM ===
let selectedRating = 0;

function initStarRating() {
    const stars = document.querySelectorAll('.star');
    const ratingInput = document.getElementById('rating');
    
    stars.forEach((star, index) => {
        star.addEventListener('click', () => {
            selectedRating = index + 1;
            ratingInput.value = selectedRating;
            updateStars();
        });
        
        star.addEventListener('mouseenter', () => {
            highlightStars(index + 1);
        });
    });
    
    const starContainer = document.querySelector('.star-rating');
    if (starContainer) {
        starContainer.addEventListener('mouseleave', () => {
            updateStars();
        });
    }
}

function updateStars() {
    const stars = document.querySelectorAll('.star');
    stars.forEach((star, index) => {
        if (index < selectedRating) {
            star.classList.add('active');
        } else {
            star.classList.remove('active');
        }
    });
}

function highlightStars(count) {
    const stars = document.querySelectorAll('.star');
    stars.forEach((star, index) => {
        if (index < count) {
            star.classList.add('active');
        } else {
            star.classList.remove('active');
        }
    });
}

// === FEEDBACK FORM VALIDATION ===
async function validateFeedback(event) {
    event.preventDefault();
    
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const rating = document.getElementById('rating').value;
    const comment = document.getElementById('comment').value;
    const movieId = document.getElementById('movie_id').value;
    
    // Validation
    if (!name || !email || !rating || !comment) {
        alert('Please fill in all fields');
        return false;
    }
    
    if (rating < 1 || rating > 5) {
        alert('Please select a rating');
        return false;
    }
    
    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        alert('Please enter a valid email address');
        return false;
    }
    
    // Call backend API to submit feedback
    try {
        const response = await fetch('/api/feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                movie_id: parseInt(movieId),
                name: name,
                email: email,
                rating: parseInt(rating),
                comment: comment
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Redirect to thank you page
            window.location.href = '/thankyou';
        } else {
            alert(data.error || 'Failed to submit feedback');
        }
    } catch (error) {
        console.error('Feedback submission error:', error);
        alert('Failed to submit feedback. Please try again.');
    }
    
    return false;
}

// === SMOOTH SCROLL ===
function smoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// === ANIMATE ON SCROLL ===
function animateOnScroll() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, {
        threshold: 0.1
    });
    
    document.querySelectorAll('.movie-card, .card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(card);
    });
}

// === INITIALIZE ON PAGE LOAD ===
document.addEventListener('DOMContentLoaded', function() {
    // Initialize star rating if on feedback page
    if (document.querySelector('.star-rating')) {
        initStarRating();
    }
    
    // Initialize smooth scroll
    smoothScroll();
    
    // Initialize animations
    animateOnScroll();
    
    // Add form listeners
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', validateLogin);
    }
    
    const feedbackForm = document.getElementById('feedbackForm');
    if (feedbackForm) {
        feedbackForm.addEventListener('submit', validateFeedback);
    }
    
    // Load dashboard movies if on dashboard page
    if (document.querySelector('.movie-grid')) {
        loadMovies();
        
        // Real-time search on input
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.addEventListener('input', debounce(searchMovies, 500));
        }
    }
    
    // Load movie details if on movie page
    if (window.location.pathname.startsWith('/movie/')) {
        const movieId = window.location.pathname.split('/')[2];
        if (movieId) {
            loadMovieDetails(movieId);
        }
    }
    
    // Load movie title if on feedback page
    if (window.location.pathname.startsWith('/feedback/')) {
        const movieId = window.location.pathname.split('/')[2];
        if (movieId) {
            loadMovieTitleForFeedback(movieId);
        }
    }
    
    // Load analytics if on analytics page
    if (window.location.pathname === '/analytics') {
        loadAnalytics();
    }
});

// === LOAD MOVIES FOR DASHBOARD ===
async function loadMovies() {
    try {
        const response = await fetch('/api/movies');
        const data = await response.json();
        
        if (data.success && data.movies) {
            const movieGrid = document.querySelector('.movie-grid');
            movieGrid.innerHTML = ''; // Clear existing content
            
            data.movies.forEach(movie => {
                const movieCard = createMovieCard(movie);
                movieGrid.appendChild(movieCard);
            });
        }
    } catch (error) {
        console.error('Error loading movies:', error);
    }
}

// === CREATE MOVIE CARD ===
function createMovieCard(movie) {
    const card = document.createElement('div');
    card.className = 'movie-card';
    card.innerHTML = `
        <img src="${movie.poster}" alt="${movie.title}" class="movie-poster">
        <div class="movie-info">
            <h2 class="movie-title">${movie.title}</h2>
            <div class="movie-rating">
                <span class="stars">★★★★★</span>
                <span class="rating-text">${movie.rating}/5</span>
            </div>
            <p class="movie-description">
                ${movie.description.substring(0, 100)}...
            </p>
            <a href="/movie/${movie.id}" class="btn btn-primary">
                View Details
            </a>
        </div>
    `;
    return card;
}

// === LOAD MOVIE DETAILS ===
async function loadMovieDetails(movieId) {
    try {
        const response = await fetch(`/api/movies/${movieId}`);
        const data = await response.json();
        
        if (data.success && data.movie) {
            // Update movie details (if elements exist)
            const movie = data.movie;
            
            // Update page title
            document.title = `${movie.title} - CinemaPulse`;
            
            // Update title
            const titleElement = document.querySelector('.detail-content h1');
            if (titleElement) titleElement.textContent = movie.title;
            
            // Update description
            const descElement = document.querySelector('.movie-description');
            if (descElement) descElement.textContent = movie.description;
            
            // Update rating
            const ratingBadge = document.querySelector('.rating-badge');
            if (ratingBadge) ratingBadge.textContent = `${movie.rating}/5`;
            
            // Update poster
            const posterElement = document.querySelector('.detail-poster');
            if (posterElement) posterElement.src = movie.poster;
            
            // Update feedback link
            const feedbackLink = document.getElementById('feedback-link');
            if (feedbackLink) feedbackLink.href = `/feedback/${movieId}`;
            
            // Load reviews
            loadReviews(movie.reviews);
        }
    } catch (error) {
        console.error('Error loading movie details:', error);
    }
}

// === LOAD REVIEWS ===
function loadReviews(reviews) {
    const reviewsSection = document.querySelector('.reviews-section');
    if (!reviewsSection) return;
    
    // Clear existing reviews except header
    const existingReviews = reviewsSection.querySelectorAll('.review-card');
    existingReviews.forEach(review => review.remove());
    
    // Add new reviews
    reviews.forEach(review => {
        const reviewCard = document.createElement('div');
        reviewCard.className = 'review-card';
        reviewCard.innerHTML = `
            <div class="review-header">
                <span class="reviewer-name">${review.name}</span>
                <span class="stars">${'★'.repeat(review.rating)}${'☆'.repeat(5 - review.rating)}</span>
            </div>
            <p style="color: var(--text-gray); margin-top: 0.5rem;">${review.comment}</p>
        `;
        reviewsSection.appendChild(reviewCard);
    });
}

// === LOAD MOVIE TITLE FOR FEEDBACK PAGE ===
async function loadMovieTitleForFeedback(movieId) {
    try {
        const response = await fetch(`/api/movies/${movieId}`);
        const data = await response.json();
        
        if (data.success && data.movie) {
            const titleDisplay = document.getElementById('movie-title-display');
            if (titleDisplay) {
                titleDisplay.innerHTML = `About: <strong style="color: var(--primary);">${data.movie.title}</strong>`;
            }
            document.title = `Feedback - ${data.movie.title} - CinemaPulse`;
        }
    } catch (error) {
        console.error('Error loading movie title:', error);
    }
}

// === LOAD ANALYTICS ===
async function loadAnalytics() {
    try {
        const response = await fetch('/api/analytics');
        const data = await response.json();
        
        if (!response.ok || !data.success) {
            // Handle error - might be access denied
            if (data.error && data.error.includes('Admin')) {
                // Access denied - show message
                const statsGrid = document.querySelector('.stats-grid');
                if (statsGrid) {
                    statsGrid.innerHTML = `
                        <div style="grid-column: 1 / -1; text-align: center; padding: 3rem; color: var(--text-gray);">
                            <h2 style="color: var(--secondary); margin-bottom: 1rem;">🔒 Access Denied</h2>
                            <p>Only administrators can view analytics.</p>
                            <p style="margin-top: 1rem;">Please log in with an admin account.</p>
                            <a href="/" class="btn btn-primary" style="margin-top: 2rem; display: inline-block;">
                                Go to Login
                            </a>
                        </div>
                    `;
                }
                return;
            } else if (data.error && data.error.includes('Not logged in')) {
                // Not logged in
                window.location.href = '/';
                return;
            }
        }
        
        if (data.success && data.analytics) {
            // Update overall stats
            const stats = data.analytics;
            
            const statValues = document.querySelectorAll('.stat-value');
            if (statValues[0]) statValues[0].textContent = stats.total_movies;
            if (statValues[1]) statValues[1].textContent = stats.total_reviews;
            if (statValues[2]) statValues[2].textContent = stats.overall_avg_rating.toFixed(1);
            if (statValues[3]) statValues[3].textContent = stats.positive_percentage.toFixed(0) + '%';
            
            // Update movie stats
            if (data.movies) {
                const movieStatsContainer = document.querySelector('.movie-stats');
                if (movieStatsContainer) {
                    movieStatsContainer.innerHTML = '';
                    
                    data.movies.forEach(movie => {
                        const movieStatCard = document.createElement('div');
                        movieStatCard.className = 'movie-stat-card';
                        movieStatCard.innerHTML = `
                            <div>
                                <h3 style="margin-bottom: 0.5rem;">${movie.title}</h3>
                                <p style="color: var(--text-gray);">
                                    ${movie.total_reviews} reviews • 
                                    Average Rating: <strong style="color: var(--primary);">${movie.rating.toFixed(1)}/5</strong>
                                </p>
                            </div>
                            <div style="text-align: right;">
                                <div class="rating-badge">${movie.rating.toFixed(1)}</div>
                            </div>
                        `;
                        movieStatsContainer.appendChild(movieStatCard);
                    });
                }
            }
        }
    } catch (error) {
        console.error('Error loading analytics:', error);
        const statsGrid = document.querySelector('.stats-grid');
        if (statsGrid) {
            statsGrid.innerHTML = `
                <div style="grid-column: 1 / -1; text-align: center; padding: 3rem; color: var(--text-gray);">
                    <h2 style="color: var(--secondary); margin-bottom: 1rem;">⚠️ Error Loading Analytics</h2>
                    <p>Unable to load analytics data. Please try again later.</p>
                </div>
            `;
        }
    }
}

// === UTILITY FUNCTIONS ===

// Search movies function
async function searchMovies() {
    const searchTerm = document.getElementById('search-input')?.value.toLowerCase() || '';
    const genre = document.getElementById('genre-filter')?.value || '';
    const minRating = parseFloat(document.getElementById('rating-filter')?.value) || 0;
    
    try {
        const response = await fetch('/api/movies');
        const data = await response.json();
        
        if (data.success && data.movies) {
            // Filter movies
            let filteredMovies = data.movies;
            
            // Filter by search term
            if (searchTerm) {
                filteredMovies = filteredMovies.filter(movie => 
                    movie.title.toLowerCase().includes(searchTerm) ||
                    movie.description.toLowerCase().includes(searchTerm)
                );
            }
            
            // Filter by genre
            if (genre) {
                filteredMovies = filteredMovies.filter(movie => 
                    movie.genre === genre
                );
            }
            
            // Filter by rating
            if (minRating > 0) {
                filteredMovies = filteredMovies.filter(movie => 
                    movie.rating >= minRating
                );
            }
            
            // Display filtered movies
            const movieGrid = document.querySelector('.movie-grid');
            movieGrid.innerHTML = '';
            
            if (filteredMovies.length === 0) {
                movieGrid.innerHTML = `
                    <div style="grid-column: 1 / -1; text-align: center; padding: 3rem;">
                        <p style="color: var(--text-gray); font-size: 1.2rem;">No movies found</p>
                        <button onclick="resetSearch()" class="btn btn-primary" style="margin-top: 1rem; width: auto;">
                            Show All Movies
                        </button>
                    </div>
                `;
                return;
            }
            
            filteredMovies.forEach(movie => {
                const movieCard = createMovieCard(movie);
                movieGrid.appendChild(movieCard);
            });
        }
    } catch (error) {
        console.error('Error searching movies:', error);
    }
}

// Reset search
function resetSearch() {
    const searchInput = document.getElementById('search-input');
    const genreFilter = document.getElementById('genre-filter');
    const ratingFilter = document.getElementById('rating-filter');
    
    if (searchInput) searchInput.value = '';
    if (genreFilter) genreFilter.value = '';
    if (ratingFilter) ratingFilter.value = '';
    
    loadMovies();
}

// Debounce function for real-time search
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Show loading state
function showLoading(button) {
    button.disabled = true;
    button.innerHTML = '<span>Loading...</span>';
}

// Hide loading state
function hideLoading(button, originalText) {
    button.disabled = false;
    button.innerHTML = originalText;
}

// Display error message
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    errorDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #ff4444;
        color: white;
        padding: 1rem 2rem;
        border-radius: 8px;
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(errorDiv);
    
    setTimeout(() => {
        errorDiv.remove();
    }, 3000);
}

// Display success message
function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'success-message';
    successDiv.textContent = message;
    successDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #48bb78;
        color: white;
        padding: 1rem 2rem;
        border-radius: 8px;
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(successDiv);
    
    setTimeout(() => {
        successDiv.remove();
    }, 3000);
}