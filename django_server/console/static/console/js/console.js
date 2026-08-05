/*
 * Progressive-enhancement layer for the action grid: intercepts the two
 * per-feature forms (trigger / schedule) and swaps the server-rendered
 * partial back in, instead of a full page reload. Deliberately vanilla —
 * no JS dependency to vendor or pin for one internal admin tool.
 */
(function () {
  function getCookie(name) {
    const match = document.cookie.match(new RegExp("(^|; )" + name + "=([^;]*)"));
    return match ? decodeURIComponent(match[2]) : "";
  }

  document.addEventListener("submit", async function (event) {
    const form = event.target.closest("form[data-ajax-row-form]");
    if (!form) return;
    event.preventDefault();

    const row = form.closest("[data-action-row]");
    const submitBtn = form.querySelector("button[type=submit]");
    if (submitBtn) submitBtn.disabled = true;

    try {
      const response = await fetch(form.action, {
        method: "POST",
        headers: { "X-CSRFToken": getCookie("csrftoken") },
        body: new FormData(form),
      });
      if (row && response.ok) {
        row.outerHTML = await response.text();
      } else if (submitBtn) {
        submitBtn.disabled = false;
      }
    } catch (err) {
      if (submitBtn) submitBtn.disabled = false;
      console.error("Console action request failed:", err);
    }
  });
})();
