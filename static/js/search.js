document.addEventListener("DOMContentLoaded", function () {
    const searchbar = document.getElementById("q");
    const searchResultsContainer = document.getElementById("search-form-result");
    const movieIDs = [];

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
    const fetchMovieInfo = async (query) => {
        try {
            const response = await fetch(`/results?q=${encodeURIComponent(query)}&type=t`);
            if (response.ok) {
                const data = await response.json();
                return data;
            } else {
                throw new Error("Network response was not ok.");
            }
        } catch(error) {
            console.log(error);
        }
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
        }, 1000);
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
    const buildSearchBarResults = async results => {
        clearSearchResults();
        searchResultsContainer.classList.add("border");
        let index = 0;

        // Start build of search result elements
        if (results.Error) {
            console.log(results.Error);
            const p = document.createElement('p');
            p.textContent = results.Error;
            p.classList.add("mt-3");
            searchResultsContainer.append(p);
        } else {
            for (const movie of results) {
                const movieInfo = await fetchMovieInfo(movie.Title);
                // Prevent duplicate movies
                if (movieIDs.includes(movieInfo.imdbID)) continue;
                movieIDs[index++] = movieInfo.imdbID;

                const movieLinkTag = document.createElement("a");
                const movieDiv = document.createElement("div");
                const leftContainer = document.createElement("div");
                const rightContainer = document.createElement("div");
                const movieInfoBody = document.createElement("div");
                const moviePoster = document.createElement("img");
                const movieTitle = document.createElement('p');
                const movieYear = document.createElement('p');

                movieLinkTag.classList.add("card", "border-bottom", "my-3");
                movieDiv.classList.add("row");
                leftContainer.classList.add("col-1")
                moviePoster.classList.add("img-fluid", "rounded");
                rightContainer.classList.add("col-11");
                movieInfoBody.classList.add("card-body");
                movieTitle.classList.add("card-title");
                movieYear.classList.add("card-text", "text-muted");

                if (movieInfo.Poster !== "N/A")
                    moviePoster.src = movieInfo.Poster;
                else
                    moviePoster.src = "/static/imgs/image-not-found-vector.jpg";
                movieTitle.textContent = movieInfo.Title;
                movieYear.textContent = movieInfo.Year;

                leftContainer.append(moviePoster);
                movieInfoBody.append(movieTitle, movieYear);
                rightContainer.append(movieInfoBody);
                movieDiv.append(leftContainer, rightContainer);
                movieLinkTag.append(movieDiv);
                searchResultsContainer.append(movieDiv);
            }
        }
    }

    const clearSearchResults = () => {
        searchResultsContainer.innerHTML = '';
        searchResultsContainer.classList.remove("border");
    }

    // Clear the search results container in search bar is unfocused
    // searchbar.addEventListener("focusout", () => {
    //     if (!searchResultsContainer.contains(document.activeElement) && document.activeElement !== searchbar)
    //         clearSearchResults();
    // })
})