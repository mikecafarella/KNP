import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

export default async function handle(req, res) {
  // const posts = await prisma.timeline.findMany({
  //   orderBy: [
  //     {timestamp: 'desc',}
  //   ],
  //   include: { owner: true, ref: true },
  // })
  const posts = []
  res.json(posts)
}
