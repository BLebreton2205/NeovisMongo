
// define config car
// instantiate nodevis object
// draw

let neoviz;
let queryInitial

function draw() {
    if(voisin=="True"){
        queryInitial=`MATCH p=(:Protein {entry: '${entry}'})-[r:SIMILAR_TO]->() WHERE  r.jaccard > ${j} RETURN p`;
    }else{
        queryInitial=`MATCH p=(:Protein {entry: '${entry}'}) RETURN p`
    }
var config = {
    containerId: "viz",
    neo4j: {
        serverUrl: "bolt://localhost:11003",
        serverUser: "neo4j",
        serverPassword: "1234",
    },
labels: {
    Protein: {
        label: "entry",
        [NeoVis.NEOVIS_ADVANCED_CONFIG]:{
            function : {
                title: NeoVis.objectToTitleHtml
            },
        }
    }
},
relationships: {
    SIMILAR_TO: {
        value:"jaccard",
        [NeoVis.NEOVIS_ADVANCED_CONFIG]:{
            function : {
                title: NeoVis.objectToTitleHtml
            },
        }
    }
},
    initialCypher: queryInitial
};

neoviz = new NeoVis.default(config);
neoviz.render();
console.log(neoviz);
}
