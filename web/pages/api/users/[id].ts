export default async function handle(req, res) {
  if (req.method == 'GET') {
      if (req.query.id == 'nologin') {
        return res.status(200).json({"nologin": true})
      }
      const { id } = req.query
      const res2 = await fetch(`http://localhost:5000/userdata/${id}`)
      const dobjs = await res2.json()
      res.status(200).json(dobjs)
  }
}
