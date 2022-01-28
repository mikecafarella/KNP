export default async function handle(req, res) {
   let statusSuccess = (req.method === 'POST') ? 201: 200;
   let url = `http://localhost:5000/subgraph`;
    const res2 = await fetch(url,
    { method: req.method,
      body: JSON.stringify(req.body),
      headers: {
        "Content-Type": "application/json"
      },
    });
    const dobjs = await res2.json();
    res.status(statusSuccess).json(dobjs)
  }