import { PrismaClient } from '@prisma/client'
const formidable = require('formidable')
import fs from "fs";

const prisma = new PrismaClient()

export default async function handle(req, res) {
    const data = await new Promise(function (resolve, reject) {
        const form = new formidable.IncomingForm();
        form.parse(req, function (err, fields, files) {
            const metadata = JSON.parse(fields["metadata"])
            const { deleteId, ownerid } = metadata

            if (err) return reject(err);
            resolve({ fields, files });
        });
      });

      
    const {fields, files} = data
    const metadata = JSON.parse(fields["metadata"])
    const { deleteId, 
            ownerid,
        } = metadata
    console.log("Upload info", metadata)
    console.log("Deleting item" + deleteId)

    const jobj = await prisma.objectName.updateMany( {
        where: {id: deleteId},
        data: {
            isdeleted: 1,
        },
    })

    if (jobj) {
        console.log("Timeline for " + ownerid)
        const jobj2 = await prisma.timeline.create( {
            data: {
                op: "delete",
                ref: {connect: {
                    id: deleteId
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


