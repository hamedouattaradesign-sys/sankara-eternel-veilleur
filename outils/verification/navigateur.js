/*
 * Contrôle du site dans un vrai navigateur.
 *
 * Deux séries :
 *   1. chaque page — erreurs de console, ressources manquantes, débordement
 *      horizontal sur écran de 360 px, textes alternatifs, unicité du h1 ;
 *   2. la visite virtuelle — curseur, boutons, clavier, glissement, bouclage,
 *      repli sans JavaScript, mode économie de données.
 *
 * Prérequis : Playwright, et le site servi en local.
 *   python3 outils/build.py
 *   (cd public && python3 -m http.server 8765)
 *   node outils/verification/navigateur.js
 *
 * Retour : 0 si tout passe, 1 sinon.
 */
const { chromium } = require("playwright");

const BASE = process.env.BASE || "http://127.0.0.1:8765";
// Phase 1 : la visite virtuelle et la galerie attendent l'inauguration.
// Les contrôles de la visite ne s'exécutent que si la page est publiée.
const PAGES = ["/", "/oeuvre/", "/nombres/", "/histoire/", "/thomas-sankara/",
               "/artiste/", "/galerie/", "/journal/", "/institutionnel/",
               "/contact/", "/404.html"];

let echecs = 0;
function verifie(nom, condition, detail) {
  console.log(`${condition ? "ok   " : "ÉCHEC"} ${nom}${detail ? " — " + detail : ""}`);
  if (!condition) echecs++;
}

const source = (p) => p.locator("[data-visionneuse-image]").getAttribute("src");
const vue = async (p) => (await source(p)).split("/").pop();

async function controlerPages(navigateur) {
  console.log("— Pages —");
  for (const chemin of PAGES) {
    const ctx = await navigateur.newContext({
      viewport: { width: 360, height: 740 }, isMobile: true, hasTouch: true,
    });
    const p = await ctx.newPage();
    const erreurs = [], casses = [];
    p.on("console", (m) => { if (m.type() === "error") erreurs.push(m.text()); });
    p.on("pageerror", (e) => erreurs.push("JS: " + e.message));
    p.on("response", (r) => { if (r.status() >= 400) casses.push(r.status() + " " + r.url().replace(BASE, "")); });

    await p.goto(BASE + chemin, { waitUntil: "networkidle" });

    const deborde = await p.evaluate(() =>
      document.documentElement.scrollWidth > document.documentElement.clientWidth + 1
        ? document.documentElement.scrollWidth : 0);
    const sansAlt = await p.evaluate(() =>
      [...document.images].filter((i) => !i.getAttribute("alt")).map((i) => i.src.split("/").pop()));
    const h1 = await p.locator("h1").count();

    const detail = [
      deborde ? `déborde à ${deborde}px` : null,
      erreurs.length ? "console : " + erreurs.join(" | ") : null,
      casses.length ? "ressources : " + casses.join(" | ") : null,
      sansAlt.length ? "sans alt : " + sansAlt.join(", ") : null,
      h1 !== 1 ? `${h1} h1` : null,
    ].filter(Boolean).join(" ; ");

    verifie(chemin, !detail, detail);
    await ctx.close();
  }
}

async function visitePubliee(navigateur) {
  const ctx = await navigateur.newContext();
  const p = await ctx.newPage();
  const r = await p.goto(BASE + "/visite/").catch(() => null);
  const publiee = !!r && r.status() === 200;
  await ctx.close();
  return publiee;
}

async function controlerVisite(navigateur) {
  console.log("\n— Visite virtuelle —");
  let ctx = await navigateur.newContext({ viewport: { width: 390, height: 800 }, hasTouch: true });
  let p = await ctx.newPage();
  await p.goto(BASE + "/visite/", { waitUntil: "networkidle" });
  await p.waitForTimeout(2500);                 // rotation entièrement chargée

  const curseur = p.locator("[data-visionneuse-curseur]");
  const regle = async (v) => { await curseur.fill(String(v)); await curseur.dispatchEvent("input"); await p.waitForTimeout(200); };

  await regle(120);
  verifie("le curseur change la vue", (await vue(p)).includes("120"), await vue(p));

  const alt = await p.locator("[data-visionneuse-image]").getAttribute("alt");
  verifie("le texte alternatif suit la rotation et nomme l'auteur",
          alt.includes("120") && alt.includes("Hamed Ouattara"));

  await p.locator('[data-visionneuse-pas="1"]').click();
  await p.waitForTimeout(200);
  verifie("le bouton tourne de dix degrés", (await vue(p)).includes("130"));

  await curseur.focus();
  await p.keyboard.press("ArrowRight");
  await p.waitForTimeout(200);
  verifie("les flèches du clavier tournent le monument", (await vue(p)).includes("140"));

  await regle(350);
  await p.locator('[data-visionneuse-pas="1"]').click();
  await p.waitForTimeout(200);
  verifie("la rotation boucle de 350 à 0", (await vue(p)).includes("000"));

  await regle(180);
  const avant = await vue(p);
  await p.locator("[data-visionneuse]").scrollIntoViewIfNeeded();
  await p.waitForTimeout(150);
  const b = await p.locator("[data-visionneuse]").boundingBox();
  await p.mouse.move(b.x + b.width * 0.5, b.y + b.height * 0.5);
  await p.mouse.down();
  await p.mouse.move(b.x + b.width * 0.85, b.y + b.height * 0.5, { steps: 8 });
  await p.mouse.up();
  await p.waitForTimeout(250);
  verifie("le glissement fait tourner le monument", avant !== (await vue(p)),
          avant + " → " + (await vue(p)));

  // Sur connexion normale, la rotation est déjà entière : proposer de la
  // charger n'aurait pas de sens. L'attribut hidden doit donc tenir, malgré
  // la règle d'affichage portée par la classe .appel.
  verifie("connexion normale : le bouton de chargement reste masqué",
          !(await p.locator("[data-visionneuse-complet]").isVisible()));
  await ctx.close();

  // Sans JavaScript
  ctx = await navigateur.newContext({ javaScriptEnabled: false, viewport: { width: 390, height: 800 } });
  p = await ctx.newPage();
  await p.goto(BASE + "/visite/", { waitUntil: "networkidle" });
  verifie("sans JS : l'image et le repli restent visibles",
          (await p.locator("noscript").count()) > 0 &&
          (await p.locator("[data-visionneuse-image]").isVisible()));
  verifie("sans JS : les commandes inutilisables sont masquées",
          !(await p.locator(".commandes").isVisible()));
  await p.goto(BASE + "/", { waitUntil: "networkidle" });
  verifie("sans JS : la navigation reste entièrement visible",
          (await p.locator(".nav__lien").first().isVisible()) &&
          (await p.locator(".nav__lien").count()) === 10);
  await ctx.close();

  // Économie de données
  ctx = await navigateur.newContext({ viewport: { width: 390, height: 800 } });
  p = await ctx.newPage();
  await p.addInitScript(() => {
    Object.defineProperty(navigator, "connection",
      { get: () => ({ saveData: true, effectiveType: "2g" }) });
  });
  let demandes = 0;
  p.on("request", (r) => { if (/rotation-\d+\.(svg|webp|jpg)/.test(r.url())) demandes++; });
  await p.goto(BASE + "/visite/", { waitUntil: "networkidle" });
  await p.waitForTimeout(2500);
  verifie("économie de données : un tiers des vues seulement", demandes <= 14,
          demandes + " vues sur 36");
  verifie("économie de données : la rotation complète reste proposée",
          await p.locator("[data-visionneuse-complet]").isVisible());
  await ctx.close();
}

(async () => {
  const navigateur = await chromium.launch();
  await controlerPages(navigateur);
  if (await visitePubliee(navigateur)) {
    await controlerVisite(navigateur);
  } else {
    console.log("\n— Visite virtuelle — non publiée (phase 1), contrôles ignorés");
  }
  await navigateur.close();
  console.log(echecs ? `\n${echecs} contrôle(s) en échec` : "\nTous les contrôles passent");
  process.exit(echecs ? 1 : 0);
})();
