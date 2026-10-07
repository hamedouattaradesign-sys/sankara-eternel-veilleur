# Mise en ligne — marche à suivre

État au 7 octobre 2026 : **le site est déployé et il fonctionne.** 39 pages,
trois langues, 0 anomalie.

| | |
|---|---|
| Dépôt | `github.com/hamedouattaradesign-sys/sankara-eternel-veilleur`, public, 28 commits |
| Hébergement | **Vercel**, projet `sankara-eternel-veilleur`, équipe *Studio Hamed Ouattara* |
| Déploiement | production, depuis le commit `4cdc321`, construit en trois secondes |
| Adresse publique | `https://sankara.hamedouattara.com` — **en attente du DNS** |

Il ne reste que des gestes qui demandent vos accès.

---

## 1. L'enregistrement DNS — chez IONOS, c'est le seul vrai blocage

Le domaine `hamedouattara.com` est rattaché à votre compte Vercel, mais sa zone
DNS reste gérée chez **IONOS** (`ns1022.ui-dns.biz` et les trois autres). C'est
donc chez IONOS que l'enregistrement se crée, et personne ne peut le faire à
votre place.

Dans la gestion DNS de `hamedouattara.com`, ajouter :

| Type | Nom d'hôte | Pointe vers | TTL |
|---|---|---|---|
| CNAME | `sankara` | `81197017f9857654.vercel-dns-017.com` | 1 heure |

**Cette valeur est propre à ce projet Vercel**, elle n'est pas la valeur
générique `cname.vercel-dns.com` que donne la documentation. Si elle doit un
jour être revérifiée, elle se lit sur la page *Settings → Domains* du projet,
en face du domaine. C'est cette page qui fait foi, pas ce document.

Dans le champ « Nom d'hôte », saisir `sankara` seul : IONOS ajoute le domaine
lui-même. Et n'y modifier aucune autre ligne — les enregistrements MX portent la
messagerie.

La propagation prend de une à quelques heures, et le certificat TLS n'est émis
qu'une fois le nom résolu.

**Rien n'est public avant ce geste**, et c'est voulu : la protection Vercel
couvre toutes les adresses `.vercel.app` du projet et laisse passer le seul
domaine propre. Tant que le CNAME n'existe pas, le site est déployé mais
personne ne peut le lire. **C'est vous qui choisissez le moment de l'ouverture,
et c'est ce geste-là qui l'ouvre.**

---

## 2. Le dépôt est connecté à Vercel — fait

Le projet Vercel est lié à `hamedouattaradesign-sys/sankara-eternel-veilleur`,
branche de production `main`. **Chaque envoi sur `main` déclenche un déploiement
tout seul**, sans que personne ait à le demander — ni vous, ni moi.

C'est ce qui fait que le site ne dépend plus d'une session de travail pour être
publié. Le cycle est décrit plus bas.

Si cela devait un jour être défait, c'est ici que cela se règle :
**Vercel → projet `sankara-eternel-veilleur` → Settings → Git**.

## 3. Signer le dossier institutionnel

La deuxième édition réserve une zone de paraphe en fin de document. Trois points
à vérifier avant de signer :

- le **lieu** et la **date** du bloc de signature — aujourd'hui Ouagadougou,
  6 octobre 2026 ;
- la section **« Orienté nord-sud »**, qui n'existait pas dans la première
  édition ;
- le comptage : **douze rangées, 48 par face de texture, 152 au total**.

Renvoyez-moi le PDF signé : je le mets en place et je redéploie. L'opération
prend quelques secondes, et peut se faire après l'ouverture du site.

---

## 4. Une fois le DNS propagé

- **Vérifier l'adresse** : `curl -I https://sankara.hamedouattara.com` doit
  répondre `HTTP/2 200`.
- **Déclarer le site** à Google Search Console et à Bing, et leur soumettre
  `https://sankara.hamedouattara.com/sitemap.xml`.
- **Envoyer la demande au Mémorial** (`outils/presse/demande-image-memorial.md`)
  avec le dossier signé.

---

## Le cycle de publication, ensuite

```bash
python3 outils/build.py        # reconstruit public/
python3 outils/verifier.py     # doit dire 0 anomalie
git add -A && git commit -m "…"
git push
```

Le déploiement suit l'envoi, tout seul, en quelques secondes. Il n'y a rien
d'autre à faire : pas de compilation, pas de dépendance, pas de serveur.

---

## Ce que le site envoie comme en-têtes

Vérifié sur le déploiement en production, pas seulement écrit dans
`vercel.json`. La politique est stricte, et elle le peut parce que le site
n'appelle aucun service extérieur :

- `default-src 'none'` — rien n'est autorisé par défaut ;
- `connect-src 'none'` — le site ne peut faire aucune requête réseau ;
- `frame-ancestors 'none'` — il ne peut pas être encadré par un autre site ;
- le seul script en ligne est autorisé par son empreinte, pas par une
  permission générale.

S'y ajoutent `strict-transport-security` sur deux ans avec `preload`,
`x-content-type-options`, `referrer-policy`, et une `permissions-policy` qui
coupe la géolocalisation, la caméra, le micro et le pistage publicitaire.

**Si un script en ligne est un jour ajouté ou modifié**, son empreinte change et
il sera bloqué. Recalculer la nouvelle valeur et la reporter dans
`vercel.json` :

```bash
python3 -c "
import hashlib, base64, re, io
s = io.open('public/index.html', encoding='utf-8').read()
for m in re.findall(r'<script>(.*?)</script>', s, re.S):
    print('sha256-' + base64.b64encode(hashlib.sha256(m.encode()).digest()).decode())
"
```

Les images, le CSS, les polices et le JS sont mis en cache un an. Les pages HTML
ne sont jamais mises en cache : une correction est visible immédiatement.
