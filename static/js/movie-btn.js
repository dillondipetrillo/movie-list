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
            .then(response => {{
                console.log(response);
            }})
        }
        // Remove movie from list
        else if (movieBtn.dataset.type === "remove") {

        }
    })
}