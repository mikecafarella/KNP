import { PrismaClient } from '@prisma/client'
const formidable = require('formidable')
const micro = require('micro')

const prisma = new PrismaClient()

export default async function handle(req, res) {

    const promise = new Promise((resolve, reject) => {
        const form = formidable({multiples:true})

        form.parse(req, (err, fields, files) => {
            const { name, description, comment, datatype, imagepath, csvpath, jsonpath, pynumber, pystring, ownerId } = fields

            let jobj = null
            switch (datatype) {
                case "/datatypes/json": {
                    jobj = await prisma.jsonData.create( {
                        data: {
                            jsondata: jsonpath,      
                            dobj: { create: { owner: {connect: {id: ownerId}}, 
                                              name: name, 
                                              desc: description, 
                                              comment: comment, 
                                              datatype: datatype } },
                            } 
                    });
                    break;
                }
                case "/datatypes/csv": {
                    jobj = await prisma.csvData.create( {
                        data: {
                        csvdata: "csvdatagoeshere",      
                        dobj: { create: { owner: {connect: {id: ownerId}}, 
                                              name: name, 
                                              desc: description, 
                                              comment: comment, 
                                              datatype: datatype } },
                            } 
                    });
                    break;
                }
                case "/datatypes/img": {
                    jobj = await prisma.imgData.create( {
                        data: {
                        img: "imagedatagoeshere",      
                        dobj: { create: { owner: {connect: {id: ownerId}}, 
                                      name: name, 
                                      desc: description, 
                                      comment: comment, 
                                      datatype: datatype } },
                        } 
                    });
                    break;
                }
                case "/datatypes/pynum": {
                    jobj = await prisma.pyNumData.create( {
                        data: {
                        val: Number(pynumber),      
                        dobj: { create: { owner: {connect: {id: ownerId}}, 
                                          name: name, 
                                          desc: description, 
                                          comment: comment, 
                                          datatype: datatype } },
                        } 
                    });
                    break;
                }
                case "/datatypes/pystring": {
                    jobj = await prisma.pyStrData.create( {
                        data: {
                        val: pystring,      
                        dobj: { create: { owner: {connect: {id: ownerId}}, 
                                          name: name, 
                                          desc: description, 
                                          comment: comment, 
                                          datatype: datatype } },
                        } 
                    });
                    break;
                }
                default: {
                    break;
                }
            }
        })
    }

    if (jobj) {
        res.json({"resultcode": "success", "data": jobj})
    } else {
        res.json({"resultcode": "fail"})
    }
    )}
}

