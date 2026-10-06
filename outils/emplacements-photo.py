#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crée les EMPLACEMENTS des visuels attendus.

Chaque emplacement est un cadre sombre portant le libellé du visuel demandé.
Il tient la place de l'image et sert en même temps de liste de ce qu'il faut
fournir. Dès qu'un visuel arrive, on dépose le fichier WebP au même nom dans le
même dossier et on retire le .svg correspondant.

PHASE 1, avant l'inauguration : maquettes, rendus, plans, portrait vectoriel,
fabrication en atelier, et images d'archive du Camarade Président Thomas
Sankara dont l'auteur détient les droits.

Usage :  python3 outils/emplacements-photo.py
"""

import os
import textwrap

RACINE = os.path.dirname(os.path.abspath(os.path.join(__file__, "..")))
IMAGES = os.path.join(RACINE, "statique", "assets", "img")

# (dossier, nom de fichier, légende, orientation)
VISUELS = [
    # Maquettes et rendus du projet
    ("maquettes", "01-rendu-ensemble",
     "Rendu du monument dans le Parco Thomas Sankara", "paysage"),
    ("maquettes", "02-rendu-face-portrait",
     "Rendu de la face portrait, à hauteur de regard", "portrait"),
    ("maquettes", "03-rendu-face-texture",
     "Rendu d'une face de texture, bossages lisibles", "portrait"),
    ("maquettes", "04-rendu-detail-decoupe",
     "Rendu, détail de la découpe du visage à contre-jour", "paysage"),

    # Plans et dessins de conception
    ("maquettes", "05-planche-deux-faces",
     "La planche illustrative des deux faces", "paysage"),
    ("maquettes", "06-plan-socle",
     "Plan du socle de béton armé à gradins", "paysage"),
    ("maquettes", "07-portrait-vectoriel",
     "Le portrait vectoriel de la découpe traversante", "portrait"),

    # Fabrication en atelier
    ("maquettes", "08-atelier-decoupe",
     "Fabrication : la découpe de la tôle d'acier Corten", "paysage"),
    ("maquettes", "09-atelier-emboutissage",
     "Fabrication : l'emboutissage des bossages à la presse", "paysage"),
    ("maquettes", "10-atelier-assemblage",
     "Fabrication : l'assemblage du prisme", "paysage"),

    # L'auteur
    ("maquettes", "11-artiste",
     "Hamed Ouattara, auteur de l'œuvre", "portrait"),

    # Archives — droits détenus par l'auteur, crédit à porter sous l'image
    ("archives", "01-thomas-sankara",
     "Le Camarade Président Thomas Sankara", "portrait"),
]

COTES = {"portrait": (900, 1200), "paysage": (1200, 900)}


def champ_de_bossages(larg, haut):
    """Fond d'attente de la bannière : une trame de bossages à peine marquée.
    Sans texte — le libellé transparaîtrait sous le voile de la bannière."""
    points = []
    pas = 64
    for y in range(pas // 2, haut, pas):
        for x in range(pas // 2, larg, pas):
            points.append('<circle cx="%d" cy="%d" r="9" fill="#2a2520"/>' % (x, y))
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
        'role="img" aria-label="Emplacement réservé : rendu du monument dans le Parco Thomas '
        'Sankara. Visuel à venir.">\n'
        "<title>Emplacement réservé : rendu du monument. Visuel à venir.</title>\n"
        '<rect width="%d" height="%d" fill="#1f1c18"/>\n%s\n</svg>\n'
        % (larg, haut, larg, haut, larg, haut, "\n".join(points))
    )


def emplacement(legende, orientation, index):
    larg, haut = COTES[orientation]
    lignes = textwrap.wrap(legende, 34)
    depart = haut / 2.0 - (len(lignes) - 1) * 26 / 2.0 + 58
    texte = [
        '<text x="%d" y="%.0f" text-anchor="middle" font-size="30" fill="#5c564d" '
        'font-family="system-ui, sans-serif">%s</text>'
        % (larg // 2, depart + i * 38, ligne.replace("&", "&amp;").replace("<", "&lt;"))
        for i, ligne in enumerate(lignes)
    ]
    alt = "Emplacement réservé : %s. Visuel à venir." % legende
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
        'role="img" aria-label="%s">\n'
        "<title>%s</title>\n"
        '<rect width="%d" height="%d" fill="#f1ebe0"/>\n'
        '<rect x="12" y="12" width="%d" height="%d" fill="none" stroke="#ddd5c7" '
        'stroke-width="2" stroke-dasharray="14 10"/>\n'
        '<text x="%d" y="%.0f" text-anchor="middle" font-size="86" fill="#ddd5c7" '
        'font-family="system-ui, sans-serif" font-weight="700">%02d</text>\n'
        '<text x="%d" y="%.0f" text-anchor="middle" font-size="22" fill="#8a4f2b" '
        'font-family="system-ui, sans-serif" letter-spacing="3">VISUEL ATTENDU</text>\n'
        "%s\n</svg>\n"
        % (larg, haut, larg, haut, alt, alt, larg, haut, larg - 24, haut - 24,
           larg // 2, haut / 2.0 - 92, index,
           larg // 2, haut / 2.0 - 10,
           "\n".join(texte))
    )


def main():
    compteurs = {}
    for dossier, nom, legende, orientation in VISUELS:
        cible = os.path.join(IMAGES, dossier)
        os.makedirs(cible, exist_ok=True)
        compteurs[dossier] = compteurs.get(dossier, 0) + 1
        larg, haut = COTES[orientation]
        # Le rendu d'ensemble sert de fond à la bannière d'accueil : pas de texte.
        contenu = (champ_de_bossages(larg, haut) if nom == "01-rendu-ensemble"
                   else emplacement(legende, orientation, compteurs[dossier]))
        with open(os.path.join(cible, nom + ".svg"), "w", encoding="utf-8") as f:
            f.write(contenu)
    for dossier, n in sorted(compteurs.items()):
        print("%2d emplacements dans statique/assets/img/%s" % (n, dossier))


if __name__ == "__main__":
    main()
