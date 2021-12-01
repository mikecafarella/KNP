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
                  versions: {
                    orderBy: {
                        id: 'desc',
                      },
                    include: {
                      dobj: {
                        include: {
                          owner: true,
                          predecessors: {
                            include: {
                              owner: true,
                              NameAssignment: {
                                include: {
                                  objname: true
                                }
                              },
                              JsonData: true,
                              CsvData: true,
                              ImgData: true,
                              ColumnData: true,
                              SchemaData: true,
                              PyStrData: true,
                              PyNumData: true,
                              FunctionData: true,
                              predecessors: {
                                include: {
                                  owner: true,
                                  NameAssignment: {
                                    include: {
                                      objname: true
                                    }
                                  },
                                  JsonData: true,
                                  CsvData: true,
                                  ImgData: true,
                                  ColumnData: true,
                                  SchemaData: true,
                                  PyStrData: true,
                                  PyNumData: true,
                                  FunctionData: true,
                                  predecessors: true
                                }
                              }
                            }
                          },
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
        // const successors = await prisma.dataObject.findMany({
        //   where: {
        //     predecessors: {
        //       id: { equals: obj[0].versions[0].dobj.id }
        //     }
        //   },
        // })
        //
        // console.log(successors)

    {/**
      Convert this into the format needed by client
    */}

    // Find the right versions
    let vid = 0
    if (req.query.v) {
      for (let i = 0; i < obj[0].versions.length; i++) {
        if (obj[0].versions[i].id == req.query.v) vid = i
      }
    }

    var outobj = {
      label: {
        id: obj[0].id,
        name: obj[0].name,
        desc: obj[0].desc,
        owner: obj[0].owner,
        created: obj[0].versions[0].created,
        iscurrent: true,
      },
      dobj: {
        id: obj[0].versions[vid].dobj.id,
        created: obj[0].versions[vid].dobj.created,
        datatype: obj[0].versions[vid].dobj.datatype,
        comment: obj[0].versions[vid].dobj.comment,
        owner: obj[0].versions[vid].dobj.owner,
        predecessors: obj[0].versions[vid].dobj.predecessors,
        JsonData: obj[0].versions[vid].dobj.JsonData,
        CsvData: obj[0].versions[vid].dobj.CsvData,
        ImgData: obj[0].versions[vid].dobj.ImgData,
        ColumnData: obj[0].versions[vid].dobj.ColumnData,
        SchemaData: obj[0].versions[vid].dobj.SchemaData,
        FunctionData: obj[0].versions[vid].dobj.FunctionData,
        PyStrData: obj[0].versions[vid].dobj.PyStrData,
        PyNumData: obj[0].versions[vid].dobj.PyNumData,
      }
    }

    let versions = []
    for (let i = 0; i < obj[0].versions.length; i++) {
      const readableDate = new Date(obj[0].versions[i].dobj.created).toString()
      versions.push({
        id: obj[0].versions[i].dobj.id,
        dobjid: obj[0].id,
        created: obj[0].versions[i].dobj.created,
        readableDate: readableDate,
        datatype: obj[0].versions[i].dobj.datatype,
        comment: obj[0].versions[i].dobj.comment,
        owner: obj[0].versions[i].dobj.owner,
        predecessors: obj[0].versions[i].dobj.predecessors,
        JsonData: obj[0].versions[i].dobj.JsonData,
        CsvData: obj[0].versions[i].dobj.CsvData,
        ImgData: obj[0].versions[i].dobj.ImgData,
        ColumnData: obj[0].versions[i].dobj.ColumnData,
        SchemaData: obj[0].versions[i].dobj.SchemaData,
        FunctionData: obj[0].versions[i].dobj.FunctionData,
        PyStrData: obj[0].versions[i].dobj.PyStrData,
        PyNumData: obj[0].versions[i].dobj.PyNumData,
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
        created: obj[0].NameAssignment[0].created,
        iscurrent: labelIsCurrent,
      },
      dobj: {
        id: obj[0].id,
        created: obj[0].created,
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
