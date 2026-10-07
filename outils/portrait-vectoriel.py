#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vectorise le portrait découpé, d'après le plan de fabrication de l'auteur.

La source est `statique/assets/img/oeuvre/05-plan-face-portrait.webp`, extraite
du plan FACE PORTRAIT INDICE E du Studio Hamed Ouattara. C'est le pochoir exact
découpé au laser dans la tôle : pas une photographie du Camarade Président, pas
une interprétation, mais la forme que porte le monument.

Elle sert deux choses :
  — la marque du site, à côté du titre, en tête de chaque page ;
  — l'icône d'onglet et l'icône d'écran d'accueil.

Usage :  python3 outils/portrait-vectoriel.py
"""

import os
import sys

import numpy as np
import potrace
from PIL import Image

RACINE = os.path.dirname(os.path.abspath(os.path.join(__file__, "..")))
PLAN = os.path.join(RACINE, "statique", "assets", "img", "oeuvre",
                    "05-plan-face-portrait.webp")
SORTIE = os.path.join(RACINE, "statique", "assets", "img", "identite")

# Cadre du visage dans le plan, en proportions de l'image. Relevé à la main :
# le plan porte aussi les bossages, les cotes et le bloc du nom, qu'il faut
# écarter. Si le plan est un jour remplacé, c'est cette ligne à reprendre.
CADRE = (0.292, 0.143, 0.578, 0.338)

SEUIL = 128          # le plan est déjà en noir et blanc franc
ALPHAMAX = 1.0       # arrondi des coins : 1.0 suit le pochoir de près
OPTTOLERANCE = 0.2   # tolérance de simplification des courbes


def tracer():
    im = Image.open(PLAN).convert("L")
    L, H = im.size
    x0, y0, x1, y1 = CADRE
    visage = im.crop((int(L * x0), int(H * y0), int(L * x1), int(H * y1)))

    # Le pochoir est noir sur blanc, et les zones NOIRES sont les vides
    # traversants de la tôle : ce sont elles qu'il faut tracer.
    #
    # ATTENTION, le sens est contre-intuitif : potrace remplit les pixels à
    # FAUX, pas à vrai. On lui passe donc le masque du blanc pour obtenir le
    # noir. Passer le masque du noir produit le négatif — un rectangle plein
    # avec le visage en réserve —, et cela se voit tout de suite.
    pixels = np.array(visage)
    encre = pixels < SEUIL
    if not encre.any():
        raise SystemExit("Le cadre ne contient aucun noir : CADRE est à revoir.")
    if encre.mean() > 0.75:
        raise SystemExit(
            "Le cadre est noir à %.0f %% : il déborde du pochoir, ou le seuil "
            "est trop haut. CADRE ou SEUIL est à revoir." % (encre.mean() * 100))
    masque = pixels >= SEUIL

    # Bornes de l'encre, pour cadrer sans deviner.
    lignes = np.where(encre.any(axis=1))[0]
    colonnes = np.where(encre.any(axis=0))[0]
    bornes = (int(colonnes[0]), int(lignes[0]),
              int(colonnes[-1]) + 1, int(lignes[-1]) + 1)

    # turdsize écarte les taches minuscules. Le cadre attrape les pointes des
    # flèches de cote du plan, qui font quelques pixels : 40 les supprime sans
    # toucher aux détails du visage, dont le plus fin — la pupille — en fait
    # plusieurs centaines.
    chemins = potrace.Bitmap(masque).trace(
        turdsize=40, alphamax=ALPHAMAX, opttolerance=OPTTOLERANCE)

    l, h = visage.size

    def pt(p):
        return (p.x, p.y)

    d = []
    for courbe in chemins:
        d.append("M%.1f %.1f" % pt(courbe.start_point))
        for seg in courbe:
            if seg.is_corner:
                d.append("L%.1f %.1f L%.1f %.1f" % (pt(seg.c) + pt(seg.end_point)))
            else:
                d.append("C%.1f %.1f %.1f %.1f %.1f %.1f"
                         % (pt(seg.c1) + pt(seg.c2) + pt(seg.end_point)))
        d.append("Z")
    return l, h, " ".join(d), bornes


def ecrire(nom, contenu):
    chemin = os.path.join(SORTIE, nom)
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)
    return os.path.getsize(chemin)


if __name__ == "__main__":
    os.makedirs(SORTIE, exist_ok=True)
    l, h, d, bornes = tracer()

    # 1. La marque de l'en-tête : le portrait cadré sur la tête, en courant
    #    d'encre pour qu'il prenne la couleur du texte. aria-hidden : le titre
    #    « SANKARA » qui le suit dit déjà ce qu'il faut à un lecteur d'écran,
    #    et répéter le nom ferait doublon à la lecture.
    x0, y0, x1, y1 = bornes
    marge = (x1 - x0) * 0.04
    marque = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="%.1f %.1f %.1f %.1f" '
        'fill="currentColor" role="img" aria-hidden="true">\n'
        '  <path d="%s"/>\n</svg>\n'
        % (x0 - marge, y0 - marge,
           (x1 - x0) + 2 * marge, (y1 - y0) + 2 * marge, d))
    print("marque   %6.1f Ko" % (ecrire("portrait.svg", marque) / 1024))

    # 2. L'icône d'onglet. Un favicon se regarde à seize pixels : à cette
    #    taille, le portrait entier devient une tache. On cadre donc sur le
    #    haut du visage — le béret, l'étoile, les yeux —, qui est la partie
    #    qui se reconnaît même minuscule, et on laisse le menton déborder.
    #    Les proportions du cadre sont relevées sur l'encre, non devinées.
    x0, y0, x1, y1 = bornes
    largeur = x1 - x0
    #    Un carré de la largeur de la tête, aligné sur le sommet du béret.
    marge = largeur * 0.08
    cx0 = x0 - marge
    cy0 = y0 - marge
    cote = largeur + 2 * marge
    icone = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="%.1f %.1f %.1f %.1f" '
        'role="img" aria-label="SANKARA, L\'ÉTERNEL VEILLEUR">\n'
        '  <rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#8a4f2b"/>\n'
        '  <path d="%s" fill="#1c1a17"/>\n</svg>\n'
        % (cx0, cy0, cote, cote, cx0, cy0, cote, cote, d))
    print("icône    %6.1f Ko" % (ecrire("../favicon.svg", icone) / 1024))
