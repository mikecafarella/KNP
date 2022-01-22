import React from "react"
import { GetServerSideProps } from "next"
import Layout from "../components/Layout"
import Router from 'next/router'
import { Table, Heading } from 'evergreen-ui'
import {SubgraphNodeProps} from '../components/KnownLocation'

type Props = {
    subgraphs: SubgraphNodeProps[]
}

const SubGraphs: React.FC<Props> = (props) => {
    return (
      <Layout>
          <Heading size={800}>Labeled KNPS Provenance Subgraphs</Heading>
          <Table>
            <Table.Head>
              <Table.TextHeaderCell>
                Root Node Full Name
              </Table.TextHeaderCell>
              <Table.TextHeaderCell>
                Root Node Short Name
              </Table.TextHeaderCell>
              <Table.TextHeaderCell>
                Label
              </Table.TextHeaderCell>
              <Table.TextHeaderCell>
                Labeler 
              </Table.TextHeaderCell>
              <Table.TextHeaderCell>
                Labeler Email
              </Table.TextHeaderCell>
            </Table.Head>
            <Table.Body>
               {props.subgraphs.map(obj => (
               <Table.Row key={obj.uuid} isSelectable onSelect={() => Router.push({pathname: `/knownlocation/${obj.subgraphRootId}`, query: {root: obj.subgraphRootName, label: obj.label, indexNum: obj.indexNum}})}>
                  <Table.TextCell>{obj.fullRootFileName}</Table.TextCell>
                  <Table.TextCell>{obj.subgraphRootName}</Table.TextCell>
                  <Table.TextCell>{obj.label}</Table.TextCell>
                  <Table.TextCell>{obj.owner}</Table.TextCell>
                  <Table.TextCell>{obj.ownerEmail}</Table.TextCell>
               </Table.Row>
              ))}
            </Table.Body>
          </Table>
      </Layout>
    )
  }
  
  export const getServerSideProps: GetServerSideProps = async () => {
    const res = await fetch("http://localhost:5000/subgraphs")
    const subgraphs = await res.json()
    return {
      props: { subgraphs },
    }
  }
  
  export default SubGraphs