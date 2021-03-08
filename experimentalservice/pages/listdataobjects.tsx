import React from "react"
import { GetServerSideProps } from "next"
import Layout from "../components/Layout"
import Router from 'next/router'
import User, { UserProps } from "../components/User"
import { UserSelect } from "@prisma/client"
import { Table, Heading } from 'evergreen-ui'
import Header from "../components/Header"


type DataObjectProps = {
    id: number;
    timestamp: string;
    datatype: string;
}

type Props = {
  dobjs: DataObjectProps[]
}

const DataObjects: React.FC<Props> = (props) => {
  return (
    <Layout>
        <Heading size={800}>Data Objects</Heading>
        <Table>
          <Table.Head>
            <Table.TextHeaderCell>
                 Object Id
            </Table.TextHeaderCell>
            <Table.TextHeaderCell>
              Name
            </Table.TextHeaderCell>
            <Table.TextHeaderCell>
              Description
            </Table.TextHeaderCell>
            <Table.TextHeaderCell>
              Datatype
            </Table.TextHeaderCell>
            <Table.TextHeaderCell>
              Timestamp
            </Table.TextHeaderCell>
            <Table.TextHeaderCell>
              Comment
            </Table.TextHeaderCell>
            <Table.TextHeaderCell>
              Owner
            </Table.TextHeaderCell>
          </Table.Head>
          <Table.Body>
             {props.dobjs.map(obj => (
             <Table.Row key={obj.id} isSelectable onSelect={() => Router.push(`/dobj/X${obj.id}`)}>
                <Table.TextCell>X{obj.id}</Table.TextCell>
                <Table.TextCell>{obj.name}</Table.TextCell>
                <Table.TextCell>{obj.desc}</Table.TextCell>
                <Table.TextCell>{obj.version.dobj.datatype}</Table.TextCell>
                <Table.TextCell>{obj.version.timestamp}</Table.TextCell>
                <Table.TextCell>{obj.version.dobj.comment}</Table.TextCell>
                <Table.TextCell>{obj.owner.name}</Table.TextCell>
             </Table.Row>
            ))}
          </Table.Body>
        </Table>
    </Layout>
  )
}

export const getServerSideProps: GetServerSideProps = async () => {
  const res = await fetch("http://localhost:3000/api/listdataobjects")
  const dobjs = await res.json()
  return {
    props: { dobjs },
  }
}

export default DataObjects
