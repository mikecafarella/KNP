import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

export default async function handle(req, res) {
    const obj1 = await prisma.dataObject.findOne({
        where: { id: Number(req.query.id) },
        include: {
            predecessors: true,
        }
      })
    

    console.log(obj1)
    const obj = await prisma.dataObject.findOne({
    where: { id: Number(obj1.id) },
    include: {
        owner: true,
        NameAssignment: {
          include: {
              ObjectName: true,
          }  
        },
        JsonData: "/datatypes/json" == obj1.datatype,
        CsvData: "/datatypes/csv" == obj1.datatype,
        ColumnData: "/datatypes/datacolumn" == obj1.datatype,
        owner: true,
        predecessors: {
            select: {
                id: true,
            }
        }
    }
  })

  const modifiedObj = {}
  modifiedObj.id = obj.id
  modifiedObj.owner = obj.owner
  modifiedObj.version = {}
  modifiedObj.version.dobj = obj

  console.log(modifiedObj)

  res.json(modifiedObj)
}