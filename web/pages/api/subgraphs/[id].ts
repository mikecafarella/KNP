export default async function handle(req, res) {
   let method;
   let statusSuccess;
   if (req.method == 'POST') {
        method = 'POST'
        statusSuccess = 201
    } else if (req.method == 'PUT') {
        method = 'PUT'
        statusSuccess = 200
    }
    const { id } = req.query;
    const res2 = await fetch(`http://localhost:5000/addsubgraph/${id}`,
    { method: method,
      body: JSON.stringify(req.body),
      headers: {
        "Content-Type": "application/json"
      },
      })
    const dobjs = await res2.json();
    res.status(statusSuccess).json(dobjs)
  }