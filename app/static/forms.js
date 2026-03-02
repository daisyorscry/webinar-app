(function () {
  function toggleVisibility(button) {
    var targetId = button.getAttribute("data-target");
    if (!targetId) return;
    var input = document.getElementById(targetId);
    if (!input) return;
    var isPassword = input.getAttribute("type") === "password";
    input.setAttribute("type", isPassword ? "text" : "password");
    button.setAttribute("aria-pressed", String(isPassword));
    var icon = button.querySelector("i");
    if (icon) {
      icon.classList.toggle("fa-eye", !isPassword);
      icon.classList.toggle("fa-eye-slash", isPassword);
    }
  }

  document.addEventListener("click", function (event) {
    var button = event.target.closest("[data-toggle-password]");
    if (!button) return;
    event.preventDefault();
    toggleVisibility(button);
  });
})();
