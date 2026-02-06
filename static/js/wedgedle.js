console.log("Wedgedle JS loaded")

// data structures
const HELP_CONTENT = {
    "Alignment": "Light Side, Dark Side, or Neutral",
    "Ship": "Is this character the pilot of a ship",
    "Faction": "What faction(s) is this character a part of (Empire, Jedi, etc.)",
    "Leader": "Does this character have a leader ability",
    "Release Era": "What in-game era was this character released",
    "Role": "What role does this character have in-game (Attacker, Tank, etc.)"
}

const gameDesc = "Guess the Star Wars: Galaxy of Heroes character."

let guessCount = 0;
let isAnimating = false;
let isSubmitting = false;
const maxGuesses = 500;   // maximum guesses allowed

// Get references to HTML
// inputs
const guessInput = document.getElementById("guess-input");
const guessButton = document.getElementById("guess-button");
const guessList = document.getElementById("guess-list");
// feedback
const container = document.getElementById("guess-container");
// help modal
const helpOverlay = document.getElementById("help-overlay");
const helpDesc = document.getElementById("help-description");
const helpSubtext = document.getElementById("help-subtext");
const helpBtn = document.getElementById("help-button");
const helpClose = document.getElementById("help-close-btn");
// end game screen
const endOverlay = document.getElementById("endgame-overlay");
const endTitle = document.getElementById("endgame-title");
const endGuessCnt = document.getElementById("endgame-guess-cnt");
const endAnswer = document.getElementById("endgame-answer");
const closeBtn = document.getElementById("endgame-close-btn");


getResetTime();

helpDesc.textContent = gameDesc;
for (const attr in HELP_CONTENT) {
    // const row = document.createElement("div");

    const attrHead = document.createElement("div");
    let cat = attr.replaceAll("_", " ");
    attrHead.textContent = `${cat}:`;
    attrHead.classList.add("help-sub-header");

    const attrDesc = document.createElement("div");
    attrDesc.textContent = HELP_CONTENT[attr];
    attrDesc.classList.add("help-desc");

    attrHead.appendChild(attrDesc);
    helpSubtext.appendChild(attrHead);
}
helpBtn.addEventListener("click", showHelpModal);
helpClose.addEventListener("click", hideHelpModal);
helpOverlay.addEventListener("click", (e) => {
    if(e.target === helpOverlay) {
        hideHelpModal();
    }
});

guessButton.addEventListener("click", () => {
    guessList.innerHTML = "";
    guessList.classList.add("hidden");
    submitGuess();
});
guessInput.addEventListener("keydown", (event) => {
    if(event.key === "Enter"){
        event.preventDefault();
        guessList.innerHTML = "";
        guessList.classList.add("hidden");
        
        submitGuess();
    }
});
guessInput.addEventListener("input", async () => {
    const query = guessInput.value.trim();

    if(query.length < 1) {
        guessList.innerHTML = "";
        guessList.classList.add("hidden");
        return;
    }

    const res = await fetch(`${SEARCH_URL}?q=${encodeURIComponent(query)}`)
    const data = await res.json();

    renderList(data);
});

// close end game message
closeBtn.addEventListener("click", hideEndModal);
endOverlay.addEventListener("click", (e) => {
    if(e.target === endOverlay) {
        hideEndModal();
    }
});


// functions
function submitGuess() {
    console.log("sub isAnimating: ",isAnimating);
    if(isSubmitting || isAnimating) return;
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
        
        if(!data.valid) {
            return;
        }
        // if (isAnimating) return;
        console.log("starting submit");
        guessList.innerHTML = "";
        guessList.classList.add("hidden");
        isAnimating = true;

        guessInput.value = "";
        guessInput.placeholder = "Enter character name";       
        guessCount += 1;

        // category labels appear
        if(guessCount == 1){
            document.getElementById("cat-list").classList.remove("hidden");
        }

        // set up container and row for guess feedback
        const row = document.createElement("div");
        row.className = "guess-row";

        // grab data from backend (result = feedback ; guess_info = character info) 
        const result = data.result;
        const guess_info = data.guess_info; // ( {name: , info: })      

        // append the guess name to front of row
        const box = document.createElement("div");
        const boxImg = document.createElement("img");
        console.log(`${guess_info.info["alignment"]}`)
        box.className = `box incorrect`;
        boxImg.src = guess_info.info["image"];
        boxImg.alt = "?";
        boxImg.loading = "lazy";
        boxImg.classList.add(`${guess_info.info["alignment"]}`);
        box.appendChild(boxImg);
        row.appendChild(box);

        // shows guess info with correctness
        const boxes = [];
        for(const attr in result) {
            const feedbackText = document.createElement("div");
            feedbackText.className = `box ${result[attr]} hidden`;

            let value = guess_info.info[attr];

            if(Array.isArray(value)) {
                value = value.join(", ");
            }

            if(result[attr] === "higher") {
                value += " ↑";
            } else if (result[attr] === "lower") {
                value += " ↓";
            }

            text = value;
            if(value == true) {
                text = "Yes";
            } else if (value == false) {
                text = "No";
            }
            feedbackText.textContent = text;
            row.appendChild(feedbackText);
            boxes.push(feedbackText);
        }

        container.prepend(row);
        animateBoxes(boxes, result);

        if(data.correct_guess) {
            showEndModal(true, guess_info.name, guess_info.info["image"], guess_info.info["alignment"]);
            guessButton.disabled = true;
            guessInput.disabled = true;
            return;
        }

        if(guessCount >= maxGuesses){
            // showEndModal(false, guess_info.name, guess_info.info["image"], guess_info.info["alignment"]);
            handleLoss();
            guessButton.disabled = true;
            guessInput.disabled = true;
        }
        console.log("finished submit");
        // isAnimating = false;
    })
    .catch(error => {
        console.error("Error:", error);
    })
    .finally(() => {
        isSubmitting = false;
    })
}
function resetGame() {
    guessCount = 0;
    guessButton.disabled = false;
    guessInput.disabled = false;
    hideEndModal();

    container.innerHTML = "";
    document.getElementById("cat-list").classList.add("hidden");
}

function renderList(characters) {
    // console.log("rendering list");
    guessList.innerHTML = "";
    guessList.classList.remove("hidden");

    characters.forEach(char => {
        const item = document.createElement("div");
        item.className = "guess-list-item";

        const guessImg = document.createElement("div");
        guessImg.className = 'guess-list-image';
        const img = document.createElement("img");
        img.src = char.image;
        img.alt = char.name;
        // img.loading = "lazy";
        img.classList.add(`${char["alignment"]}`);
        img.onerror = () =>  { img.style.display = "none"; };
        guessImg.appendChild(img);

        const name = document.createElement("div");
        name.className = "guess-list-name";
        name.textContent = char.name;

        item.appendChild(guessImg);
        item.appendChild(name);

        item.addEventListener("click", () => {
            guessList.innerHTML = "";
            guessList.classList.add("hidden");

            guessInput.value = char.name;
            submitGuess();
        });
        
        guessList.appendChild(item);
        // console.log("list rendered");
    })
}

async function handleLoss() {
    const res = await fetch(ANSWER_URL);
    const answer = await res.json();

    showEndModal(false, answer["name"], answer["image"], answer["alignment"]);
}

function animateBoxes(boxes, result) {
    console.log("func isAnimating: ",isAnimating);
    boxes.forEach((box, index) => {
        const attr = result;
        const resultClass = result[attr]

        setTimeout(() => {
            box.classList.add("flip");

            setTimeout(() => {
                box.classList.remove("hidden");
                box.classList.remove("flip");
                box.classList.add(resultClass);
            }, 400);
        }, index * 600);
    });
    isAnimating = false;
}

function showEndModal(isWin, correctName, correctImg, alignment) {
    endTitle.textContent = isWin ? "You Win!" : "Sorry, you lost.";
    msgColor = isWin ? "win" : "loss";
    endTitle.classList.add(msgColor);
    endGuessCnt.textContent = `You guessed today's Wedgedle in ${guessCount} guesses.`;
    
    const endImg = document.createElement("img");
    endImg.src = correctImg;
    endImg.alt = "?";
    endImg.loading = "lazy";
    endImg.classList.add(`${alignment}`);
    endImg.onerror = () =>  { img.style.display = "none"; };
    
    const endMsg = document.createElement("div");
    endMsg.textContent = `The correct answer was ${correctName}`;
    endMsg.classList.add("endgame-msg");

    endAnswer.appendChild(endImg);
    endAnswer.appendChild(endMsg);

    endOverlay.classList.remove("hidden");
}
function hideEndModal() {
    endOverlay.classList.add("hidden");
}
function showHelpModal() {
    helpOverlay.classList.remove("hidden");
}
function hideHelpModal() {
    helpOverlay.classList.add("hidden");
}

async function getResetTime() {
    const res = await fetch(TIMER_URL);
    const data = await res.json();

    SERVER_NOW = new Date(data.server_now);
    RESET_AT = new Date(data.reset_time);
    FETCHED_AT = Date.now();

    TIMER_OFFSET = SERVER_NOW.getTime() - FETCHED_AT;

    startCountdown(document.getElementById("help-timer"));
    startCountdown(document.getElementById("end-timer"));
}
function getTimeUntilReset() {
    const now = Date.now() + TIMER_OFFSET;
    const diff = RESET_AT.getTime() - now;

    const hours = Math.floor(diff / (1000*60*60));
    const mins = Math.floor((diff / (1000*60) % 60));
    const secs = Math.floor((diff / 1000) % 60);

    return {hours, mins, secs};
}
function formatCountdown( {hours, mins, secs} ) {
    return `${hours.toString().padStart(2, "0")}:` +
        `${mins.toString().padStart(2, "0")}:` +
        `${secs.toString().padStart(2, "0")}`;
}
function startCountdown(element) {
    function update() {
        const time = getTimeUntilReset();
        element.textContent = formatCountdown(time);
    }

    update();
    setInterval(update, 1000);
}

// async function preloadImages() {
//     fetch(IMAGE_URL)
//     .then(res => res.json())
//     .then(images => {
//         images.forEach(char_img => {
//             const img = new Image();
//             img.src = char_img;
//         });
//     });
// }

