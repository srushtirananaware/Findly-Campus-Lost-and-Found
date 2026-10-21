
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-confirm]").forEach((form) => {
    form.addEventListener("submit", (event) => {
      const message = form.getAttribute("data-confirm") || "Are you sure?";
      if (!window.confirm(message)) event.preventDefault();
    });
  });
  document.querySelectorAll("[data-dismiss]").forEach((button) => {
    button.addEventListener("click", () => button.closest(".notice")?.remove());
  });
  const photoInput = document.querySelector("#id_photo");
  if (photoInput) {
    photoInput.addEventListener("change", () => {
      const file = photoInput.files?.[0];
      const preview = document.querySelector("#photo-preview");
      if (!preview || !file) return;
      if (!file.type.startsWith("image/")) return;
      preview.src = URL.createObjectURL(file);
      preview.hidden = false;
    });
  }
});
