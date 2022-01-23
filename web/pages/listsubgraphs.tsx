import React, {useState, useEffect} from "react"
import { GetServerSideProps } from "next"
import Layout from "../components/Layout"
import Router from 'next/router'
import { Table, Heading, Combobox, Pane } from 'evergreen-ui'
import {SubgraphNodeProps} from '../components/KnownLocation'

type Props = {
    subgraphs: SubgraphNodeProps[]
    emails: string[],
    labels: string[]
}

const SubGraphs: React.FC<Props> = (props) => {
    let displayedSubgraphs = [...props.subgraphs];
    const [label, setLabel] = useState('');
    const [email, setEmail] = useState('');

    if (label) {
        displayedSubgraphs = displayedSubgraphs.filter(node => node.label === label);
    }
    if (email) {
        displayedSubgraphs = displayedSubgraphs.filter(node => node.ownerEmail === email);
    }

    return (
      <Layout>
          <Heading size={800}>Labeled KNPS Provenance Subgraphs</Heading>
          <Pane display='flex' flexDirection='row' width='19%'>
            <Combobox
                items={props.labels}
                onChange={selected => setLabel(selected)}
                placeholder="choose a label to filter by"
                autocompleteProps={{
                    // Used for the title in the autocomplete.
                    title: 'label'
                }}/>

            <Combobox
                items={props.emails}
                onChange={selected => setEmail(selected)}
                placeholder="choose email to filter by"
                autocompleteProps={{
                    // Used for the title in the autocomplete.
                    title: 'email'
                }}/>
          </Pane>
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
              <Table.TextHeaderCell>
                Modified Time
              </Table.TextHeaderCell>
            </Table.Head>
            <Table.Body>
               {displayedSubgraphs.map(obj => (
               <Table.Row key={obj.uuid} isSelectable onSelect={() => Router.push({pathname: `/knownlocation/${obj.subgraphRootId}`, query: {root: obj.subgraphRootName, label: obj.label, uuid: obj.uuid}})}>
                  <Table.TextCell>{obj.fullRootFileName}</Table.TextCell>
                  <Table.TextCell>{obj.subgraphRootName}</Table.TextCell>
                  <Table.TextCell>{obj.label}</Table.TextCell>
                  <Table.TextCell>{obj.owner}</Table.TextCell>
                  <Table.TextCell>{obj.ownerEmail}</Table.TextCell>
                  <Table.TextCell>{obj.modified}</Table.TextCell>
               </Table.Row>
              ))}
            </Table.Body>
          </Table>
      </Layout>
    )
  }
  
  export const getServerSideProps: GetServerSideProps = async () => {
    const res = await fetch("http://localhost:5000/subgraphs")
    const data = await res.json()
    return {
      props: { subgraphs: data.subgraphs, emails: data.emails, labels: data.labels },
    }
  }
  
  export default SubGraphs