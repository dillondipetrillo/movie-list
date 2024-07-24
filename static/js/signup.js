// DOM elements
const signUpForm = document.getElementById("sign-up-form");
const formFieldElements = signUpForm.querySelectorAll("input");

// Global values
const formFields = [...formFieldElements];
let errorFields;
const emailRegex = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9]+\.[a-zA-Z0-9-.]+$/;
const passwordRegex = /^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{7,}$/;

// Event listeners
signUpForm.addEventListener("submit", (event) => {
    event.preventDefault();
    
    // Variable to check if field is validated
    let validated = true;
    errorFields = [];

    // Validate each form field
    formFields.forEach(field => {
        if(!validateField(field) && validated)
            validated = false;
    })

    // There was an error validating fields client-side
    // Create ul showing errors
    if (!validated && errorFields.length > 0) {
        buildErrorMessages(errorFields);
    }
})

/**
 * Validate username input field
 * @param field form field being passed in to validate
 */
const validateField = field => {
    let isValid = true;
    if (field.id === "username" && field.value.length < 2) {
        errorFields.push({ [field.id]: "Username must be at least 2 characters" });
        isValid = false;
    } else if (field.id === "email" && !emailRegex.test(field.value)) {
        errorFields.push({ [field.id]: "Must enter a valid email" });
        isValid = false;
    } else if (field.id === "password" && !passwordRegex.test(field.value)) {
        errorFields.push({ [field.id]: "Password must be at least 7 characters and contain at least one uppercase letter, digit, and special character(@$!%*?&)" });
        isValid = false;
    } else if (field.id === "password-confirm" &&
    formFields.find(field => field.id === "password").value !== field.value) {
        errorFields.push({ [field.id]: "Passwords must match" });
        isValid = false;
    }

    if (!isValid) {
        field.classList.contains("border-dark") ? field.classList.remove("border-dark") : null;
        field.classList.add("border-danger");
    } else {
        field.classList.contains("border-danger") ? field.classList.remove("border-danger") : null;
        field.classList.add("border-dark");
    }
}

/**
 * Builds the ui list of error messages and appends it to the sign up form
 * @param errors The array of error object messages with form field id as key 
 */
const buildErrorMessages = errors => {
    let errorList;
    if (!(errorList = document.getElementById("sign-up-error-list"))) {
        errorList = document.createElement("ul");
        errorList.id = "sign-up-error-list";
    } else
        errorList.innerHTML = '';

    for (const error of errors) {
        const errorKey = Object.keys(error);
        const liError = document.createElement("li");
        liError.textContent = error[errorKey];
        liError.classList.add("text-danger");
        errorList.append(liError);
    }
    signUpForm.insertAdjacentElement("afterend", errorList);
}