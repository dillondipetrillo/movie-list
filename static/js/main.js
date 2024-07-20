// DOM Elements
const closeSearch = document.getElementById("close-search");
const openSearchBarBtn = document.getElementById("open-search");
const searchBar = document.getElementById("q");
const searchBarContainer = document.getElementById("search-bar-container");

// Open search bar when search icon clicked and focus input
openSearchBarBtn.addEventListener("click", () => {
    searchBarContainer.classList.add("sticky-search-open");
    searchBar.focus();
})

// Close search bar if already open
closeSearch.addEventListener("click", () => {
    if (searchBarContainer.classList.contains("sticky-search-open"))
        searchBarContainer.classList.remove("sticky-search-open");
})