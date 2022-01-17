export default async function handle(req, res) {
   if (req.method == 'POST') {
        const { id } = req.query;
        const res2 = await fetch(`http://localhost:5000/addsubgraph/${id}`,
        { method: "POST",
          body: JSON.stringify(req.body),
          headers: {
            "Content-Type": "application/json"
          },
          })
        const dobjs = await res2.json();
        const subgraphs = dobjs.subgraphs;
        const body = JSON.parse(req.body);
        if (subgraphs.filter(subgraph => subgraph.subgraphNodeMD5s === JSON.stringify(body.subgraphNodeMD5s)).length > 0) {
            console.log("you just labeled this graph");

        }
        res.status(201).json(dobjs)      
    }
  }