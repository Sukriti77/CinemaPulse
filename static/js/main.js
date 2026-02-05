// ===============================================
// CinemaPulse - Interactive JavaScript (STABLE)
// ===============================================

const DEFAULT_POSTER =
  'https://via.placeholder.com/400x600?text=No+Poster';

// ===============================================
// LOGIN VALIDATION (FIXED)
// ===============================================
async function validateLogin(event) {
    event.preventDefault();

    const email = document.getElementById('login-email')?.value;
    const password = document.getElementById('login-password')?.value;

    if (!email || !password) {
        showError('Please fill in all fields');
        return false;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        showError('Please enter a valid email address');
        return false;
    }

    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (!data.success) {
            showError(data.message || 'Login failed');
            return false;
        }

        // 🔥 IMPORTANT: correct admin route
        window.location.href =
            data.user.role === 'admin' ? '/admin' : '/dashboard';

    } catch (error) {
        console.error('Login error:', error);
        showError('Login failed. Please try again.');
    }

    return false;
}

// ===============================================
// STAR RATING
// ===============================================
let selectedRating = 0;

function initStarRating() {
    const stars = document.querySelectorAll('.star');
    const ratingInput = document.getElementById('rating');
    if (!stars.length || !ratingInput) return;

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

    document
        .querySelector('.star-rating')
        ?.addEventListener('mouseleave', updateStars);
}

function updateStars() {
    document.querySelectorAll('.star').forEach((star, index) => {
        star.classList.toggle('active', index < selectedRating);
    });
}

function highlightStars(count) {
    document.querySelectorAll('.star').forEach((star, index) => {
        star.classList.toggle('active', index < count);
    });
}

// ===============================================
// FEEDBACK SUBMISSION (AWS SAFE)
// ===============================================
async function validateFeedback(event) {
    event.preventDefault();

    const rating = document.getElementById('rating')?.value;
    const comment = document.getElementById('comment')?.value;
    const movieId = document.getElementById('movie_id')?.value;

    if (!rating || !comment || !movieId) {
        alert('Please fill in all fields');
        return false;
    }

    try {
        const response = await fetch('/api/feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                movie_id: parseInt(movieId), // DynamoDB expects NUMBER
                rating: parseInt(rating),
                comment: comment
            })
        });

        const data = await response.json();

        if (data.success) {
            window.location.href = '/thankyou';
        } else {
            alert(data.error || 'Failed to submit feedback');
        }
    } catch (error) {
        console.error('Feedback error:', error);
        alert('Failed to submit feedback');
    }

    return false;
}

// ===============================================
// LOAD MOVIES (DASHBOARD)
// ===============================================
async function loadMovies() {
    try {
        const response = await fetch('/api/movies');
        const data = await response.json();
        if (!data.success || !data.movies) return;

        const grid = document.querySelector('.movie-grid');
        if (!grid) return;

        grid.innerHTML = '';
        data.movies.forEach(movie => {
            grid.appendChild(createMovieCard(movie));
        });

    } catch (error) {
        console.error('Error loading movies:', error);
    }
}

// ===============================================
// CREATE MOVIE CARD (BULLETPROOF)
// ===============================================
function createMovieCard(movie) {
    const card = document.createElement('div');
    card.className = 'movie-card';

    const poster = movie.poster || DEFAULT_POSTER;
    const description = movie.description
        ? movie.description.substring(0, 100)
        : 'No description available';

    card.innerHTML = `
        <img src="${poster}"
             class="movie-poster"
             onerror="this.src='${DEFAULT_POSTER}'">

        <div class="movie-info">
            <h2 class="movie-title">${movie.title}</h2>

            <div class="movie-rating">
                <span class="stars">★★★★★</span>
                <span class="rating-text">${movie.rating || 0}/5</span>
            </div>

            <p class="movie-description">${description}...</p>

            <a href="/movie/${movie.id}" class="btn btn-primary">
                View Details
            </a>
        </div>
    `;
    return card;
}

// ===============================================
// MOVIE DETAILS PAGE
// ===============================================
async function loadMovieDetails(movieId) {
    try {
        const response = await fetch(`/api/movies/${movieId}`);
        const data = await response.json();
        if (!data.success || !data.movie) return;

        const movie = data.movie;
        document.title = `${movie.title} - CinemaPulse`;

        document.querySelector('.detail-content h1') &&
            (document.querySelector('.detail-content h1').textContent = movie.title);

        document.querySelector('.movie-description') &&
            (document.querySelector('.movie-description').textContent = movie.description || '');

        document.querySelector('.rating-badge') &&
            (document.querySelector('.rating-badge').textContent = `${movie.rating || 0}/5`);

        const posterEl = document.querySelector('.detail-poster');
        if (posterEl) {
            posterEl.src = movie.poster || DEFAULT_POSTER;
            posterEl.onerror = () => posterEl.src = DEFAULT_POSTER;
        }

        loadReviews(movie.reviews || []);

    } catch (error) {
        console.error('Error loading movie details:', error);
    }
}

// ===============================================
// REVIEWS
// ===============================================
function loadReviews(reviews) {
    const section = document.querySelector('.reviews-section');
    if (!section) return;

    section.querySelectorAll('.review-card').forEach(r => r.remove());

    reviews.forEach(review => {
        const div = document.createElement('div');
        div.className = 'review-card';
        div.innerHTML = `
            <div class="review-header">
                <span>${review.name || 'Anonymous'}</span>
                <span>${'★'.repeat(review.rating)}${'☆'.repeat(5 - review.rating)}</span>
            </div>
            <p>${review.comment}</p>
        `;
        section.appendChild(div);
    });
}

// ===============================================
// ANALYTICS
// ===============================================
async function loadAnalytics() {
    try {
        const response = await fetch('/api/analytics');
        const data = await response.json();
        if (!data.success) return;

        const stats = document.querySelectorAll('.stat-value');
        stats[0].textContent = data.analytics.total_movies;
        stats[1].textContent = data.analytics.total_reviews;
        stats[2].textContent = data.analytics.overall_avg_rating;
        stats[3].textContent = data.analytics.positive_percentage + '%';

        renderAnalyticsMovies(data.movies);

    } catch (error) {
        console.error('Analytics error:', error);
    }
}

function renderAnalyticsMovies(movies) {
    const box = document.querySelector('.movie-stats');
    if (!box) return;

    box.innerHTML = '';
    movies.forEach(m => {
        const div = document.createElement('div');
        div.className = 'movie-stat-card';
        div.innerHTML = `
            <h3>${m.title}</h3>
            <p>${m.total_reviews} reviews</p>
            <strong>${m.rating.toFixed(1)}/5</strong>
        `;
        box.appendChild(div);
    });
}

// ===============================================
// INIT
// ===============================================
document.addEventListener('DOMContentLoaded', () => {
    initStarRating();

    document.getElementById('loginForm')
        ?.addEventListener('submit', validateLogin);

    document.getElementById('feedbackForm')
        ?.addEventListener('submit', validateFeedback);

    if (document.querySelector('.movie-grid')) loadMovies();

    if (location.pathname.startsWith('/movie/'))
        loadMovieDetails(location.pathname.split('/')[2]);

    if (location.pathname === '/analytics')
        loadAnalytics();
});

// ===============================================
// UTIL
// ===============================================
function showError(msg) {
    alert(msg);
}
