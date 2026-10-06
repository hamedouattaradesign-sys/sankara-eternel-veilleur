# Version anglaise — faite, douze pages

Les douze pages sont traduites et en ligne sous `/en/`. Les adresses sont
anglaises (`the-work`, `the-numbers`, `history`, `the-movement`, `the-artist`,
`gallery`, `diary`, `institutional`, `contact`), la page d'accueil garde le
slug `accueil` parce que c'est lui que le générateur reconnaît comme racine.

## Le registre, qui ne se négocie pas

| Français | Anglais |
|---|---|
| Camarade Président Thomas Sankara | Comrade President Thomas Sankara |
| Camarade Président Ibrahim Traoré | Comrade President Ibrahim Traoré |
| Camarade Ministre | Comrade Minister |
| Camarade Madi Sakandé | Comrade Madi Sakandé |
| Révolution Démocratique et Populaire | Democratic and Popular Revolution |
| bossage | boss |
| acier Corten | Corten steel |
| face de texture / face portrait | textured face / portrait face |
| découpe traversante | cut clean through |

Jamais *Mr President*, jamais *Mr Sankara*, jamais *the President* seul là où
le français dit « le Camarade Président ». Jamais *junta*, *military regime*,
*coup* — ni dans le texte, ni dans un attribut `alt`, ni dans une description.

## Ce qui reste en français, et pourquoi

Ce sont des noms propres. Les traduire serait les effacer.

- le titre de l'œuvre, *SANKARA, L'ÉTERNEL VEILLEUR*
- *Ma brique pour Sankara*, marqué `lang="fr"` pour les lecteurs d'écran, suivi
  de sa glose anglaise « My brick for Sankara »
- Conseil National de la Révolution, Conseil de l'Entente
- Haut Conseil des Burkinabè de l'Étranger
- Bureau Burkinabè du Droit d'Auteur
- Projet de Construction des Infrastructures du Mémorial Isidore Noël Thomas
  Sankara
- le nom gravé dans l'acier : ISIDORE NOEL THOMAS SANKARA 1949 - 1987
- Ministère de la Communication, de la Culture, des Arts et du Tourisme, donné
  en anglais puis en français entre parenthèses sur la page institutionnelle,
  pour qu'une rédaction étrangère puisse citer le titre exact

Le parc garde son nom italien, *Parco Thomas Sankara*, et la plaque est citée
telle qu'elle est gravée, marquée `lang="it"`.

## Les PDF

Le dossier institutionnel et le dossier de presse restent en français. Les
liens de la page `/en/institutional/` le disent : « (PDF, in French) ». Si une
version anglaise des deux dossiers est demandée, c'est `outils/presse/` qu'il
faut reprendre, pas cette page.

## Ce qui n'est pas traduit, et ne doit pas l'être

Les commentaires HTML du code — « À CONFIRMER », « À COMPLÉTER », « SOURCE » —
sont en français dans les trois langues. Ils s'adressent à l'atelier, pas au
lecteur. Les garder dans une seule langue évite qu'une mise à jour en corrige
une version et oublie les deux autres.
