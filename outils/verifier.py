#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contrôle le site produit dans public/ sans rien installer.

Vérifie, page par page : l'équilibre des balises, la présence et la longueur
des balises title et meta description, l'unicité du h1, la validité du JSON-LD,
les textes alternatifs, la cohérence des liens internes et des fichiers
référencés, et le port de la ligne de crédit.

Usage :  python3 outils/verifier.py
Retour :  0 si tout passe, 1 sinon.
"""

import json
import os
import re
import sys
from html.parser import HTMLParser

RACINE = os.path.dirname(os.path.abspath(os.path.join(__file__, "..")))
PUBLIC = os.path.join(RACINE, "public")

# Balises sans fermeture en HTML5.
ORPHELINES = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
              "meta", "param", "source", "track", "wbr"}

anomalies = []
avertissements = []


class Structure(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.pile = []
        self.desequilibres = []
        self.h1 = 0
        self.images = []
        self.liens = []
        self.jsonld = []
        self._dans_jsonld = False

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "h1":
            self.h1 += 1
        if tag == "img":
            self.images.append(d)
        if tag == "a" and d.get("href"):
            self.liens.append(d["href"])
        if tag == "script" and d.get("type") == "application/ld+json":
            self._dans_jsonld = True
        if tag not in ORPHELINES:
            self.pile.append(tag)

    def handle_endtag(self, tag):
        if tag in ORPHELINES:
            return
        if tag == "script":
            self._dans_jsonld = False
        if not self.pile:
            self.desequilibres.append("</%s> sans ouverture" % tag)
            return
        if self.pile[-1] == tag:
            self.pile.pop()
        elif tag in self.pile:
            while self.pile and self.pile[-1] != tag:
                self.desequilibres.append("<%s> jamais fermée" % self.pile.pop())
            if self.pile:
                self.pile.pop()
        else:
            self.desequilibres.append("</%s> inattendue" % tag)

    def handle_data(self, data):
        if self._dans_jsonld and data.strip():
            self.jsonld.append(data)


def pages_html():
    for dossier, _, fichiers in os.walk(PUBLIC):
        for nom in sorted(fichiers):
            if nom.endswith(".html"):
                yield os.path.join(dossier, nom)


def chemin_servi(fichier):
    rel = os.path.relpath(fichier, PUBLIC).replace(os.sep, "/")
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("index.html")]
    if rel == "index.html":
        return "/"
    return "/" + rel


def cible_existe(href):
    """Un lien interne doit correspondre à un fichier réellement produit."""
    chemin = href.split("#")[0].split("?")[0]
    if not chemin:
        return True
    local = chemin.lstrip("/")
    direct = os.path.join(PUBLIC, local)
    if os.path.isfile(direct):
        return True
    return os.path.isfile(os.path.join(PUBLIC, local, "index.html"))


def verifier_page(fichier):
    rel = chemin_servi(fichier)
    with open(fichier, encoding="utf-8") as f:
        brut = f.read()

    s = Structure()
    s.feed(brut)
    s.close()

    for souci in s.desequilibres:
        anomalies.append("%s : balises — %s" % (rel, souci))
    if s.pile:
        anomalies.append("%s : balises jamais fermées — %s" % (rel, ", ".join(s.pile)))

    titre = re.search(r"<title>(.*?)</title>", brut, re.DOTALL)
    if not titre or not titre.group(1).strip():
        anomalies.append("%s : title absent" % rel)
    elif len(titre.group(1)) > 75:
        avertissements.append("%s : title de %d caractères, au-delà de 75 il est tronqué "
                              "dans les résultats de recherche" % (rel, len(titre.group(1))))

    desc = re.search(r'<meta name="description" content="(.*?)">', brut, re.DOTALL)
    if not desc or not desc.group(1).strip():
        anomalies.append("%s : meta description absente" % rel)
    else:
        n = len(desc.group(1))
        if n > 165:
            avertissements.append("%s : meta description de %d caractères, "
                                  "au-delà de 165 elle est tronquée" % (rel, n))

    if s.h1 != 1:
        anomalies.append("%s : %d balises h1, il en faut exactement une" % (rel, s.h1))

    if '<link rel="canonical"' not in brut:
        anomalies.append("%s : lien canonique absent" % rel)

    for bloc in s.jsonld:
        try:
            charge = json.loads(bloc)
        except json.JSONDecodeError as err:
            anomalies.append("%s : JSON-LD invalide — %s" % (rel, err))
            continue
        if "@context" not in charge:
            anomalies.append("%s : JSON-LD sans @context" % rel)

    for img in s.images:
        # Un alt vide n'est correct que si l'image est explicitement déclarée
        # décorative ; sinon c'est un oubli.
        decorative = img.get("aria-hidden") == "true" or img.get("role") == "presentation"
        if not img.get("alt", "").strip() and not decorative:
            anomalies.append("%s : image sans texte alternatif — %s"
                             % (rel, img.get("src", "?")))
        if "alt" not in img and decorative:
            anomalies.append("%s : image décorative sans attribut alt — %s"
                             % (rel, img.get("src", "?")))
        if not (img.get("width") and img.get("height")):
            avertissements.append("%s : image sans width/height, la page sautera au "
                                  "chargement — %s" % (rel, img.get("src", "?")))

    for href in s.liens:
        if href.startswith(("http://", "https://", "mailto:", "tel:", "#")):
            continue
        if not cible_existe(href):
            anomalies.append("%s : lien interne cassé — %s" % (rel, href))

    # Une image absente ne se voit pas dans le code : elle se voit sur la page,
    # trop tard. On la cherche ici.
    for img in s.images:
        src = img.get("src", "")
        if not src or src.startswith(("http://", "https://", "data:")):
            continue
        if not cible_existe(src):
            anomalies.append("%s : image introuvable — %s" % (rel, src))

    # Le pied de page porte la mention obligatoire de l'auteur sur chaque page.
    if "Hamed Ouattara" not in brut:
        anomalies.append("%s : le nom de l'auteur ne figure pas sur la page" % rel)

    return rel


def verifier_fichiers_annexes():
    for attendu in ("sitemap.xml", "robots.txt", "404.html",
                    "assets/css/site.css", "assets/js/site.js",
                    "assets/img/favicon.svg",
                    "assets/img/partage/og-sankara-eternel-veilleur.png",
                    "assets/presse/dossier-de-presse-sankara-eternel-veilleur.pdf"):
        if not os.path.isfile(os.path.join(PUBLIC, attendu)):
            anomalies.append("fichier attendu absent — %s" % attendu)

    # Ce que seule la visite virtuelle emploie n'est exigé que si elle est
    # publiée : en phase 1, elle attend dans _phase2/.
    if not any("visite.js" in open(f, encoding="utf-8").read() for f in pages_html()):
        return
    if not os.path.isfile(os.path.join(PUBLIC, "assets", "js", "visite.js")):
        anomalies.append("fichier attendu absent — assets/js/visite.js")

    # Les trente-six vues de la rotation ne sont exigées que si une page les
    # emploie : en phase 1, la visite virtuelle n'est pas publiée.
    emploie_rotation = any(
        "rotation-" in open(f, encoding="utf-8").read() for f in pages_html()
    )
    if not emploie_rotation:
        return
    manquantes = [a for a in range(0, 360, 10)
                  if not os.path.isfile(os.path.join(PUBLIC, "assets", "img", "visite",
                                                     "rotation-%03d.svg" % a))
                  and not os.path.isfile(os.path.join(PUBLIC, "assets", "img", "visite",
                                                      "rotation-%03d.webp" % a))]
    if manquantes:
        anomalies.append("vues de rotation manquantes — %s"
                         % ", ".join("%03d" % a for a in manquantes))


def main():
    if not os.path.isdir(PUBLIC):
        print("public/ est absent : lancez d'abord python3 outils/build.py")
        return 1

    pages = list(pages_html())
    for fichier in pages:
        verifier_page(fichier)
    verifier_fichiers_annexes()

    for a in avertissements:
        print("  avertissement  %s" % a)
    for a in anomalies:
        print("  ANOMALIE       %s" % a)

    print("\n%d pages contrôlées, %d anomalie(s), %d avertissement(s)"
          % (len(pages), len(anomalies), len(avertissements)))
    return 1 if anomalies else 0


if __name__ == "__main__":
    sys.exit(main())
