document.addEventListener("DOMContentLoaded", function () {
    const searchbar = document.getElementById("q");
    const searchResultsContainer = document.getElementById("search-form-result");

    const fetchSearchResult = (query) => {
        // Don't show results if search bar isn't focused
        if (document.activeElement !== searchbar) return;
        fetch(`/results?q=${encodeURIComponent(query)}`)
        .then(response => {
            if (response.ok)
                return response.json();
        })
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

    let timeout = null;

    searchbar.addEventListener("input", () => {
        if (!searchbar.value) {
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
     * @param searchResults the reults from fetch call to OMDB
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
        } else
            console.log("SUCCESS", results);
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