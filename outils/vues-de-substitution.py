#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Génère les vues de SUBSTITUTION de la visite virtuelle.

Ces images ne sont pas l'œuvre : ce sont des schémas volumétriques qui tiennent
la place des photographies, afin que la rotation soit vérifiable avant la
campagne photographique de Rome. Elles seront remplacées par les photographies
réelles, au même nommage, dès qu'elles seront disponibles.

Usage :  python3 outils/vues-de-substitution.py
Sortie :  _phase2/statique/assets/img/visite/rotation-000.svg … rotation-350.svg
"""

import math
import os

RACINE = os.path.dirname(os.path.abspath(os.path.join(__file__, "..")))
# La visite virtuelle attend l'inauguration : ses images vivent dans _phase2/,
# hors du dossier publié. Voir _phase2/LISEZ-MOI.md.
SORTIE = os.path.join(RACINE, "_phase2", "statique", "assets", "img", "visite")

PAS = 10                     # degrés entre deux vues
ELEVATION = 10               # hauteur du point de vue, en degrés

# Cotes réelles de l'œuvre, en centimètres (hors socle).
LARGEUR, PROFONDEUR, HAUTEUR = 70, 70, 200
SOCLE = [(104, 18), (88, 14), (76, 10)]   # (largeur, hauteur) par gradin

# Bossages : 4 colonnes pour les 4 années de la Révolution,
# 12 rangées sur les faces de texture pour les 12 compagnons.
COLONNES, RANGEES_TEXTURE, RANGEES_PORTRAIT = 4, 12, 7

ECHELLE = 1.32
CENTRE_X = 150.0
SOL_Y = 372.0

CORTEN_CLAIR = "#a9643c"
CORTEN = "#8a4f2b"
CORTEN_SOMBRE = "#5f3620"
CORTEN_SOMMET = "#6f4226"
BETON = "#3a3732"
BETON_SOMBRE = "#2b2825"
CREUX = "#141311"
BOSSAGE_LUMIERE = "#cf9166"


def projeter(x, y, z, angle):
    """Rotation autour de l'axe vertical, puis projection orthographique."""
    t = math.radians(angle)
    xr = x * math.cos(t) + z * math.sin(t)
    zr = -x * math.sin(t) + z * math.cos(t)
    p = math.radians(ELEVATION)
    ex = xr
    ey = -(y * math.cos(p)) + zr * math.sin(p)
    return (CENTRE_X + ex * ECHELLE, SOL_Y + ey * ECHELLE)


def normale_visible(nx, nz, angle):
    """Une face est visible si sa normale tournée pointe vers l'observateur."""
    t = math.radians(angle)
    return (-nx * math.sin(t) + nz * math.cos(t)) > 0.015


def point_sur_face(face, u, v, angle):
    """(u, v) dans [0,1]² sur une face → coordonnées écran.
    u va de gauche à droite de la face, v de bas en haut."""
    dx, dz = LARGEUR / 2.0, PROFONDEUR / 2.0
    y = v * HAUTEUR
    if face == "+z":
        return projeter(-dx + u * LARGEUR, y, dz, angle)
    if face == "-z":
        return projeter(dx - u * LARGEUR, y, -dz, angle)
    if face == "+x":
        return projeter(dx, y, dz - u * PROFONDEUR, angle)
    return projeter(-dx, y, -dz + u * PROFONDEUR, angle)


FACES = {
    "+z": (0.0, 1.0, "portrait"),
    "-z": (0.0, -1.0, "portrait"),
    "+x": (1.0, 0.0, "texture"),
    "-x": (-1.0, 0.0, "texture"),
}


def quadrilatere(face, angle, remplissage):
    coins = [
        point_sur_face(face, 0.0, 0.0, angle),
        point_sur_face(face, 1.0, 0.0, angle),
        point_sur_face(face, 1.0, 1.0, angle),
        point_sur_face(face, 0.0, 1.0, angle),
    ]
    points = " ".join("%.2f,%.2f" % p for p in coins)
    return '<polygon points="%s" fill="%s"/>' % (points, remplissage)


def eclairement(face, angle):
    """Teinte de la face selon son orientation : volume lisible d'un coup d'œil."""
    nx, nz, _ = FACES[face]
    t = math.radians(angle)
    xr = -nx * math.sin(t) + nz * math.cos(t)
    yr = nx * math.cos(t) + nz * math.sin(t)
    # Lumière venant de la gauche et de l'avant.
    intensite = max(0.0, 0.62 * xr + 0.48 * -yr)
    if intensite > 0.52:
        return CORTEN_CLAIR
    if intensite > 0.2:
        return CORTEN
    return CORTEN_SOMBRE


def bossages(face, angle, rangees, haut, bas):
    """Grille de bossages hémisphériques, projetée sur la face."""
    morceaux = []
    for colonne in range(COLONNES):
        u = (colonne + 0.5) / COLONNES
        for rangee in range(rangees):
            v = bas + (rangee + 0.5) / rangees * (haut - bas)
            x, y = point_sur_face(face, u, v, angle)
            # Le bossage s'aplatit quand la face se présente de biais.
            gauche = point_sur_face(face, 0.0, v, angle)
            droite = point_sur_face(face, 1.0, v, angle)
            largeur_vue = abs(droite[0] - gauche[0]) / max(COLONNES, 1)
            rx = max(0.35, min(3.0, largeur_vue * 0.26))
            morceaux.append(
                '<ellipse cx="%.2f" cy="%.2f" rx="%.2f" ry="2.2" fill="%s" '
                'fill-opacity="0.50"/>' % (x + rx * 0.22, y + 0.9, rx, CORTEN_SOMBRE)
            )
            morceaux.append(
                '<ellipse cx="%.2f" cy="%.2f" rx="%.2f" ry="1.8" fill="%s" '
                'fill-opacity="0.60"/>' % (x - rx * 0.20, y - 0.6, rx * 0.86, BOSSAGE_LUMIERE)
            )
    return morceaux


def zone_portrait(face, angle):
    """Portrait en espace négatif : on ne dessine pas le visage, on marque
    l'emprise traversante par laquelle on voit la pénombre intérieure."""
    morceaux = []
    coins = [
        point_sur_face(face, 0.16, 0.52, angle),
        point_sur_face(face, 0.84, 0.52, angle),
        point_sur_face(face, 0.84, 0.95, angle),
        point_sur_face(face, 0.16, 0.95, angle),
    ]
    points = " ".join("%.2f,%.2f" % p for p in coins)
    morceaux.append('<polygon points="%s" fill="%s"/>' % (points, CREUX))
    # Bandeau de l'inscription, lui aussi découpé.
    bande = [
        point_sur_face(face, 0.2, 0.4, angle),
        point_sur_face(face, 0.8, 0.4, angle),
        point_sur_face(face, 0.8, 0.455, angle),
        point_sur_face(face, 0.2, 0.455, angle),
    ]
    morceaux.append(
        '<polygon points="%s" fill="%s"/>'
        % (" ".join("%.2f,%.2f" % p for p in bande), CREUX)
    )
    # Signature de l'auteur, au pied de la face.
    sig = [
        point_sur_face(face, 0.3, 0.055, angle),
        point_sur_face(face, 0.56, 0.055, angle),
        point_sur_face(face, 0.56, 0.085, angle),
        point_sur_face(face, 0.3, 0.085, angle),
    ]
    morceaux.append(
        '<polygon points="%s" fill="%s" fill-opacity="0.8"/>'
        % (" ".join("%.2f,%.2f" % p for p in sig), CREUX)
    )
    return morceaux


def sommet(angle):
    """Face supérieure du prisme : sans elle, le volume paraît ouvert."""
    d, e = LARGEUR / 2.0, PROFONDEUR / 2.0
    coins = [
        projeter(-d, HAUTEUR, e, angle), projeter(d, HAUTEUR, e, angle),
        projeter(d, HAUTEUR, -e, angle), projeter(-d, HAUTEUR, -e, angle),
    ]
    return '<polygon points="%s" fill="%s"/>' % (
        " ".join("%.2f,%.2f" % p for p in coins), CORTEN_SOMMET
    )


def gradins(angle):
    """Socle de béton armé à gradins, coulé sur place."""
    morceaux = []
    y = 0.0
    for largeur, hauteur in reversed(SOCLE):
        d = largeur / 2.0
        bas, haut = y - hauteur, y
        sommet = [
            projeter(-d, haut, d, angle), projeter(d, haut, d, angle),
            projeter(d, haut, -d, angle), projeter(-d, haut, -d, angle),
        ]
        morceaux.append(
            '<polygon points="%s" fill="%s"/>'
            % (" ".join("%.2f,%.2f" % p for p in sommet), BETON)
        )
        for nx, nz in ((0, 1), (1, 0), (0, -1), (-1, 0)):
            if not normale_visible(nx, nz, angle):
                continue
            if nz:
                a = (-d * nz, d * nz)
            else:
                a = (d * nx, -d * nx)
            if nz:
                coins = [projeter(a[0], bas, d * nz, angle), projeter(a[1], bas, d * nz, angle),
                         projeter(a[1], haut, d * nz, angle), projeter(a[0], haut, d * nz, angle)]
            else:
                coins = [projeter(d * nx, bas, a[0], angle), projeter(d * nx, bas, a[1], angle),
                         projeter(d * nx, haut, a[1], angle), projeter(d * nx, haut, a[0], angle)]
            morceaux.append(
                '<polygon points="%s" fill="%s"/>'
                % (" ".join("%.2f,%.2f" % p for p in coins), BETON_SOMBRE)
            )
        y = bas
    return morceaux


def vue(angle):
    morceaux = []
    # Faces arrière d'abord, faces avant ensuite : pas de z-buffer nécessaire.
    visibles = [f for f in FACES if normale_visible(FACES[f][0], FACES[f][1], angle)]
    for face in visibles:
        morceaux.append(quadrilatere(face, angle, eclairement(face, angle)))
        nature = FACES[face][2]
        if nature == "texture":
            morceaux += bossages(face, angle, RANGEES_TEXTURE, 0.95, 0.1)
        else:
            morceaux += zone_portrait(face, angle)
            morceaux += bossages(face, angle, RANGEES_PORTRAIT, 0.37, 0.1)
    # Arête verticale la plus proche : lit le creux du prisme.
    morceaux = gradins(angle) + [sommet(angle)] + morceaux

    titre = (
        "SANKARA, L'ÉTERNEL VEILLEUR, sculpture monumentale de Hamed Ouattara, "
        "vue de substitution à %d degrés" % angle
    )
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 400" '
        'width="300" height="400" role="img" aria-label="%s">\n'
        "<title>%s</title>\n"
        '<rect width="300" height="400" fill="#1a1816"/>\n'
        "%s\n</svg>\n" % (titre, titre, "\n".join(morceaux))
    )


def main():
    os.makedirs(SORTIE, exist_ok=True)
    ecrits = 0
    for angle in range(0, 360, PAS):
        chemin = os.path.join(SORTIE, "rotation-%03d.svg" % angle)
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(vue(angle))
        ecrits += 1
    print("%d vues de substitution dans %s" % (ecrits, os.path.relpath(SORTIE, RACINE)))


if __name__ == "__main__":
    main()
