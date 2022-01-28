export default async function handle(req, res) {
   const { id } = req.query
   console.log("SO CLOSE");
   console.log(id);
   let statusSuccess = (req.method === 'POST') ? 201: 200;
    const res2 = (req.method !== "GET") ? 
      await fetch(`http://localhost:5000/subgraph`,
        { method: req.method,
          body: JSON.stringify(req.body),
          headers: {
            "Content-Type": "application/json"
          },
        }) :
      await fetch(`http://localhost:5000/subgraphs/${id}`);
    const dobjs = await res2.json();
    res.status(statusSuccess).json(dobjs);
  }