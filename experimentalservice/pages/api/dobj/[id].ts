import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

export default async function handle(req, res) {
  {/**
    This function takes an 'id' of an object to retrieve.
    It is either prefixed with an "X", indicating it's a label.
    Or it has no prefix, in which case it's a raw data object.
    This returns data in the format of "DataObjProps".
  */}
  if (req.query.id.startsWith("X")) {
    var realId = Number(req.query.id.substring(1))
    const obj = await prisma.objectName.findMany({
      where: { id: realId },
      include: {owner: true,
                  version: {
                    include: {
                      dobj: {
                        include: {
                          owner: true,
                          predecessors: true,
                          JsonData: true,
                          CsvData: true,
                          ImgData: true,
                          ColumnData: true,
                          SchemaData: true,
                          PyStrData: true,
                          PyNumData: true,
                          FunctionData: true,
                        }
                     }
                    }
                  }
                }
              })

              console.log(obj)

    {/**
      Convert this into the format needed by client
    */}

    var outobj = {
      label: {
        id: obj[0].id,
        name: obj[0].name,
        desc: obj[0].desc,
        owner: obj[0].owner,
        timestamp: obj[0].version.timestamp,
        iscurrent: true,
      },
      dobj: {
        id: obj[0].version.dobj.id,
        timestamp: obj[0].version.dobj.timestamp,
        datatype: obj[0].version.dobj.datatype,
        comment: obj[0].version.dobj.comment,
        owner: obj[0].version.dobj.owner,
        predecessors: obj[0].version.dobj.predecessors,
        JsonData: obj[0].version.dobj.JsonData,
        CsvData: obj[0].version.dobj.CsvData,
        ImgData: obj[0].version.dobj.ImgData,
        ColumnData: obj[0].version.dobj.ColumnData,
        SchemaData: obj[0].version.dobj.SchemaData,
        FunctionData: obj[0].version.dobj.FunctionData,
        PyStrData: obj[0].version.dobj.PyStrData,
        PyNumData: obj[0].version.dobj.PyNumData,
      }
    }
    let versions = []
    for (let i = 0; i < obj.length; i++) {
      versions.push({
        id: obj[i].version.dobj.id,
        timestamp: obj[i].version.dobj.timestamp,
        datatype: obj[i].version.dobj.datatype,
        comment: obj[i].version.dobj.comment,
        owner: obj[i].version.dobj.owner,
        predecessors: obj[i].version.dobj.predecessors,
        JsonData: obj[i].version.dobj.JsonData,
        CsvData: obj[i].version.dobj.CsvData,
        ImgData: obj[i].version.dobj.ImgData,
        ColumnData: obj[i].version.dobj.ColumnData,
        SchemaData: obj[i].version.dobj.SchemaData,
        FunctionData: obj[i].version.dobj.FunctionData,
        PyStrData: obj[i].version.dobj.PyStrData,
        PyNumData: obj[i].version.dobj.PyNumData,
      })
    }
    outobj.versions = versions
    res.json(outobj);

  } else {
    var realId = Number(req.query.id)
    const obj = await prisma.dataObject.findMany({
      where: { id: realId },
      include: {
              NameAssignment: {
                include: {
                  ObjectName: {
                    include: {
                      owner: true,
                    }
                  },
                }
              },
              owner: true,
              predecessors: true,
              JsonData: true,
              CsvData: true,
              ImgData: true,
              ColumnData: true,
              SchemaData: true,
              FunctionData: true,
              PyStrData: true,
              PyNumData: true,
              }
      })

    var labelIsCurrent = true;
    {/**
      Convert this into the format needed by client
    */}
    var outobj = {
      label: {
        id: obj[0].NameAssignment[0].ObjectName[0].id,
        name: obj[0].NameAssignment[0].ObjectName[0].name,
        desc: obj[0].NameAssignment[0].ObjectName[0].desc,
        owner: obj[0].NameAssignment[0].ObjectName[0].owner,
        timestamp: obj[0].NameAssignment[0].timestamp,
        iscurrent: labelIsCurrent,
      },
      dobj: {
        id: obj[0].id,
        timestamp: obj[0].timestamp,
        datatype: obj[0].datatype,
        comment: obj[0].comment,
        owner: obj[0].owner,
        predecessors: obj[0].predecessors,
        JsonData: obj[0].JsonData,
        CsvData: obj[0].CsvData,
        ImgData: obj[0].ImgData,
        ColumnData: obj[0].ColumnData,
        SchemaData: obj[0].SchemaData,
        FunctionData: obj[0].FunctionData,
        PyStrData: obj[0].PyStrData,
        PyNumData: obj[0].PyNumData,
      }
    }
     res.json(outobj);
  }
}
