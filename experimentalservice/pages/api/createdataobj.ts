import { PrismaClient } from '@prisma/client'
const formidable = require('formidable')
import fs from "fs";
import { createBrotliDecompress } from 'zlib';


const prisma = new PrismaClient()

export default async function handle(req, res) {
    const data = await new Promise(function (resolve, reject) {
        const form = new formidable.IncomingForm();
        form.parse(req, function (err, fields, files) {
            const metadata = JSON.parse(fields["metadata"])
            const { name, description, ownerid, comment, datatype, pynumber, pystring } = metadata

            if (err) return reject(err);
            resolve({ fields, files });
        });
      });
      
    const {fields, files} = data
    const metadata = JSON.parse(fields["metadata"])
    const { name, 
            description, 
            ownerid, 
            comment, 
            datatype, 
            pynumber, 
            pystring, 
            datacolumnheader, 
            datacolumntype,
            schemaLabel1,
            schemaType1,
            schemaLabel2,
            schemaType2,
            schemaLabel3,
            schemaType3,
            schemaLabel4,
            schemaType4,
            schemaLabel5,
            schemaType5,
        } = metadata
    let jobj = null
        switch (datatype) {
            case "/datatypes/json": {
                const datacontents = {"contents": fs.readFileSync(files.jsonpath.path),
                                 "length": files.jsonpath.size,
                                 "type": files.jsonpath.type} 
                fs.unlinkSync(files.jsonpath.path)

                jobj = await prisma.jsonData.create( {
                    data: {
                        jsondata: JSON.stringify(datacontents),      
                        dobj: { create: {   owner: {connect: 
                                                    {id: ownerid}}, 
                                            comment: comment, 
                                            datatype: datatype,
                                            NameAssignment: { 
                                                create: {
                                                    ObjectName: {
                                                        create: {
                                                            owner: {connect: 
                                                            {id: ownerid}},
                                                            desc: description,
                                                            name: name,
                                                        }
                                                    }
                                                }
                                            }
                                        } 
                                },
                        } 
                });
                break;
            }
            case "/datatypes/csv": {
                const datacontents = {"contents": fs.readFileSync(files.csvpath.path),
                                 "length": files.csvpath.size,
                                 "type": files.csvpath.type} 
                fs.unlinkSync(files.csvpath.path)
                jobj = await prisma.csvData.create( {
                    data: {
                        csvdata: JSON.stringify(datacontents),      
                        dobj: { create: {   owner: {connect: 
                                                    {id: ownerid}}, 
                                            comment: comment, 
                                            datatype: datatype,
                                            NameAssignment: { 
                                                create: {
                                                    ObjectName: {
                                                        create: {
                                                            owner: {connect: 
                                                            {id: ownerid}},
                                                            desc: description,
                                                            name: name,
                                                        }
                                                    }
                                                }
                                            }
                                        } 
                                },
                        } 
                });
                break;
            }
            case "/datatypes/img": {
                const datacontents = {"contents": fs.readFileSync(files.imgpath.path),
                                 "length": files.imgpath.size,
                                 "type": files.imgpath.type} 
                fs.unlinkSync(files.imgpath.path)
                jobj = await prisma.imgData.create( {
                    data: {
                        csvdata: JSON.stringify(datacontents),      
                        dobj: { create: {   owner: {connect: 
                                                    {id: ownerid}}, 
                                            comment: comment, 
                                            datatype: datatype,
                                            NameAssignment: { 
                                                create: {
                                                    ObjectName: {
                                                        create: {
                                                            owner: {connect: 
                                                            {id: ownerid}},
                                                            desc: description,
                                                            name: name,
                                                        }
                                                    }
                                                }
                                            }
                                        } 
                                },
                        } 
                });
                break;
            }
            case "/datatypes/pynum": {
                jobj = await prisma.pyNumData.create( {
                    data: {
                        val: Number(pynumber),      
                        dobj: { create: { owner: {connect: {id: ownerid}}, 
                                            comment: comment, 
                                            datatype: datatype, 
                                            NameAssignment: {
                                                create: {
                                                    ObjectName: {
                                                        create: {
                                                            owner: {connect:
                                                                {id: ownerid}},
                                                                desc: description,
                                                                name: name,
                                                            }
                                                        }
                                                    }
                                                }
                                            } 
                                },
                        } 
                });
                break;
            }
            case "/datatypes/pystring": {
                jobj = await prisma.pyStrData.create( {
                    data: {
                        val: pystring,      
                        dobj: { create: { owner: {connect: {id: ownerid}}, 
                                            comment: comment, 
                                            datatype: datatype, 
                                            NameAssignment: {
                                                create: {
                                                    ObjectName: {
                                                        create: {
                                                            owner: {connect:
                                                                {id: ownerid}},
                                                                desc: description,
                                                                name: name,
                                                            }
                                                        }
                                                    }
                                                }
                                            } 
                                },
                        } 
                });
                break;
            }
            case "/datatypes/datacolumn": {
                jobj = await prisma.columnData.create( {
                    data: {
                        headerlabel: datacolumnheader,      
                        typedesc: datacolumntype,      
                        dobj: { create: { owner: {connect: {id: ownerid}}, 
                                          comment: comment, 
                                          datatype: datatype,
                                          NameAssignment: {
                                              create: {
                                                  ObjectName: {
                                                      create: {
                                                          owner: {connect:
                                                            {id: ownerid}},
                                                            desc: description,
                                                            name: name,
                                                      }
                                                  }
                                              }
                                          }  
                                    } 
                                },
                        } 
                });
                break;
            }
            case "/datatypes/schema": {
                var dataStruct = {}
                if (schemaLabel1) {
                    dataStruct.colname1 = schemaLabel1
                    dataStruct.coldesc1 = schemaType1
                }
                if (schemaLabel2) {
                    dataStruct.colname2 = schemaLabel2
                    dataStruct.coldesc2 = schemaType2
                }
                if (schemaLabel3) {
                    dataStruct.colname3 = schemaLabel3
                    dataStruct.coldesc3 = schemaType3
                }
                if (schemaLabel4) {
                    dataStruct.colname4 = schemaLabel4
                    dataStruct.coldesc4 = schemaType4
                }
                if (schemaLabel5) {
                    dataStruct.colname5 = schemaLabel5
                    dataStruct.coldesc5 = schemaType5
                }
                dataStruct.dobj = { create: { owner: {connect: {id: ownerid}}, 
                    comment: comment, 
                    datatype: datatype,
                    NameAssignment: {
                        create: {
                            ObjectName: {
                                create: {
                                    owner: {connect:
                                    {id: ownerid}},
                                    desc: description,
                                    name: name,
                                    }
                                }
                            }
                        }  
                        } 
                    }
                jobj = await prisma.schemaData.create( {
                    data: dataStruct});
                break;
            }
            default: {
                break;
            }
        }
    if (jobj) {
        const jobj2 = await prisma.timeline.create( {
            data: {
                op: "create",
                ref: {connect: {
                    id: jobj.dobjid
                }},
                owner: {connect: {
                    id: ownerid
                }}
            }
        })

        res.json({"resultcode": "success", "data": jobj})
    } else {
        res.json({"resultcode": "fail"})
    }
}

export const config = {
    api: {
      bodyParser: false,
    },
  };
