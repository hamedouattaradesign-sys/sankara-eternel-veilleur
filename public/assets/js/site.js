/* SANKARA, L'ÉTERNEL VEILLEUR — comportements communs.
   Repli de la navigation sur petit écran. Sans ce script, la navigation
   reste entièrement visible et utilisable. */
(function () {
  "use strict";

  var bascule = document.querySelector(".bascule");
  var nav = document.getElementById("navigation");
  if (!bascule || !nav) return;

  var PLI = window.matchMedia("(min-width: 46em)");

  function replier(replie) {
    nav.setAttribute("data-ouvert", replie ? "false" : "true");
    bascule.setAttribute("aria-expanded", replie ? "false" : "true");
  }

  function ajuster() {
    // Au-delà du pli, la feuille de style déplie la navigation ;
    // on remet l'attribut à plat pour que l'état reste cohérent.
    if (PLI.matches) {
      nav.setAttribute("data-ouvert", "true");
      bascule.setAttribute("aria-expanded", "false");
    } else {
      replier(true);
    }
  }

  bascule.addEventListener("click", function () {
    replier(bascule.getAttribute("aria-expanded") === "true");
  });

  document.addEventListener("keydown", function (evt) {
    if (evt.key === "Escape" && bascule.getAttribute("aria-expanded") === "true") {
      replier(true);
      bascule.focus();
    }
  });

  if (PLI.addEventListener) PLI.addEventListener("change", ajuster);
  else if (PLI.addListener) PLI.addListener(ajuster);

  ajuster();
})();
