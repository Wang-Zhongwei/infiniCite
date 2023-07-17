/** @format */

// @ts-nocheck
const libraryList = document.querySelector(".library-list");
let selectedPaperId = "";

function toggleLibraryCheckBox(showCheckbox, librariesToCheckIds = []) {
  libraryList.querySelectorAll("input").forEach((input) => {
    if (showCheckbox) {
      input.removeAttribute("hidden");
      if (
        librariesToCheckIds.includes(parseInt(input.value)) ||
        librariesToCheckIds.includes(input.value)
      ) {
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
  newLibraryIds = getNewLibraryIds();

  const toDeleteLibraryIds = oldLibraryIds.filter(
    (id) => !newLibraryIds.includes(id)
  );
  const toSaveLibraryIds = newLibraryIds.filter(
    (id) => !oldLibraryIds.includes(id)
  );
  batchRemove(selectedPaperId, toDeleteLibraryIds);
  batchSave(selectedPaperId, toSaveLibraryIds);
  toggleLibraryCheckBox(false);
  alert("Success!");
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
  const newLibraryIds = [];
  libraryList.querySelectorAll("input").forEach((input) => {
    if (input.checked) {
      newLibraryIds.push(Number(input.value));
    }
  });
  return newLibraryIds;
}

function savePaper(id) {
  showSidebar();
  toggleLibraryCheckBox(true);
  selectedPaperId = id;
}

function managePaperOnClick(paperId) {
  oldLibraryIds = getOldLibraryIds(paperId);
  managePaper(paperId, oldLibraryIds);
}

function removePaperOnClick(paperId, libraryId) {
  if (libraryId) {
    const libraryName = document.getElementById(`library-checkbox-${libraryId}`).title;
    if (confirm(`Are you sure you want to remove this paper from ${libraryName}?`)) {
      removePaper(paperId, libraryId);
    }
  } else {
    if (confirm("Are you sure you want to remove this paper from all libraries?")) {
      batchRemove(paperId, getOldLibraryIds(paperId));
    }
  }
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
  })
  .then(modifyPaperLibraryList(paperId, libraryIds))
  .catch((err) => {
    console.log(err);
    alert("Error deleting paper!");
  });
}

function removePaper(paperId, libraryId) {
  fetch(`/api/libraries/${libraryId}/papers/${paperId}`, {
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
        name: document.getElementById(`library-checkbox-${libraryId}`).title,
      };
    });
    script.textContent = JSON.stringify(newLibraries);
  }
}
