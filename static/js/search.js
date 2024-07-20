document.addEventListener("DOMContentLoaded", function () {
    const searchbar = document.getElementById("q");
    const searchResultsContainer = document.getElementById("search-form-result");

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

    // Fetch a single movies info
    const fetchMovieInfo = (query) => {
        fetch(`/results?q=${encodeURIComponent(query)}&type=t`)
        .then(response => { if (response.ok) return response.json(); })
        .then(data => {
            console.log(data);
        })
        .catch(error => {
            console.log(error);
        })
    }

    let timeout = null;

    searchbar.addEventListener("input", () => {
        if (!searchbar.value) {
            clearSearchResults();
            clearTimeout(timeout);
            return;
        }
        clearTimeout(timeout);
        let query = searchbar.value;

        timeout = setTimeout(() => {
            fetchSearchResult(query);
        }, 1250);
    })

    searchbar.addEventListener("focus", () => {
        if (searchbar.value)
            fetchSearchResult(searchbar.value);
    })

    /* Use when going to /search page from GET request
        Display search results in the main tag on page */
    if (searchbar.value)
        fetchSearchResult(searchbar.value);

    /**
     * Builds the search bar results
     * @param results the reults from fetch call to OMDB
     */
    const buildSearchBarResults = results => {
        clearSearchResults();
        searchResultsContainer.classList.add("border");

        // Start build of search result elements
        if (results.Error) {
            console.log(results.Error);
            const p = document.createElement('p');
            p.textContent = results.Error;
            p.classList.add("mt-3");
            searchResultsContainer.append(p);
        } else {
            for (const movie of results) {
                console.log(movie);
                const movieDiv = document.createElement("div");
                const leftContainer = document.createElement("div");
                const rightContainer = document.createElement("div");
                const moviePoster = document.createElement("img");
                const movieTitle = document.createElement('p');
                const movieYear = document.createElement('p');

                movieDiv.classList.add("d-flex", "justify-content-start", "py-3");
                rightContainer.classList.add("d-flex", "flex-column");
                leftContainer.classList.add("mw-25")
                moviePoster.classList.add("float-left", "rounded", "img-fluid", "w-100");

                moviePoster.src = movie.Poster;
                movieTitle.textContent = movie.Title;
                movieYear.textContent = movie.Year;

                leftContainer.append(moviePoster);
                rightContainer.append(movieTitle, movieYear);
                movieDiv.append(leftContainer, rightContainer);
                searchResultsContainer.append(movieDiv);
            }
        }
    }

    const clearSearchResults = () => {
        searchResultsContainer.innerHTML = '';
        searchResultsContainer.classList.remove("border");
    }

    // Clear the search results container in search bar is unfocused
    searchbar.addEventListener("focusout", () => {
        if (!searchResultsContainer.contains(document.activeElement) && document.activeElement !== searchbar)
            clearSearchResults();
    })
})