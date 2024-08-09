// DOM Elements
const searchbar = document.getElementById("q");
// Container for nav search bar results
const searchResultsContainer = document.getElementById("search-bar-results");
const closeMobileSearchBar = document.getElementById("close-search");
const openSearchBarBtn = document.getElementById("open-search");
const searchBarContainer = document.getElementById("search-bar-container");
// Wrapper for search bar results on search results page
const searchPageWrapper = document.getElementById("search-results-wrapper");
const searchValue = document.getElementById("search-value");
/* This value is to keep track of what was searched for when search bar is 
unfocused. If when it's focused again and its value is the same as this value, 
no need to recall api */
let searchedValue = null;

/**
 * Fetch search results by similar movie title
 * @param query the string that is searched for
 * @param parentContainer the parent html element the results will be appended to
 */
const fetchSearchResult = (query, parentContainer) => {
    fetch(`/search-results?q=${encodeURIComponent(query)}`)
    .then(response => { if (response.ok) return response.json(); })
    .then(data => {
        let results;
        if (data.results.length) {
            results = data.results;
        } else {
            results = { Error: `Could not find the movie '${query}'`, };
        }
        buildSearchBarResults(results, parentContainer);
    })
    .catch(error => {
        console.log(error);
    })
}

/**
 * Builds the search bar results
 * @param results the reults from fetch call to OMDB
 * @param parentContainer the parent html element the results will be appended to
 */
const buildSearchBarResults = async (results, parentContainer) => {
    clearSearchResults();
    parentContainer.classList.contains("d-none") ? parentContainer.classList.remove("d-none") : null;

    // Start build of search result elements
    if (results.Error) {
        const p = document.createElement('p');
        p.textContent = results.Error;
        p.classList.add("mb-0", "px-2", "py-3", "search-result", "rounded");
        parentContainer.append(p);
    } else {
        results.forEach((movie, index) => {
            const movieLink = document.createElement("a");
            const leftContainer = document.createElement("div");
            const rightContainer = document.createElement("div");
            const moviePosterContainer = document.createElement("div");
            const moviePoster = document.createElement("img");
            const movieTitle = document.createElement('p');
            const movieYear = document.createElement('p');
            const movieOverview = document.createElement('p');

            movieLink.classList.add("search-result", "container-fluid", "p-2", "d-flex", "border-bottom", "text-decoration-none", "link-dark");
            if (results.length === 1)
                movieLink.classList.add("rounded");
            if (index === 0)
                movieLink.classList.add("rounded-top");
            if (index === results.length - 1) {
                movieLink.classList.add("rounded-bottom");
                movieLink.classList.remove("border-bottom")
            }
            leftContainer.classList.add("result-left", "me-2");
            rightContainer.classList.add("result-right", "py-1");
            moviePosterContainer.classList.add("result-img-wrapper");
            moviePoster.classList.add("result-img");
            movieTitle.classList.add("result-title", "mb-0", "fw-bold");
            movieYear.classList.add("result-year", "opacity-50", "mb-0");
            movieOverview.classList.add("search-bar-overview");

            if (movie.poster_path)
                moviePoster.src = `https://image.tmdb.org/t/p/w92${movie.poster_path}`;
            else
                moviePoster.src = "/static/imgs/image-not-found-vector.jpg";
            movieTitle.textContent = movie.original_title;
            // Format date
            movieYear.textContent = movie.release_date.slice(0,4) || '';
            movieLink.href = `/movie?id=${movie.id}`;
            movieOverview.textContent = movie.overview;

            moviePosterContainer.append(moviePoster);
            leftContainer.append(moviePosterContainer);
            rightContainer.append(movieTitle, movieYear, movieOverview);
            movieLink.append(leftContainer, rightContainer);
            parentContainer.append(movieLink);
        })
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
        searchedValue = null;
        return;
    }
    clearTimeout(timeout);
    let query = searchbar.value;
    searchedValue = query;

    timeout = setTimeout(() => {
        fetchSearchResult(query, searchResultsContainer);
    }, 1000);
})

// Closes and clears mobile search bar
closeMobileSearchBar.addEventListener("click", () => {
    if (searchBarContainer.classList.contains("sticky-search-open"))
        searchBarContainer.classList.remove("sticky-search-open");
    searchbar.value = '';
    searchedValue = null;
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
    if (searchbar.value === searchedValue
    && searchResultsContainer.classList.contains("d-none")) {
        searchResultsContainer.classList.remove("d-none");
    }
})

// Open search bar when search icon clicked and focus input
openSearchBarBtn.addEventListener("click", () => {
    searchBarContainer.classList.add("sticky-search-open");
    searchbar.focus();
})

// If on search page, display search results immediately
if (searchPageWrapper) {
    (function() {
        if (!searchValue.textContent) {
            const p = document.createElement('p');
            p.textContent = "Please search for a movie.";
            p.classList.add("mb-0", "px-2", "py-3", "search-result", "rounded");
            searchPageWrapper.append(p);
        } else {
            fetchSearchResult(searchValue.textContent, searchPageWrapper);
        }
    })();
}