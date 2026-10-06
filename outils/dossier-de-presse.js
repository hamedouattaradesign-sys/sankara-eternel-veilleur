/* Produit statique/assets/presse/dossier-de-presse-sankara-eternel-veilleur.pdf
   à partir de outils/presse/dossier-de-presse.html.

   Usage :  node outils/dossier-de-presse.js
   Nécessite Playwright (Chromium). Le PDF produit est versionné : il n'est donc
   pas nécessaire de régénérer pour déployer, seulement pour mettre à jour. */
const { chromium } = require("playwright");
const path = require("path");

(async () => {
  const racine = path.resolve(__dirname, "..");
  const source = "file://" + path.join(racine, "outils", "presse", "dossier-de-presse.html");
  const cible = path.join(racine, "statique", "assets", "presse",
                          "dossier-de-presse-sankara-eternel-veilleur.pdf");

  const navigateur = await chromium.launch();
  const page = await navigateur.newPage();
  await page.goto(source, { waitUntil: "networkidle" });
  await page.pdf({ path: cible, format: "A4", printBackground: true });
  await navigateur.close();
  console.log("Dossier de presse : " + path.relative(racine, cible));
})();
