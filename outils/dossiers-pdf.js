/* Produit les dossiers PDF de statique/assets/presse/, dans les trois langues.

   Usage :  node outils/dossiers-pdf.js          toutes les sorties
            node outils/dossiers-pdf.js it       une seule langue

   Les six dossiers sont produits ici. Le dossier institutionnel français en est
   la deuxième édition : la première, signée le 17 août 2026, portait un
   comptage faux — onze rangées, 144 bossages — et a été retirée du site. Elle
   est conservée, non publiée, dans outils/presse/archive/. La deuxième édition
   attend la signature de l'auteur : une zone de paraphe lui est réservée.

   Les versions italienne et anglaise sont des traductions de cette deuxième
   édition, et le disent en tête : en cas de divergence, c'est le français qui
   fait foi.

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
  { source: "institutionnel-fr.html",  cible: "dossier-institutionnel-sankara-eternel-veilleur.pdf",  langue: "fr" },
  { source: "presse-fr.html",          cible: "dossier-de-presse-sankara-eternel-veilleur.pdf",       langue: "fr" },
  { source: "presse-it.html",          cible: "dossier-stampa-sankara-eternel-veilleur-it.pdf",      langue: "it" },
  { source: "presse-en.html",          cible: "press-kit-sankara-eternel-veilleur-en.pdf",            langue: "en" },
  { source: "institutionnel-it.html",  cible: "dossier-istituzionale-sankara-eternel-veilleur-it.pdf", langue: "it" },
  { source: "institutionnel-en.html",  cible: "institutional-dossier-sankara-eternel-veilleur-en.pdf", langue: "en" },
  /* Le cartel au code QR : A5, trilingue, à imprimer et à poser près de
     l'œuvre ou à distribuer. Le code est tracé par outils/qr.py — aucun
     générateur en ligne : une adresse confiée à un tiers, c'est un tiers qui
     la compte, parfois la redirige, et peut cesser d'exister. */
  { source: "cartel-qr.html", cible: "cartel-qr-sankara-eternel-veilleur.pdf",
    langue: "fr", format: "A5" },
  /* La même chose, avec les armoiries du Burkina Faso et la bande des
     partenaires. Le cartel sobre reste : près de l'œuvre, un cartel de musée
     ne porte pas de logos ; sur un stand ou dans un dossier, celui-ci dit qui
     porte le projet.

     PROVISOIRE — il n'est pas publié sur le site, et sa sortie reste dans
     outils/presse/. Sa bande vient de l'invitation de l'Ambassade, et
     l'auteur a signalé que le logo du CIM-TS qui y figure est une ancienne
     version. Manquent aussi le Musée National du Burkina Faso et la
     communauté burkinabè d'Italie. Le jour où ces trois fichiers arrivent,
     la bande est refaite, `sortie` disparaît et le lien revient sur la page
     Institutions, dans les trois langues. */
  { source: "cartel-qr-institutions.html",
    cible: "cartel-qr-institutions-sankara-eternel-veilleur.pdf",
    langue: "fr", format: "A5", sortie: presse },
];

/* L'adresse que porte le code. Elle est écrite ici une seule fois, et le
   cartel l'imprime aussi en toutes lettres : qui ne scanne pas doit pouvoir
   la recopier. */
const ADRESSE = "https://sankara.hamedouattara.com";

/* Le fond du code est celui du papier du cartel, et non du blanc : le carré
   blanc posé sur la crème se voyait de loin et cassait la page. Le contraste
   avec l'encre reste très au-dessus de ce qu'un téléphone demande, et le
   contrôle relit le PDF rendu pour s'en assurer. */
const PAPIER = "#fbf8f2";

function codeQR() {
  return execFileSync("python3",
                      [path.join(racine, "outils", "qr.py"), ADRESSE, "Q", PAPIER],
                      { encoding: "utf-8", maxBuffer: 1 << 20 });
}

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
    let injecte = false;
    if (html.includes("<!--PLANCHE-->")) {
      html = html.replace("<!--PLANCHE-->", planche(dossier.langue));
      injecte = true;
    }
    if (html.includes("<!--QR-->")) {
      html = html.replace("<!--QR-->", codeQR());
      injecte = true;
    }
    if (injecte) {
      servi = path.join(presse, ".rendu-" + dossier.source);
      fs.writeFileSync(servi, html, "utf-8");
    }

    try {
      await page.goto("file://" + servi, { waitUntil: "networkidle" });
      await page.pdf({ path: path.join(dossier.sortie || sortie, dossier.cible),
                       format: dossier.format || "A4", printBackground: true });
    } finally {
      if (servi !== chemin) fs.unlinkSync(servi);
    }

    const octets = fs.statSync(path.join(dossier.sortie || sortie, dossier.cible)).size;
    console.log("  " + dossier.cible + "  " + Math.round(octets / 1024) + " Ko"
                + (dossier.sortie ? "  (non publié)" : ""));
  }

  await navigateur.close();
})();
