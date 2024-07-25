// DOM elements
const entryForm = document.getElementById("entry-form");
const formFieldElements = entryForm.querySelectorAll("input");

// Global values
const formFields = [...formFieldElements];
let errorFields;
const emailRegex = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9]+\.[a-zA-Z0-9-.]+$/;
const passwordRegex = /^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{7,}$/;
let errorMsgs;
if (entryForm.dataset.form === "signup") { // Sign up form
    errorMsgs = {
        "username": "Username must be at least 2 characters",
        "email": "Must enter a valid email",
        "password": "Password must be at least 7 characters and contain at least one uppercase letter, digit, and special character(@$!%*?&)",
        "password-confirm": "Passwords must match",
    };
} else if (entryForm.dataset.form === "login") { // Login form
    errorMsgs = {
        "email": "Invalid email",
        "password": "Invalid password",
    };
}

// Event listeners
entryForm.addEventListener("submit", (event) => {
    event.preventDefault();
    
    // Variable to check if field is validated
    let validated = true;
    errorFields = [];

    // Validate each form field
    formFields.forEach(field => {
        if(!validateField(field, formFields) && validated)
            validated = false;
    })

    // There was an error validating fields client-side
    // Create ul showing errors
    if (!validated && errorFields.length > 0) {
        buildErrorMessages(errorFields, entryForm);
        // Put focus on first found invalid input
        focusInvalidInput(formFields);
    }
})

/**
 * Validate username input field
 * @param field form field being passed in to validate
 * @param fieldsArr the list of the form fiels used to find password to compare to confirm password
 */
const validateField = (field, fieldsArr) => {
    let isValid = true;
    if (field.id === "username" && field.value.length < 2 ||
        field.id === "email" && !emailRegex.test(field.value) ||
        field.id === "password" && !passwordRegex.test(field.value) ||
        (field.id === "password-confirm" && 
        fieldsArr.find(field => field.id === "password").value !== field.value)
    ) {
        isValid = false;
    }

    if (!isValid) {
        field.classList.add("border-danger", "focus-ring", "focus-ring-danger");
        errorFields.push({ [field.id]: errorMsgs[field.id] });
    } else {
        field.classList.contains("border-danger") &&
        field.classList.contains("focus-ring") &&
        field.classList.contains("focus-ring-danger") ? 
            field.classList.remove("border-danger", "focus-ring", "focus-ring-danger") : 
            null;
    }
}

/**
 * Builds the ui list of error messages and appends it to the sign up form
 * @param errors The array of error object messages with form field id as key
 * @param form the form that we need to append the error list after
 */
const buildErrorMessages = (errors, form) => {
    let errorList;
    if (!(errorList = document.getElementById("form-error-list"))) {
        errorList = document.createElement("ul");
        errorList.id = "form-error-list";
    } else
        errorList.innerHTML = '';

    for (const error of errors) {
        const errorKey = Object.keys(error);
        const liError = document.createElement("li");
        liError.textContent = error[errorKey];
        liError.classList.add("text-danger");
        errorList.append(liError);
    }
    form.insertAdjacentElement("afterend", errorList);
}

/**
 * Searchs for the first invalid input and puts focus on it
 * @param fields the input fields from the form to search through
 */
const focusInvalidInput = fields => {
    const fieldToFocus = fields.find(field => {
        return field.classList.contains("border-danger") && field.classList.contains("focus-ring-danger")
    })
    if (fieldToFocus)
        fieldToFocus.focus();
}