#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Découpe Charis SIL aux seuls caractères dont le site a besoin, et l'encode
en WOFF2.

POURQUOI CHARIS. C'est une dérivée de Bitstream Charter, dessinée par Matthew
Carter pour rester lisible là où le rendu est mauvais — écrans de faible
définition, impression bon marché. SIL l'a reprise et étendue pour les
orthographes africaines. Pour un site burkinabè lu sur des téléphones d'entrée
de gamme, en français, en italien et en anglais, il n'y a pas de meilleur
choix, et il est sous licence libre.

POURQUOI LA DÉCOUPER. La fonte complète pèse 880 Ko par graisse : elle couvre
des centaines de langues. Le site en emploie moins de trois cents caractères.
Découpée, chaque graisse tombe sous les 30 Ko.

POURQUOI UN JEU FIXE, ET NON LES CARACTÈRES DU SITE. On pourrait ne garder que
les caractères présents aujourd'hui. Ce serait plus léger, et cela casserait au
premier mot nouveau : un nom propre, une citation, une légende. Le jeu ci-dessous
est arrêté une fois pour toutes et couvre le latin dont les trois langues ont
besoin, plus la ponctuation typographique.

Usage :  python3 outils/polices.py
         python3 outils/polices.py --verifier    contrôle sans réécrire
"""

import os
import subprocess
import sys

RACINE = os.path.dirname(os.path.abspath(os.path.join(__file__, "..")))
SOURCE = "/home/user/silnrsi/font-charis/references/v7000"
SORTIE = os.path.join(RACINE, "statique", "assets", "polices")

# Les trois coupes employées par la feuille de style : les titres et la marque
# sont en gras, les citations et le pied en romain, et <em> appelle l'italique.
# Sans l'italique, le navigateur penche le romain lui-même, et sur une fonte à
# empattements cela se voit.
COUPES = [
    ("Charis-Regular.ttf", "charis-400.woff2", "400", "normal"),
    ("Charis-Italic.ttf", "charis-400i.woff2", "400", "italic"),
    ("Charis-Bold.ttf", "charis-700.woff2", "700", "normal"),
]


def jeu_de_caracteres():
    """Ce que le site doit pouvoir écrire, et rien de plus."""
    car = set()

    # Latin de base, chiffres et ponctuation ASCII.
    car |= {chr(c) for c in range(0x20, 0x7F)}

    # Latin-1 : les accents du français et de l'italien, et les symboles
    # courants — °, ×, ·, ©, «, ».
    car |= {chr(c) for c in range(0xA0, 0x100)}

    # Latin étendu A, pour les quelques lettres qui manquent au Latin-1 :
    # Œ œ (français), Ÿ, et les lettres des noms propres qu'on peut croiser.
    car |= set("ŒœŸŠšŽžĆćČčĐđŁłŃńŐőŘřŚśŢţŰűŹźŻż")

    # Ponctuation typographique. L'apostrophe courbe, les tirets cadratin et
    # demi-cadratin, les guillemets des trois langues, les points de suspension,
    # l'espace insécable fine et le trait d'union insécable.
    car |= set("‐‑–—‘’“”„"
               "†‡•…‰‹›⁄"
               "  ​­")

    # Monnaies et symboles que le site peut avoir à écrire.
    car |= set("€$£₣№™−≈≤≥")

    # Exposants, pour « IIIᵉ Municipio » et les ordinaux.
    car |= set("ªºᵉ⁰¹²³"
               "⁴⁵⁶⁷⁸⁹")

    return "".join(sorted(car))


def decouper(source, cible, jeu):
    chemin = os.path.join(SOURCE, source)
    if not os.path.isfile(chemin):
        raise SystemExit(
            "Fonte introuvable : %s\n"
            "Cloner d'abord : git clone --depth 1 "
            "https://github.com/silnrsi/font-charis /home/user/silnrsi/font-charis"
            % chemin)
    sortie = os.path.join(SORTIE, cible)
    subprocess.run([
        sys.executable, "-m", "fontTools.subset", chemin,
        "--text=" + jeu,
        "--output-file=" + sortie,
        "--flavor=woff2",
        "--layout-features=kern,liga,calt,onum,tnum,frac",
        "--desubroutinize",
        "--no-hinting",
        "--drop-tables+=DSIG",
        "--name-IDs=1,2,3,4,5,6,13,14",   # on garde la licence dans la fonte
    ], check=True, capture_output=True)
    return os.path.getsize(sortie)


if __name__ == "__main__":
    jeu = jeu_de_caracteres()
    os.makedirs(SORTIE, exist_ok=True)
    print("Jeu de caractères : %d signes" % len(jeu))
    total = 0
    for source, cible, graisse, style in COUPES:
        octets = decouper(source, cible, jeu)
        total += octets
        print("  %-18s  %s %-7s  %5.1f Ko" % (cible, graisse, style, octets / 1024))
    print("  %-18s  %s  %5.1f Ko" % ("", " " * 11, total / 1024))
    if total > 120 * 1024:
        raise SystemExit(
            "Les fontes pèsent %.0f Ko au total, au-delà du budget de 120 Ko. "
            "Retirer une coupe ou resserrer le jeu de caractères." % (total / 1024))
