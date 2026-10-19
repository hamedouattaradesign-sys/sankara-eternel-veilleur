/* SANKARA, L'ÉTERNEL VEILLEUR — comportements communs.
   Repli de la navigation sur petit écran. Sans ce script, la navigation
   reste entièrement visible et utilisable. */
(function () {
  "use strict";

  var bascule = document.querySelector(".bascule");
  var nav = document.getElementById("navigation");
  if (!bascule || !nav) return;

  // LE PLI DOIT ÊTRE LE MÊME QUE CELUI DE LA FEUILLE DE STYLE — 62em.
  // Il a valu 46em pendant un temps, alors que le style ne déplie la
  // navigation qu'à 62em. Entre les deux, c'est-à-dire sur toutes les
  // tablettes et les petits portables, le menu s'affichait déplié par-dessus
  // le contenu, et le bouton annonçait aria-expanded="false" sur une
  // navigation visible — un mensonge pour les lecteurs d'écran.
  // outils/verifier.py refuse désormais que les deux valeurs divergent.
  var PLI = window.matchMedia("(min-width: 62em)");

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
