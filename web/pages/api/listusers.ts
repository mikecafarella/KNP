import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()


export default async function handle(req, res) {
    const users = await prisma.user.findMany({
      select: {email: true, 
              id: true, 
              name: true,
              posts: true
      }
    })
    res.json(users)
  }
  

