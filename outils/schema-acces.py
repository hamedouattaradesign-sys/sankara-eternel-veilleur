#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trace le schéma d'accès au Parco Thomas Sankara, dans la langue demandée.

Ce n'est PAS une carte. Le site ne fait aucune requête hors de son domaine :
pas de fond cartographique, pas de tuiles, pas de traceur tiers. C'est un
diagramme de trajet — les lignes et les arrêts sont réels, leur disposition ne
l'est pas. La page qui l'emploie le dit, et donne l'adresse et les coordonnées
pour une carte véritable.

Usage :  python3 outils/schema-acces.py fr > schema.svg
         python3 outils/schema-acces.py it | en
"""

import sys

ENCRE = "#1c1a17"; TRAIT = "#5c564d"; FILET = "#ddd5c7"
CORTEN = "#8a4f2b"; VERT = "#0a6136"; ROUGE = "#9c1c21"; PAPIER = "#f4efe6"

L, H = 520, 380

MOTS = {
    "fr": {
        "titre": "Schéma d'accès au Parco Thomas Sankara",
        "desc": ("Diagramme du trajet, et non une carte. Depuis le centre de Rome, deux chemins "
                 "mènent au parc. Par le métro : ligne B puis B1 jusqu'au terminus Jonio, puis "
                 "environ vingt-cinq minutes à pied ou un autobus. Par le trolleybus 90 depuis "
                 "la gare de Termini jusqu'à Largo Labia, dans le quartier de Val Melaina. "
                 "L'autobus 80 s'arrête Via Ugo della Seta, devant le parc. Le monument sera "
                 "dressé dans le parc, ses deux faces au visage tournées vers le nord et vers "
                 "le sud."),
        "depart": "Centre de Rome",
        "termini": "Roma Termini",
        "metro": "Métro B puis B1",
        "jonio": "Jonio", "jonio_sous": "terminus de la B1",
        "filobus": "Trolleybus 90", "bus80": "Autobus 80",
        "labia": "Largo Labia", "labia_sous": "Val Melaina",
        "arret": "Arrêt « Della Seta »", "arret_sous": "Via Ugo della Seta",
        "pied": "25 min à pied", "parc": "PARCO THOMAS SANKARA",
        "parc_sous": "Via Ugo della Seta, III Municipio",
        "nord": "N", "axe": "les deux faces au visage",
        "note": "Diagramme de trajet, non une carte à l'échelle.",
    },
    "it": {
        "titre": "Schema d'accesso al Parco Thomas Sankara",
        "desc": ("Diagramma del percorso, non una mappa. Dal centro di Roma due vie portano al "
                 "parco. Con la metropolitana: linea B poi B1 fino al capolinea Jonio, poi circa "
                 "venticinque minuti a piedi o un autobus. Con il filobus 90 da Roma Termini "
                 "fino a Largo Labia, a Val Melaina. L'autobus 80 ferma in Via Ugo della Seta, "
                 "davanti al parco. Il monumento sarà eretto nel parco, con le due facce che "
                 "portano il volto rivolte a nord e a sud."),
        "depart": "Centro di Roma",
        "termini": "Roma Termini",
        "metro": "Metro B poi B1",
        "jonio": "Jonio", "jonio_sous": "capolinea della B1",
        "filobus": "Filobus 90", "bus80": "Autobus 80",
        "labia": "Largo Labia", "labia_sous": "Val Melaina",
        "arret": "Fermata « Della Seta »", "arret_sous": "Via Ugo della Seta",
        "pied": "25 min a piedi", "parc": "PARCO THOMAS SANKARA",
        "parc_sous": "Via Ugo della Seta, III Municipio",
        "nord": "N", "axe": "le due facce con il volto",
        "note": "Diagramma di percorso, non una mappa in scala.",
    },
    "en": {
        "titre": "Access diagram for the Parco Thomas Sankara",
        "desc": ("A journey diagram, not a map. From the centre of Rome two ways lead to the "
                 "park. By underground: line B then B1 to the Jonio terminus, then about "
                 "twenty-five minutes on foot, or a bus. By trolleybus 90 from Roma Termini to "
                 "Largo Labia, in Val Melaina. Bus 80 stops on Via Ugo della Seta, in front of "
                 "the park. The monument will stand in the park, its two portrait faces turned "
                 "north and south."),
        "depart": "Centre of Rome",
        "termini": "Roma Termini",
        "metro": "Metro B then B1",
        "jonio": "Jonio", "jonio_sous": "B1 terminus",
        "filobus": "Trolleybus 90", "bus80": "Bus 80",
        "labia": "Largo Labia", "labia_sous": "Val Melaina",
        "arret": "“Della Seta” stop", "arret_sous": "Via Ugo della Seta",
        "pied": "25 min on foot", "parc": "PARCO THOMAS SANKARA",
        "parc_sous": "Via Ugo della Seta, III Municipio",
        "nord": "N", "axe": "the two portrait faces",
        "note": "A journey diagram, not a map to scale.",
    },
}


def tracer(langue):
    m = MOTS[langue]
    p = []

    def txt(x, y, t, taille=10, couleur=TRAIT, gras=False, ancre="middle"):
        return ('<text x="%.1f" y="%.1f" text-anchor="%s" font-size="%g" fill="%s"%s '
                'font-family="system-ui, sans-serif">%s</text>'
                % (x, y, ancre, taille, couleur, ' font-weight="700"' if gras else "", t))

    def noeud(x, y, r=7, couleur=TRAIT, plein=False):
        return ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke="%s" stroke-width="2.2"/>'
                % (x, y, r, couleur if plein else "#fff", couleur))

    def ligne(x1, y1, x2, y2, couleur, largeur=4.5, tirets=None):
        d = ' stroke-dasharray="%s"' % tirets if tirets else ""
        return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%g" '
                'stroke-linecap="round"%s/>' % (x1, y1, x2, y2, couleur, largeur, d))

    # Deux colonnes de départ, qui convergent vers le parc.
    XA, XB = 130.0, 390.0
    Y0, Y1, Y2, Y3 = 62.0, 150.0, 238.0, 318.0

    # --- branche métro, à gauche -----------------------------------------
    p.append(ligne(XA, Y0, XA, Y1, ROUGE))
    p.append(ligne(XA, Y1 + 46, XA, Y2, TRAIT, 3.4, "1 7"))
    p.append(noeud(XA, Y0))
    p.append(noeud(XA, Y1, 8, ROUGE, True))
    p.append(txt(XA, Y0 - 16, m["depart"], 10.5, ENCRE, True))
    p.append(txt(XA + 14, (Y0 + Y1) / 2 + 3, m["metro"], 9.5, ROUGE, ancre="start"))
    p.append(txt(XA, Y1 + 22, m["jonio"], 11, ENCRE, True))
    p.append(txt(XA, Y1 + 36, m["jonio_sous"], 9))
    p.append(txt(XA + 12, Y1 + 74, m["pied"], 9.5, ancre="start"))

    # --- branche autobus, à droite ---------------------------------------
    p.append(ligne(XB, Y0, XB, Y1, VERT))
    p.append(ligne(XB, Y1 + 46, XB, Y2, VERT))
    p.append(noeud(XB, Y0))
    p.append(noeud(XB, Y1, 8, VERT, True))
    p.append(noeud(XB, Y2, 8, VERT, True))
    p.append(txt(XB, Y0 - 16, m["termini"], 10.5, ENCRE, True))
    p.append(txt(XB + 14, (Y0 + Y1) / 2 + 3, m["filobus"], 9.5, VERT, ancre="start"))
    p.append(txt(XB, Y1 + 22, m["labia"], 11, ENCRE, True))
    p.append(txt(XB, Y1 + 36, m["labia_sous"], 9))
    p.append(txt(XB + 14, Y1 + 74, m["bus80"], 9.5, VERT, ancre="start"))
    p.append(txt(XB, Y2 + 22, m["arret"], 10.5, ENCRE, True))
    p.append(txt(XB, Y2 + 36, m["arret_sous"], 9))

    # --- convergence vers le parc ----------------------------------------
    XC = (XA + XB) / 2
    p.append(ligne(XA, Y2, XA, Y3 - 28, TRAIT, 3.4, "1 7"))
    p.append(ligne(XA, Y3 - 28, XB, Y3 - 28, TRAIT, 1.2))
    p.append(ligne(XB, Y2 + 44, XB, Y3 - 28, VERT, 3.4))
    p.append(ligne(XC, Y3 - 28, XC, Y3 - 14, TRAIT, 1.2))

    # Le parc, et l'axe du monument.
    p.append('<rect x="%.1f" y="%.1f" width="200" height="46" rx="4" fill="%s" stroke="%s" '
             'stroke-width="1.6"/>' % (XC - 100, Y3 - 14, PAPIER, CORTEN))
    p.append(txt(XC, Y3 + 6, m["parc"], 10.5, CORTEN, True))
    p.append(txt(XC, Y3 + 21, m["parc_sous"], 8.6))

    # Flèche du nord : le monument regarde le nord et le sud.
    xn, yn = L - 46, 300
    p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.6"/>'
             % (xn, yn + 30, xn, yn - 14, ENCRE))
    p.append('<path d="M %.1f %.1f l -5 11 l 5 -3.5 l 5 3.5 Z" fill="%s"/>' % (xn, yn - 18, ENCRE))
    p.append(txt(xn, yn - 24, m["nord"], 10, ENCRE, True))
    p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.2" '
             'stroke-dasharray="3 3"/>' % (xn - 16, yn + 8, xn + 16, yn + 8, CORTEN))
    p.append(txt(xn, yn + 46, m["axe"], 8, CORTEN))

    p.append('<line x1="20" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1"/>'
             % (H - 26, L - 20, H - 26, FILET))
    p.append(txt(L / 2, H - 10, m["note"], 8.6))

    return ('<svg viewBox="0 0 %d %d" width="%d" height="%d" role="img" '
            'aria-labelledby="acces-titre acces-desc" xmlns="http://www.w3.org/2000/svg">\n'
            '  <title id="acces-titre">%s</title>\n'
            '  <desc id="acces-desc">%s</desc>\n' % (L, H, L, H, m["titre"], m["desc"])
            + "\n".join("  " + e for e in p) + "\n</svg>")


if __name__ == "__main__":
    langue = sys.argv[1] if len(sys.argv) > 1 else "fr"
    if langue not in MOTS:
        raise SystemExit("Langue inconnue : %s (fr, it ou en)" % langue)
    sys.stdout.write(tracer(langue))
