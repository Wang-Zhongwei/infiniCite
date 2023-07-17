// @ts-nocheck
const libraryList = document.querySelector(".library-list");
let selectedPaperId = "";

function toggleLibraryCheckBox(showCheckbox, librariesToCheckIds = []) {
  libraryList.querySelectorAll("input").forEach((input) => {
    if (showCheckbox) {
      input.removeAttribute("hidden");
      if (librariesToCheckIds.includes(parseInt(input.value)) || librariesToCheckIds.includes(input.value)) {
        input.checked = true;
      } else {
        input.checked = false;
      }
    } else {
      input.checked = false;
      input.setAttribute("hidden", "");
    }
  });
  // display the confirm button
  const confirmBtn = document.querySelector(".confirm-save-to-libraries-btn");
  const cancelBtn = document.querySelector(".cancel-save-to-libraries-btn");
  if (showCheckbox) {
    confirmBtn.removeAttribute("hidden");
    cancelBtn.removeAttribute("hidden");
  } else {
    confirmBtn.setAttribute("hidden", "");
    cancelBtn.setAttribute("hidden", "");
  }
}

function showSidebar() {
  // toggle the sidebar if closed
  const body = document.querySelector("body");
  if (body.classList.contains("sidebar-closed")) {
    body.classList.remove("sidebar-closed");
  }
  // display the library list if not shown
  const libraryContainer = document.querySelector("#library-links-container");
  if (!libraryContainer.classList.contains("show")) {
    libraryContainer.classList.add("show");
  }
}

function batchSave(paperId, libraryIds) {
  fetch(`/api/paper/${paperId}/libraries/`, {
    method: "POST",
    body: JSON.stringify({
      libraryIds: libraryIds,
    }),
    headers: { "Content-Type": "application/json", "X-CSRFToken": csrftoken },
  })
    .then(modifyPaperLibraryList(paperId, libraryIds))
    .catch((err) => {
      console.log(err);
      alert("Error saving paper!");
    });
}

function confirmBtnOnClick() {
  if (selectedPaperId === "") {
    alert("Paper not selected!");
    return;
  }

  oldLibraryIds = getOldLibraryIds(selectedPaperId);
  if (oldLibraryIds.length > 0) {
    batchRemove(selectedPaperId, oldLibraryIds);
  }

  newLibraryIds = getNewLibraryIds();
  if (newLibraryIds.length === 0) {
    alert("No library selected!");
  } else {
    batchSave(selectedPaperId, newLibraryIds);
    toggleLibraryCheckBox(false);
    alert("Paper saved!");
  }
}

function getOldLibraryIds(paperId) {
  const input = document.getElementById(`manage-paper-${paperId}`);
  if (input) {
    // Get the libraries data from the associated script tag
    const script = input.nextElementSibling;
    const oldLibraries = JSON.parse(script.textContent);
    return oldLibraries.map((library) => library.id);
  } else {
    return [];
  }
}

function getNewLibraryIds() {
  const libraryIds = [];
  libraryList.querySelectorAll("input").forEach((input) => {
    if (input.checked) {
      libraryIds.push(input.value);
    }
  });
  return libraryIds;
}

function savePaper(id) {
  showSidebar();
  toggleLibraryCheckBox(true);
  selectedPaperId = id;
}

function managePaperClickHandler(paperId) {
  oldLibraryIds = getOldLibraryIds(paperId);
  managePaper(paperId, oldLibraryIds);
}

function managePaper(id, oldLibraryIds) {
  selectedPaperId = id;
  showSidebar();
  toggleLibraryCheckBox(true, oldLibraryIds);
}

function batchRemove(paperId, libraryIds) {
  fetch(`/api/paper/${paperId}/libraries/`, {
    method: "DELETE",
    body: JSON.stringify({
      libraryIds: libraryIds,
    }),
    headers: { "Content-Type": "application/json", "X-CSRFToken": csrftoken },
  }).catch((err) => {
    console.log(err);
    alert("Error deleting paper!");
  });
}

function removePaper(paperId, libraryId) {
  fetch(`/api/paper/${paperId}/libraries/${libraryId}/`, {
    method: "DELETE",
    headers: { "Content-Type": "application/json", "X-CSRFToken": csrftoken },
  })
    .then(() => {
      alert("Paper removed!");
      location.reload();
    })
    .catch((err) => {
      console.log(err);
      alert("Error removing paper!");
    });
}

function cancelBtnOnClick() {
  selectedPaperId = "";
  toggleLibraryCheckBox(false);
}

// TODO: implement this
function modifyPaperLibraryList(paperId, libraryIds) {
  const oldInput = document.getElementById(`manage-paper-${paperId}`);
  if (oldInput) {
    // Get the libraries data from the associated script tag
    const script = oldInput.nextElementSibling;
    const oldLibraries = JSON.parse(script.textContent);
    const newLibraries = libraryIds.map((libraryId) => {
      return {
        id: libraryId,
        name: oldLibraries.find((library) => library.id === libraryId)?.name || document.getElementById(`library-checkbox-${libraryId}`).title,
      };
    });
    script.textContent = JSON.stringify(newLibraries);
  }
}
