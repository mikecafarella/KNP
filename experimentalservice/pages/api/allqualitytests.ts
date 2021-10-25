export default async function handle(req, res) {
  if (req.method == 'GET') {
      const res2 = await fetch(`http://localhost:5000/allqualitytests`)
      const dobjs = await res2.json()
      res.status(200).json(dobjs)
  }
}
