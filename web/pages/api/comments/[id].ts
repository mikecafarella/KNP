export default async function handle(req, res) {
  if (req.method == 'GET') {
      const { id } = req.query
      const res2 = await fetch(`http://localhost:5000/comments/${id}`)
      const dobjs = await res2.json()
       res.status(200).json(dobjs)
 } else if (req.method == 'POST') {
      const { id } = req.query
      const res2 = await fetch(`http://localhost:5000/addcomment/${id}`,
      { method: "POST",
        body: JSON.stringify(req.body),
        headers: {
          "Content-Type": "application/json"
        },
        })
      const dobjs = await res2.json()
      res.status(200).json(dobjs)      
  }
}
