import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()


export default async function handle(req, res) {
    const dobjs = await prisma.objectName.findMany({
      where: {isdeleted: 0, version: { dobj: { datatype: '/datatypes/function'}}},
      select: {version: {
                select: {dobj: true, timestamp: true},
                },
                owner: true,
                name: true,
                desc: true,
                id: true,
              },
    })
    res.json(dobjs)
  }
