// DOM Elements
const movieBtn = document.getElementById("movie-btn");

// Only add event listeners if movieBtn exists (logged in)
if (movieBtn) {
    movieBtn.addEventListener("click", () => {
        const movieId = movieBtn.dataset.id;
        // Save movie to list
        if (movieBtn.dataset.type === "save") {
            fetch(`/save-movie?id=${movieId}`, {
                method: "POST"
            })
            .then(response => response.json())
            .then(data => {
                if(data.success) {
                    window.location.href = data.redirect_url;
                } else {
                    console.error("Error saving movie");
                }
            })
            .catch(error => console.error("Error:", error));
        }
        // Remove movie from list
        else if (movieBtn.dataset.type === "remove") {
            fetch(`/remove-movie?id=${movieId}`, {
                method: "DELETE"
            })
            .then(response => response.json())
            .then(data => {
                if(data.success) {
                    window.location.href = data.redirect_url;
                } else {
                    console.error("Error removing movie");
                }
            })
            .catch(error => console.error("Error:", error));
        }
    })
}