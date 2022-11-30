from flask import Flask, render_template, request
from flask_pymongo import PyMongo
from neo4j import GraphDatabase, basic_auth
import os

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/projet"
mongo = PyMongo(app)


uri = "bolt://localhost:11003"
driver = GraphDatabase.driver(uri, auth=basic_auth("flask", "1234"))
#print(driver)
def create_relation(tx, key, value, jaccard):
    print("neo4j : {'"+key+"', '"+value+"', '"+jaccard+"'}")
    return(tx.run("MATCH (a:Protein) MATCH (b:Protein) WHERE id(b) <> id(a) AND a."+key+"= $value AND not exists((a) - [:SIMILAR_TO] -> (b)) WITH 1.0*size(apoc.coll.intersection(a.interPro,b.interPro)) / size(apoc.coll.union(a.interPro, b.interPro)) AS jaccard_similarity, a, b WHERE jaccard_similarity > $jaccard CREATE (a)-[:SIMILAR_TO {jaccard: jaccard_similarity}]->(b)",
    value=value, jaccard = float(jaccard)))

def get_nbVoisin(tx, key, value, jaccard):
    result = tx.run("MATCH p=(:Protein {"+key+": $value})-[r:SIMILAR_TO]->() WHERE  r.jaccard > $jaccard RETURN Count(r)", value=value, jaccard = float(jaccard))
    value = result.value()[0]
    return(value)


@app.route("/protein", methods=['GET'])
def protein():
    arg = [(k, v) for k, v in request.args.to_dict(flat=False).items()]
    database = os.getenv("NEO4J_DATABASE", "neo4j")
    print(arg)

    if arg[1][1][0] == 'entry':
        protein = mongo.db.proteins.find({"Entry": arg[0][1][0]})
    else:
        protein = mongo.db.proteins.find({"Entry Name": arg[0][1][0]})   

    protein=protein[0]
    if protein['InterPro']!="":
        voisin = True
        drive = driver.session(database=database)
        drive.execute_write(create_relation, arg[1][1][0], arg[0][1][0], arg[2][1][0])
        nbVoisin = drive.execute_write(get_nbVoisin, arg[1][1][0], arg[0][1][0], arg[2][1][0])
        print(nbVoisin)
    else:
        print('pas de voisin')
        voisin = False



    return render_template("projects-1.html", protein=protein, voisin=voisin, jaccard=arg[2][1][0], nbVoisin = nbVoisin)
        
@app.route("/")
def HOME_PAGE():
    #db.proteins.find({"EC number": {$eq : ""}}).count()
    nbLabel = mongo.db.proteins.count_documents({"EC number": {"$ne" : ""}})

    nbNonLabel = mongo.db.proteins.count_documents({"EC number": {"$eq" : ""}})

    nbNonVoisin = mongo.db.proteins.count_documents({"InterPro": {"$eq" : ""}}) + 2389

    #for i in ListofInterPro:
    #    for j in i["InterPro"]:
    #        if j in InterproArray :
    #            index = InterproArray.index(j)
    #            InterProOc[index]+=1
    #            if InterProOc[index] > 1:
    #                InterproArray.pop(index)
    #                InterProOc.pop(index)

    
    
    return render_template("index.html", nbLabel = nbLabel, nbNonLabel = nbNonLabel, nbNonVoisin = nbNonVoisin)

if __name__ == '__main__':
    app.run(debug=True)


driver.close()