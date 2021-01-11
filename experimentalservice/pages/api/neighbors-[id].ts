import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

export default async function handle(req, res) {
  const obj1 = await prisma.objectName.findOne({
    where: { id: Number(req.query.id) },
    include: {version: {
      include: {
        dobj: {
            include: {
                predecesors: true,
            }
        }
    }}}
    })

    const predIds = map(obj1.version.)
  const obj = await prisma.objectName.findMany({
      where: { id: Number(req.query.id) },
      include: {owner: true, 
                version: {
                  include: {
                    dobj: {
                      include: {
                        owner: true,
                        predecessors: true,
                        JsonData: "/datatypes/json" == obj1.version.dobj.datatype,
                      }
                    }
                  }
                }
              }
            })
  res.json(obj[0])
}