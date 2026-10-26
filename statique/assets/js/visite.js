/* SANKARA, L'ÉTERNEL VEILLEUR — visite virtuelle.
 *
 * Rotation autour du monument par séquence d'images : aucun WebGL, aucune
 * bibliothèque, aucun modèle 3D à télécharger. Le curseur de rotation est un
 * champ « range » natif : la visite est donc utilisable au clavier et par un
 * lecteur d'écran sans traitement particulier. Le glissement à la souris ou au
 * doigt vient en supplément.
 *
 * Sur connexion lente ou économie de données, seule une vue sur trois est
 * chargée ; le reste est proposé à la demande.
 */
(function () {
  "use strict";

  var vue = document.querySelector("[data-visionneuse]");
  if (!vue) return;

  var image = vue.querySelector("[data-visionneuse-image]");
  var etat = vue.querySelector("[data-visionneuse-etat]");
  var curseur = document.querySelector("[data-visionneuse-curseur]");
  var precedent = document.querySelector('[data-visionneuse-pas="-1"]');
  var suivant = document.querySelector('[data-visionneuse-pas="1"]');
  var complet = document.querySelector("[data-visionneuse-complet]");
  if (!image || !curseur) return;

  var base = vue.getAttribute("data-base");
  var ext = vue.getAttribute("data-ext") || ".webp";
  var pas = parseInt(vue.getAttribute("data-pas"), 10) || 10;
  var gabaritAlt = image.getAttribute("data-alt-gabarit") ||
    "SANKARA, L'ÉTERNEL VEILLEUR, sculpture de Hamed Ouattara, vue à {angle} degrés";

  var angles = [];
  for (var a = 0; a < 360; a += pas) angles.push(a);

  var cache = {};
  var charges = 0;
  var angleCourant = 0;
  var allege = false;

  /* ---------- Adresses et libellés ---------- */

  function adresse(angle) {
    var n = String(angle);
    while (n.length < 3) n = "0" + n;
    return base + n + ext;
  }

  function texteAlt(angle) {
    return gabaritAlt.replace("{angle}", String(angle));
  }

  function annoncer(message) {
    if (etat) etat.textContent = message;
  }

  /* ---------- Chargement ---------- */

  function precharger(angle, ensuite) {
    if (cache[angle]) {
      if (ensuite) ensuite();
      return;
    }
    var pre = new Image();
    pre.decoding = "async";
    pre.onload = pre.onerror = function () {
      cache[angle] = true;
      charges += 1;
      if (ensuite) ensuite();
    };
    pre.src = adresse(angle);
  }

  function plusProcheCharge(angle) {
    // Pendant le chargement, ou en mode allégé, on montre la vue disponible
    // la plus proche plutôt qu'une image vide.
    if (cache[angle]) return angle;
    for (var ecart = pas; ecart <= 180; ecart += pas) {
      var avant = (angle - ecart + 360) % 360;
      var apres = (angle + ecart) % 360;
      if (cache[avant]) return avant;
      if (cache[apres]) return apres;
    }
    return angle;
  }

  function afficher(angle) {
    angleCourant = ((angle % 360) + 360) % 360;
    var rendu = plusProcheCharge(angleCourant);
    var src = adresse(rendu);
    if (image.getAttribute("src") !== src) image.setAttribute("src", src);
    image.setAttribute("alt", texteAlt(angleCourant));
    if (curseur.value !== String(angleCourant)) curseur.value = String(angleCourant);
  }

  function fileDAttente(liste, fini) {
    var i = 0;
    function suite() {
      if (i >= liste.length) {
        if (fini) fini();
        return;
      }
      var angle = liste[i++];
      precharger(angle, function () {
        afficher(angleCourant);
        if (liste.length > 4) {
          annoncer("Chargement de la rotation… " + charges + " / " + total());
        }
        if (window.requestIdleCallback) window.requestIdleCallback(suite, { timeout: 500 });
        else window.setTimeout(suite, 0);
      });
    }
    suite();
  }

  function total() {
    return allege ? Math.ceil(angles.length / 3) : angles.length;
  }

  function instructions() {
    annoncer(
      allege
        ? "Rotation allégée — faites glisser ou utilisez le curseur"
        : "Faites glisser, ou utilisez le curseur et les flèches du clavier"
    );
  }

  /* ---------- Économie de données ---------- */

  var lien = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
  if (lien) {
    var type = lien.effectiveType || "";
    if (lien.saveData === true || type === "slow-2g" || type === "2g") allege = true;
  }

  var aCharger = angles.slice();
  if (allege) {
    aCharger = angles.filter(function (angle, i) { return i % 3 === 0; });
    if (complet) complet.hidden = false;
  }

  // Les quatre faces d'abord : le monument est lisible immédiatement,
  // la rotation se complète ensuite.
  var cardinales = [0, 90, 180, 270].filter(function (angle) {
    return aCharger.indexOf(angle) !== -1;
  });
  var reste = aCharger.filter(function (angle) { return cardinales.indexOf(angle) === -1; });

  annoncer("Chargement de la rotation…");
  fileDAttente(cardinales, function () {
    vue.setAttribute("data-pret", "true");
    fileDAttente(reste, instructions);
  });

  if (complet) {
    complet.addEventListener("click", function () {
      complet.hidden = true;
      allege = false;
      var manquants = angles.filter(function (angle) { return !cache[angle]; });
      fileDAttente(manquants, instructions);
    });
  }

  /* ---------- Curseur, boutons, clavier ---------- */

  curseur.setAttribute("min", "0");
  curseur.setAttribute("max", String(360 - pas));
  curseur.setAttribute("step", String(pas));
  curseur.value = "0";

  curseur.addEventListener("input", function () {
    afficher(parseInt(curseur.value, 10) || 0);
  });

  function tourner(sens) {
    afficher(angleCourant + sens * pas);
  }

  if (precedent) precedent.addEventListener("click", function () { tourner(-1); });
  if (suivant) suivant.addEventListener("click", function () { tourner(1); });

  /* ---------- Glissement ---------- */

  var saisi = false;
  var departX = 0;
  var departAngle = 0;

  function debut(evt) {
    if (evt.button !== undefined && evt.button !== 0) return;
    saisi = true;
    departX = evt.clientX;
    departAngle = angleCourant;
    vue.setAttribute("data-saisi", "true");
    if (vue.setPointerCapture && evt.pointerId !== undefined) {
      try { vue.setPointerCapture(evt.pointerId); } catch (e) { /* sans capture */ }
    }
  }

  function deplacement(evt) {
    if (!saisi) return;
    var largeur = vue.clientWidth || 1;
    // Un balayage de toute la largeur fait un tour complet.
    var degres = ((evt.clientX - departX) / largeur) * 360;
    var cible = Math.round((departAngle + degres) / pas) * pas;
    if (cible !== angleCourant) afficher(cible);
    if (evt.cancelable) evt.preventDefault();
  }

  function fin() {
    if (!saisi) return;
    saisi = false;
    vue.removeAttribute("data-saisi");
  }

  if (window.PointerEvent) {
    vue.addEventListener("pointerdown", debut);
    vue.addEventListener("pointermove", deplacement);
    vue.addEventListener("pointerup", fin);
    vue.addEventListener("pointercancel", fin);
    vue.addEventListener("lostpointercapture", fin);
  } else {
    vue.addEventListener("mousedown", debut);
    window.addEventListener("mousemove", deplacement);
    window.addEventListener("mouseup", fin);
    vue.addEventListener("touchstart", function (evt) { debut(evt.touches[0]); });
    vue.addEventListener("touchmove", function (evt) {
      deplacement({ clientX: evt.touches[0].clientX, cancelable: evt.cancelable,
                    preventDefault: function () { evt.preventDefault(); } });
    });
    vue.addEventListener("touchend", fin);
  }

  // Le glissement ne doit pas déclencher le report d'image par le navigateur.
  vue.addEventListener("dragstart", function (evt) { evt.preventDefault(); });

  afficher(0);
})();
