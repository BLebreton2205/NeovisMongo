### Membres du projet :
- LEBRETON Baptiste;
- RIVIERE Mickael;
- SAMSON Ulrik.

# Comment utiliser notre projet

Voici les étapes à suivre afin de lancer notre projet. Bien entendu, la première phase, à savoir ********Importation et prétraitement********, n’est pas à réaliser à chaque lancement, mais uniquement lors du premier lancement.

## Importation et prétraitement

Afin de réaliser ce projet, nous avons utilisé la base de données utilisée est dans le dossier `/Database` du répertoire [GitHub](https://github.com/BLebreton2205/NeovisMongo/tree/master/Database). Il a tout de même fallu faire un premier traitement sur ces bases pour modifier le type de l’argument `InterPro` des protéines. En effet, il s’agissait d’une chaîne de caractère, or, nous avions besoin d’une liste de chaînes de caractère.

```sql
//initialement
"IPR000232;IPR027725;IPR010542;IPR036388;IPR036390;"

//après traitement
["IPR000232","IPR027725","IPR010542","IPR036388","IPR036390"]
```

### MongoDB :

Afin d’importer la base de données, nous avons utilisé la commande suivante :

```jsx
mongoimport --port 27017 --db projet --collection proteins --type tsv --file </path/to/file.tsv> --headerline
```

Nous utilisons donc `mongoimport` pour importer les données dans la table ****************************projet****************************. On nomme la collection ****************proteins****************. 

Ensuite, il a fallu modifier, pour chaque ligne, le type de `InterPro`. Pour cela, nous avons utilisé deux `aggregates`:

```java
db.proteins.aggregate([
    {$project: {InterPro: {$substr: ["$InterPro",0,{$add: [{$strLenCP: "$InterPro"},-1]}]}}},
    {$project: {InterPro: {$split: ["$InterPro",";"]}}},
    {$merge:"proteins"}
])
```

### Neo4J :

Concernant Neo4J, nous avons pu modifier la valeur d’`InterPro` dès l’importation :

```jsx
LOAD CSV WITH HEADERS FROM "file:/output.csv" as l
CREATE (protein:Protein{entry:l.` Entry`, entryName:l.`Entry Name`, proteinName:l.`Protein names`, organism:l.Organism, sequence:l.Sequence, ecNUmber:l.`EC number`, interPro: split(substring(l.InterPro, 0, size(l.InterPro) -1), ';')});
```

## Lancement de l’application

L’application est en `Flask`, elle demande donc Python avec certaines librairies :

```bash
pip install Flask Flask-PyMongo neo4j
```

Pour lancer le serveur via `Python` :

```bash
python app.py
```

# 1 - Réalisations

L’ensemble des commandes est effectué depuis `Flask`, nous donnerons simplement ici les références des commandes sous Neo4j/Mongo.

### 1.1. Recherche d’une protéine via son nom/ID & Affichage des informations

Il est possible de rechercher une protéine via l’une de ses clefs sous MongoDB :

```sql
//via Entry
mongo.db.proteins.find({"Entry": <Entry_de_la_proteine>})

//via Entry Name
mongo.db.proteins.find({"Entry Name": <Entry_Name_de_la_proteine>})
```

La sortie de la commande nous donne accès aux informations sous forme de JSON :

```json
{
  "_id": {
    "$oid": "6358dabb84310a57e1471c45"
  },
  "Entry": "A0A087WPF7",
  "Entry Name": "AUTS2_MOUSE",
  "Protein names": "Autism susceptibility gene 2 protein homolog",
  "Organism": "Mus musculus (Mouse)",
  "Sequence": "MDGPTRGHGLRKKRRSRSQRDRERRSRAGLGTGAAGGIGAGRTRAPSLASSSGSDKEDNGKPPSSAPSRPRPPRRKRRESTSAEEDIIDGFAMTSFVTFEALEKDVAVKPQERAEKRQTPLTKKKREALTNGLSFHSKKSRLSHSHHYSSDRENDRNLCQHLGKRKKMPKGLRQLKPGQNSCRDSDSESASGESKGFQRSSSRERLSDSSAPSSLGTGYFCDSDSDQEEKASDASSEKLFNTVLVNKDPELGVGALPEHNQDAGPIVPKISGLERSQEKSQDCCKEPVFEPVVLKDPHPQLPQLPSQAQAEPQLQIPSPGPDLVPRTEAPPQFPPPSTQPAQGPPEAQLQPAPLPQVQQRPPRPQSPSHLLQQTLPPVQSHPSSQSLSQPLSAYNSSSLSLNSLSSRSSTPAKTQPAPPHISHHPSASPFPLSLPNHSPLHSFTPTLQPPAHSHHPNMFAPPTALPPPPPLTSGSLQVPGHPAGSTYSEQDILRQELNTRFLASQSADRGASLGPPPYLRTEFHQHQHQHQHTHQHTHQHTFTPFPHAIPPTAIMPTPAPPMFDKYPTKVDPFYRHSLFHSYPPAVSGIPPMIPPTGPFGSLQGAFQPKTSNPIDVAARPGTVPHTLLQKDPRLTDPFRPMLRKPGKWCAMHVHIAWQIYHHQQKVKKQMQSDPHKLDFGLKPEFLSRPPGPSLFGAIHHPHDLARPSTLFSAAGAAHPTGTPFGPPPHHSNFLNPAAHLEPFNRPSTFTGLAAVGGNAFGGLGNPSVTPNSVFGHKDSPSVQNFSNPHEPWNRLHRTPPSFPTPPPWLKPGELERSASAAAHDRDRDVDKRDSSVSKDDKERESVEKRHPSHPSPAPPVPVSALGHNRSSTDPTTRGHLNTEAREKDKPKEKERDHSGSRKDLTTEEHKAKESHLPERDGHSHEGRAAGEEPKQLSRVPSPYVRTPGVDSTRPNSTSSREAEPRKGEPAYENPKKNAEVKVKEERKEDHDLPTEAPQAHRTSEAPPPSSSASASVHPGPLASMPMTVGVTGIHAMNSIGSLDRTRMVTPFMGLSPIPGGERFPYPSFHWDPMRDPLRDPYRDLDMHRRDPLGRDFLLRNDPLHRLSTPRLYEADRSFRDREPHDYSHHHHHHHHPLAVDPRREHERGGHLDERERLHVLREDYEHPRLHPVHPASLDGHLPHPSLLTPGLPSMHYPRISPTAGHQNGLLNKTPPTAALSAPPPLISTLGGRPGSPRRTTPLSAEIRERPPSHTLKDIEAR",
  "EC number": "",
  "InterPro": [
    "IPR023246"
  ]
}
```

### 1.2. Affichage des voisins

Pour rechercher les voisins d’une protéine, on doit se baser sur l’**Indice de Jaccard.** L’indice de Jaccard évalue la ressemblance entre deux ensembles d'informations (ici les `InterPro`) en faisant le rapport entre les parties communes et celles propres à chaque ensemble.

L’indice de Jaccard nous permet ainsi d’obtenir une valeur représentant le ratio de ressemblance entre deux protéines.

L’affichage des voisins requiert dans un premier temps de créer les relations sous Neo4j :

```sql
//Match des proteines
MATCH (a:Protein)
//Match de la protéine (a) qui possède l'Entry désiré
//Match des autres protéines (b), différentes de (a)
//avec vérification qu'une relation (a)-[]-(b) n'existe pas déjà
MATCH (b:Protein) WHERE id(b) <> id(a) AND a.entry="<entry>" AND not exists((a) - [:SIMILAR_TO] -> (b))
//Calcul du Jaccard
WITH 1.0*size(apoc.coll.intersection(a.interPro,b.interPro)) / size(apoc.coll.union(a.interPro, b.interPro)) AS jaccard_similarity, a, b
//Vérification de l'indice Jaccard
WHERE jaccard_similarity > <value>
//Création de la relation
CREATE (a)-[:SIMILAR_TO {jaccard: jaccard_similarity}]->(b)
```

L’affichage est fait via la librairie `neovis.js`. Si l’on regarde de plus près un extrait du code, on sélectionne la protéine par son Entry (ID), ainsi que les protéines voisines via les relations précédemment créées.

```jsx
function draw() {
	  queryInitial=`MATCH p=(:Protein {entry: '${entry}'})-[r:SIMILAR_TO]->() WHERE  r.jaccard > ${j} RETURN p`;
	  ...
}
...
var config = {
    neo4j: {
        serverUrl: "bolt://<adresse>:<port>",
        serverUser: "<user>",
        serverPassword: "<password>",
}
...
```

# 2 - Tâche non implémenté

### 2.1. Affichage des voisins des voisins

L’affichage des voisins des voisins utilise la même stratégie que pour trouver les voisins. Il faut d’abord créer les relations avec les voisins proches (n), puis créer les relations avec les voisins des voisins (n+1).

Néanmoins, si l’on se base sur le nombre moyen de voisins que possède une protéine (25 voisins en moyenne, résultat empirique), le nombre total de protéines serait de 25² (environ 600 en moyenne).

Nous sommes donc devant un problème de qualité de service, ou l’affichage de plusieurs centaines de protéines prendrait trop de temps sur une machine client pour un confort d’utilisation.

Le code prototype auquel nous avons réfléchi est celui ci-contre :

```sql
MATCH (a:Protein)
MATCH (b:Protein) WHERE id(b) <> id(a) AND a.entry="<Entry>" AND not exists((a) - [:SIMILAR_TO] -> (b))

WITH 1.0*size(apoc.coll.intersection(a.interPro,b.interPro)) / size(apoc.coll.union(a.interPro, b.interPro)) AS jaccard_similarity, a, b
WHERE jaccard_similarity > 0.9 

CREATE (a)-[:SIMILAR_TO {jaccard: jaccard_similarity}]->(b)

//Match avec les autres protéines
WITH b
//Vérification que les voisins des voisins sont different de la protéine originelle et des voisins (n)
//et qu'il n'existe pas déjà de relation
MATCH (c:Protein) WHERE id(a) <> id(b) <> id(c) AND not exists((b) - [:SIMILAR_TO] -> (c))

//vérification de l'indice Jaccard
WITH 1.0*size(apoc.coll.intersection(b.interPro,c.interPro)) / size(apoc.coll.union(b.interPro, c.interPro)) AS jaccard_similarity, b, c
WHERE jaccard_similarity > 0.9

//création des rélations
CREATE (b)-[:SIMILAR {jaccard: jaccard_similarity}]->(c)
```

# 3 - Tâche non accompli

### 3.1. Labellisation des protéines

La tâche finale “Labellisation des protéines” n’a pas été réalisée. En effet, nous n’avons pas réussi à trouver la méthode de choix des labels pour les protéines. Nous n'avons ainsi pas pu traiter cette partie.