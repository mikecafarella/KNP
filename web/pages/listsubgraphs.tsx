import React, {useState, useEffect} from "react"
import { GetServerSideProps } from "next"
import Layout from "../components/Layout"
import Router from 'next/router'
import { Table, Heading, Combobox, Pane, Paragraph, Strong } from 'evergreen-ui'
import {SubgraphNodeProps} from '../components/KnownLocation'

type Props = {
    labels: string[]
}

const SubGraphs: React.FC<Props> = (props) => {
    const subgraphsUrl = '/api/subgraphs';
    const [label, setLabel] = useState('');
    const [email, setEmail] = useState('');
    const [emails, setEmails] = useState([]);

    const [displayedSubgraphs, setDisplayedSubgraphs] = useState<SubgraphNodeProps[]>([]);

    const fetcher = async (url) => {
      let data = await fetch(url, {
          method: "GET",
      }).then(res=>res.json());
      setDisplayedSubgraphs(data.subgraphs);   
      setEmails(data.emails);   
      return data;   
    }

    useEffect(()=> {
      if (label) {
        fetcher(`${subgraphsUrl}/${label}`);
      } 
    }, [label])

    const handleEmailSelection = (selected) => {
      setEmail(selected);
    }

    let displayed = [];

    if (email) {
        displayed = displayedSubgraphs.filter(node => node.ownerEmail === email);
    } else {
        displayed = displayedSubgraphs;
    }

    return (
      <Layout>
          <Heading size={800}>Labeled Operator KNPS Provenance Subgraphs</Heading>
          <Pane display='flex' flexDirection='column'>
            <Paragraph marginY="0.5em"> <Strong>Select an Operator to View Labeled Subgraphs Of</Strong></Paragraph>
            <Combobox
                items={props.labels}
                onChange={selected => setLabel(selected)}
                placeholder="Choose a Operator to View Subgraphs of"
                autocompleteProps={{
                    // Used for the title in the autocomplete.
                    title: 'label'
                }}
                marginBottom="0.5em"/>

            {(label) ? 
              (displayedSubgraphs.length > 0) ?
              <Pane>
                <Paragraph marginY="0.5em"> Select an Email to View Operators Labeled by Specific Users</Paragraph>
                  <Combobox
                    items={emails}
                    onChange={handleEmailSelection}
                    placeholder="Choose a user to View Subgraphs of"
                    autocompleteProps={{
                        // Used for the title in the autocomplete.
                        title: 'email'
                    }}
                    marginBottom="0.5em"/> 
                </Pane>
                : <Paragraph marginY="0.5em">There are no labeled subgraphs for Operator: {label}</Paragraph>
              : <></>}
          </Pane>
          <Table>
            <Table.Head>
              <Table.TextHeaderCell>
                Output File Full Name
              </Table.TextHeaderCell>
              <Table.TextHeaderCell>
                Output File Short Name
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
               {displayed.map(obj => (
               <Table.Row key={obj.uuid} isSelectable onSelect={() => Router.push({pathname: `/knownlocation/${obj.provenanceGraphRootId}`, query: {root: obj.subgraphRootName, label: obj.label, uuid: obj.uuid}})}>
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
    const res = await fetch("http://localhost:5000/operator")
    const data = await res.json()
    return {
      props: { labels: data.labels },
    }
  }
  
  export default SubGraphs