import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

// POST /api/user
// Required fields in body: name, email
export default async function handle(req, res) {
  const email = req.body.email
  const name = req.body.name
  const result = await prisma.user.upsert({
    where: { email: email },
    update: { name: name },
    create: {
      email: email,
      name: name
    }
  })
  res.json(result)
}
