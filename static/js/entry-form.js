// DOM elements
const entryForm = document.getElementById("entry-form");
const formFields = entryForm.querySelectorAll("input");

// Find the first input element that has an error class and focus it
const errorField = [...formFields].find(field => field.classList.contains("border-danger"));
if (errorField)  {
    errorField.focus();
    // If input is type email we need to clear focused input and assign
    // value to get cursor at end
    if (errorField.type === "email") {
        let buffer = errorField.value;
        errorField.value = '';
        errorField.value = buffer;
    } else
        errorField.setSelectionRange(errorField.value.length, errorField.value.length);
}