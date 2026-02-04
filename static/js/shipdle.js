console.log("shipdle.js loaded");

// inputs
const guessInput = document.getElementById("guess-input");
const guessButton = document.getElementById("guess-button");
// feedback
const container = document.getElementById("guess-container");

guessButton.addEventListener("click", () => {
    submitGuess();
});

function submitGuess() {
    const guess = guessInput.value.trim();
    if(!guess) return;

    isSubmitting = true;

    fetch(GUESS_URL, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ guess: guess })
    })
    .then(response => response.json())
    .then(data => {
        if(!data.valid) { return; }

        console.log("starting submit");
        console.log("Server Response:", data);

    })
}
