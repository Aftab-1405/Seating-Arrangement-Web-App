/**
 * Document: main.js
 * Description: This script handles various functionalities for a seating arrangement application.
 * It includes typing effects, adding/deleting seats, toggling password visibility, and generating PDFs.
 */

// Document fully loaded event
document.addEventListener("DOMContentLoaded", function () {
  // Initialize typing effect
  startTypingEffect();

  // Event listener for adding seats button
  document.getElementById("addSeats").addEventListener("click", addSeats);

  // Form submission event listener for generating PDF
  const form = document.getElementById("seatingForm");
  form.addEventListener("submit", generatePDF);

  // Event listener for toggling delete mode
  const deleteSeatsToggle = document.getElementById("deleteSeatsToggle");
  deleteSeatsToggle.addEventListener("click", toggleDeleteSeats);

  // Keydown event listener for seat table
  document
    .getElementById("seatTable")
    .addEventListener("keydown", handleTableKeyDown);

  // Visibility change event listener (tab switch)
  document.addEventListener("visibilitychange", handleVisibilityChange, false);
});

// Handles visibility change (tab switch)
function handleVisibilityChange() {
  if (document.hidden) {
    // Save typed text in localStorage when tab is hidden
    const typedText = document.getElementById("typingEffect").textContent;
    localStorage.setItem("typedText", typedText);
  } else {
    // Restart typing effect when tab is visible again
    startTypingEffect();
  }
}

// Initiates the typing effect
function startTypingEffect() {
  const typingEffectElement = document.getElementById("typingEffect");
  const storedText = localStorage.getItem("typedText");
  const toTypeText = "Department of Technology, SUK";

  typingEffectElement.innerHTML = storedText || "";
  typeText(
    typingEffectElement,
    toTypeText,
    typingEffectElement.innerHTML.length
  );
}

// Simulates a typing effect
function typeText(element, text, index) {
  if (index < text.length && !document.hidden) {
    element.innerHTML += text.charAt(index);
    index++;
    element.classList.add("breathing-effect");
    setTimeout(() => typeText(element, text, index), 100);
  } else if (index === text.length) {
    localStorage.setItem("typedText", element.textContent);
  }
}

// Handles keydown events in the seat table
function handleTableKeyDown(event) {
  const target = event.target;
  if (event.key === "Enter") {
    event.preventDefault();
    if (target.name.startsWith("benchNo")) {
      target.parentElement.nextElementSibling.firstElementChild.focus();
    } else if (target.name.startsWith("seatNo")) {
      addSeats();
      const nextRowInput =
        target.parentElement.parentElement.nextElementSibling.firstElementChild
          .firstElementChild;
      nextRowInput && nextRowInput.focus();
    }
  }
}

// Counter for the number of rows in the table
let rowCount = 0;

// Adds new seats to the seat table
function addSeats() {
  const table = document.getElementById("seatTable");
  const row = table.insertRow(-1);

  const createInputCell = (inputType, inputName) => {
    const cell = row.insertCell();
    const input = document.createElement("input");
    input.type = inputType;
    input.name = inputName;
    cell.appendChild(input);
  };

  createInputCell("number", "benchNo[]");
  createInputCell("number", "seatNo[]");

  rowCount++;
}

// State tracking for delete mode
let deleteMode = false;

// Toggles delete mode in the seat table
function toggleDeleteSeats() {
  deleteMode = !deleteMode;
  const table = document.getElementById("seatTable");
  const rows = table.getElementsByTagName("tr");

  if (deleteMode) {
    // Enter delete mode: add checkboxes
    for (let i = 0; i < rows.length; i++) {
      let cell = rows[i].cells[0];
      if (!cell.querySelector('input[type="checkbox"]')) {
        // Only add checkboxes if they don't already exist
        cell = rows[i].insertCell(0);
        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        cell.appendChild(checkbox);
      }
    }
    // Update button text to indicate it's now a confirm delete action
    deleteSeatsToggle.textContent = "Confirm Delete";
  } else {
    // Exit delete mode: remove checked rows and checkboxes
    const checkboxes = table.querySelectorAll("input[type='checkbox']");
    let countDeleted = 0;
    checkboxes.forEach((checkbox) => {
      if (checkbox.checked) {
        checkbox.closest("tr").remove();
        countDeleted++;
      }
    });

    if (countDeleted > 0) {
      alert(countDeleted + " seats deleted");
    }

    // Remove all remaining checkboxes (not just unchecked)
    checkboxes.forEach((checkbox) => checkbox.closest("td").remove());

    deleteSeatsToggle.textContent = "Delete Seat";
    deleteMode = false;
  }
}

// Handles form submission to generate PDF
function generatePDF(event) {
  event.preventDefault();

  fetch("/generate-pdf", {
    method: "POST",
    body: new FormData(event.target),
  })
    .then((response) => response.blob())
    .then((blob) => {
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "seating_arrangement.pdf";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    });
}

// Re-initializes the typing effect
function startTypingEffect() {
  const typingEffectElement = document.getElementById("typingEffect");
  typingEffectElement.innerHTML = ''; // Clear the content of the element
  typeText(typingEffectElement, "Department of Technology, SUK", 0);
}


// Fade out current page
document.querySelector(".page");

// Fade in new page
document.querySelector(".page").classList.remove("transition-out");
