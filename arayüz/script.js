document.addEventListener("DOMContentLoaded", function () {
const screens = ["start-screen", "bar-selection-screen", "exercise-selection-screen", "workout-screen"];
let selectedBar = "";

const exerciseData = {
  "v-bar": [
    { name: "Lat Pulldown", video: "assets/latpulldown.mp4" },
    { name: "Seated Row", video: "assets/seatedrow.mp4" }
  ],
  "d-handle": [
    { name: "Single Arm Row", video: "assets/singlerow.mp4" }
  ]
};

function showScreen(screenId) {
  screens.forEach(id => {
    document.getElementById(id).classList.remove("visible");
  });
  document.getElementById(screenId).classList.add("visible");
}

document.getElementById("start-btn").addEventListener("click", () => {
  window.location.href="dnm.html";
});

document.querySelectorAll(".back-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const target = btn.getAttribute("data-target");
    showScreen(target);
  });
});

document.querySelectorAll(".bar-option").forEach(btn => {
  btn.addEventListener("click", () => {
    selectedBar = btn.getAttribute("data-bar");
    const exerciseList = document.querySelector(".exercise-options");
    exerciseList.innerHTML = "";

    if (exerciseData[selectedBar]) {
      exerciseData[selectedBar].forEach(ex => {
        const btn = document.createElement("button");
        btn.className = "exercise-option";
        btn.textContent = ex.name;
        btn.onclick = () => {
          document.getElementById("workout-title").textContent = ex.name;
          document.getElementById("workout-video").src = ex.video;
          showScreen("workout-screen");
        };
        exerciseList.appendChild(btn);
      });
    }

    showScreen("exercise-selection-screen");
  });
});

});