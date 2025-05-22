document.addEventListener("DOMContentLoaded", () => {
  // Highlight newly added note
  const urlParams = new URLSearchParams(window.location.search);
  const pastedId = urlParams.get("new");
  if (pastedId) {
    const note = document.getElementById(`note-${pastedId}`);
    if (note) {
      note.classList.add("pasted");
    }
  }

  // Handle delete animation
  const deleteButtons = document.querySelectorAll('button[value="Delete"]');
  deleteButtons.forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();

      const form = btn.closest("form");
      const noteDiv = btn.closest(".note");

      if (!form || !noteDiv) {
        console.error("Delete form or note not found.");
        return;
      }

      noteDiv.classList.add("tearing");

      // Wait for animation before submitting
      setTimeout(() => {
        // Add the 'action=Delete' input manually
        const actionInput = document.createElement("input");
        actionInput.type = "hidden";
        actionInput.name = "action";
        actionInput.value = "Delete";
        form.appendChild(actionInput);

        form.submit();
      }, 600);
    });
  });
});
