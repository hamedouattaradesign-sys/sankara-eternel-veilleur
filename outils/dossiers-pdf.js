/* Produit les dossiers PDF de statique/assets/presse/, dans les trois langues.

   Usage :  node outils/dossiers-pdf.js          toutes les sorties
            node outils/dossiers-pdf.js it       une seule langue

   Le dossier institutionnel français n'est PAS produit ici : c'est l'original
   signé de la main de l'auteur, daté du 17 août 2026, déposé tel quel dans
   statique/assets/presse/. Les versions italienne et anglaise en sont des
   traductions, et le disent en tête et en pied : en cas de divergence, c'est
   l'original français qui fait foi.

   La planche des faces est tracée à la demande par outils/planche-faces.py et
   injectée à la place du commentaire <!--PLANCHE-->. Elle ne peut donc pas se
   désynchroniser des cotes : il n'y a qu'une seule source pour le dessin.

   Les PDF produits sont versionnés : il n'est pas nécessaire de les régénérer
   pour déployer, seulement pour les mettre à jour.

   Nécessite Playwright (Chromium) et Python 3. */

const { chromium } = require("playwright");
const { execFileSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const racine = path.resolve(__dirname, "..");
const presse = path.join(racine, "outils", "presse");
const sortie = path.join(racine, "statique", "assets", "presse");

/* Le nom du fichier est dans la langue du lecteur : ce qu'il télécharge arrive
   dans son dossier sous un nom qu'il comprend. Les deux documents français
   gardent leur nom d'origine, déjà cité ailleurs. */
const DOSSIERS = [
  { source: "presse-fr.html",          cible: "dossier-de-presse-sankara-eternel-veilleur.pdf",       langue: "fr" },
  { source: "presse-it.html",          cible: "dossier-stampa-sankara-eternel-veilleur-it.pdf",      langue: "it" },
  { source: "presse-en.html",          cible: "press-kit-sankara-eternel-veilleur-en.pdf",            langue: "en" },
  { source: "institutionnel-it.html",  cible: "dossier-istituzionale-sankara-eternel-veilleur-it.pdf", langue: "it" },
  { source: "institutionnel-en.html",  cible: "institutional-dossier-sankara-eternel-veilleur-en.pdf", langue: "en" },
];

/* La planche, tracée par le script qui porte les cotes et les assertions. */
function planche(langue) {
  return execFileSync("python3", [path.join(racine, "outils", "planche-faces.py"), langue],
                      { encoding: "utf-8", maxBuffer: 4 << 20 });
}

(async () => {
  const demandee = process.argv[2];
  const liste = demandee ? DOSSIERS.filter((d) => d.langue === demandee) : DOSSIERS;
  if (liste.length === 0) {
    console.error("Langue inconnue : " + demandee + ". Attendu fr, it ou en.");
    process.exit(1);
  }

  const navigateur = await chromium.launch();
  const page = await navigateur.newPage();

  for (const dossier of liste) {
    const chemin = path.join(presse, dossier.source);
    let html = fs.readFileSync(chemin, "utf-8");

    /* Fichier temporaire à côté de la source, pour que dossier.css et sho.png
       restent accessibles en chemin relatif. */
    let servi = chemin;
    if (html.includes("<!--PLANCHE-->")) {
      html = html.replace("<!--PLANCHE-->", planche(dossier.langue));
      servi = path.join(presse, ".rendu-" + dossier.source);
      fs.writeFileSync(servi, html, "utf-8");
    }

    try {
      await page.goto("file://" + servi, { waitUntil: "networkidle" });
      await page.pdf({ path: path.join(sortie, dossier.cible), format: "A4", printBackground: true });
    } finally {
      if (servi !== chemin) fs.unlinkSync(servi);
    }

    const octets = fs.statSync(path.join(sortie, dossier.cible)).size;
    console.log("  " + dossier.cible + "  " + Math.round(octets / 1024) + " Ko");
  }

  await navigateur.close();
})();
