document.addEventListener("DOMContentLoaded", function () {
    // DOM Elements
    const searchbar = document.getElementById("q");
    const searchResultsContainer = document.getElementById("search-bar-results");
    const closeMobileSearchBar = document.getElementById("close-search");
    const openSearchBarBtn = document.getElementById("open-search");
    const searchBarContainer = document.getElementById("search-bar-container");
    // Array to keep track of imdbIDs to catch duplicates
    let movieIDs = [];
    /* This value is to keep track of what was searched for when search bar is 
    unfocused. If when it's focused again and its value is the same as this value, 
    no need to recall api */
    let searchedMovie = null;

    // Fetch search results by similar movie title
    const fetchSearchResult = (query) => {
        // Don't show results if search bar isn't focused
        if (document.activeElement !== searchbar) return;
        fetch(`/results?q=${encodeURIComponent(query)}&type=s`)
        .then(response => { if (response.ok) return response.json(); })
        .then(data => {
            let result;
            if (data.Search) {
                result = data.Search;
            } else if (data.Error === "Too many results.") {
                result = {
                    Error: `${data.Error} Please be more specific.`,
                }
            } else {
                result = { Error: data.Error, };
            }
            buildSearchBarResults(result);
        })
        .catch(error => {
            console.log(error);
        })
    }

    /**
     * Builds the search bar results
     * @param results the reults from fetch call to OMDB
     */
    const buildSearchBarResults = async results => {
        clearSearchResults();
        movieIDs = [];
        let index = 0;

        // Start build of search result elements
        if (results.Error) {
            searchResultsContainer.classList.remove("d-none");
            const p = document.createElement('p');
            p.textContent = results.Error;
            p.classList.add("mb-0", "px-2", "py-3", "search-result", "rounded");
            searchResultsContainer.append(p);
        } else {
            for (const movie of results) {
                searchResultsContainer.classList.remove("d-none");
                // Prevent duplicate movies
                if (movieIDs.includes(movie.imdbID)) continue;
                movieIDs[index] = movie.imdbID;

                const movieLink = document.createElement("a");
                const leftContainer = document.createElement("div");
                const rightContainer = document.createElement("div");
                const moviePosterContainer = document.createElement("div");
                const moviePoster = document.createElement("img");
                const movieTitle = document.createElement('p');
                const movieYear = document.createElement('p');

                movieLink.classList.add("search-result", "container-fluid", "p-2", "d-flex", "border-bottom", "text-decoration-none");
                if (results.length === 1)
                    movieLink.classList.add("rounded");
                if (index === 0)
                    movieLink.classList.add("rounded-top");
                if (index++ === results.length - 1) {
                    movieLink.classList.add("rounded-bottom");
                    movieLink.classList.remove("border-bottom")
                }
                leftContainer.classList.add("result-left", "me-2");
                rightContainer.classList.add("result-right", "py-1");
                moviePosterContainer.classList.add("result-img-wrapper");
                moviePoster.classList.add("result-img");
                movieTitle.classList.add("result-title", "mb-0", "fw-bold", "text-dark");
                movieYear.classList.add("result-year", "text-muted", "mb-0");

                if (movie.Poster !== "N/A")
                    moviePoster.src = movie.Poster;
                else
                    moviePoster.src = "/static/imgs/image-not-found-vector.jpg";
                movieTitle.textContent = movie.Title;
                movieYear.textContent = movie.Year;
                movieLink.href = `/movie?id=${movie.imdbID}`;

                moviePosterContainer.append(moviePoster);
                leftContainer.append(moviePosterContainer);
                rightContainer.append(movieTitle, movieYear);
                movieLink.append(leftContainer, rightContainer);
                searchResultsContainer.append(movieLink);
            }
        }
    }

    /* Clears the search results bar */
    const clearSearchResults = () => {
        searchResultsContainer.innerHTML = '';
        searchResultsContainer.classList.add("d-none");
    }

    /* Event Listeners */

    let timeout = null;
    searchbar.addEventListener("input", () => {
        if (!searchbar.value) {
            clearSearchResults();
            clearTimeout(timeout);
            searchedMovie = null;
            return;
        }
        clearTimeout(timeout);
        let query = searchbar.value;
        searchedMovie = query;

        timeout = setTimeout(() => {
            fetchSearchResult(query);
        }, 1000);
    })

    // Closes and clears mobile search bar
    closeMobileSearchBar.addEventListener("click", () => {
        if (searchBarContainer.classList.contains("sticky-search-open"))
            searchBarContainer.classList.remove("sticky-search-open");
        searchbar.value = '';
        searchedMovie = null;
        clearSearchResults();
    })

    // Closes search bar if clicked outside
    document.addEventListener("click", (event) => {
        if ((!searchbar.contains(event.target) && !searchResultsContainer.contains(event.target) && !openSearchBarBtn.contains(event.target))
        && !searchResultsContainer.classList.contains("d-none")) {
            searchResultsContainer.classList.add("d-none");
        }
    })

    // Reopens closed search bar results when search bar is focused
    searchbar.addEventListener("focus", () => {
        if (!searchbar.value) return;
        if (searchbar.value === searchedMovie
        && searchResultsContainer.classList.contains("d-none")) {
            searchResultsContainer.classList.remove("d-none");
        }
    })

    // Open search bar when search icon clicked and focus input
    openSearchBarBtn.addEventListener("click", () => {
        searchBarContainer.classList.add("sticky-search-open");
        searchbar.focus();
    })
})