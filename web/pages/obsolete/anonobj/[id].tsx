import React from "react"
import { GetServerSideProps } from "next"
import Layout from "../../components/Layout"
import { UserSelect } from "@prisma/client"
import { Heading, Pane } from 'evergreen-ui'
import AnonymousDataobject, { AnonymousDataobjProps } from "../../components/AnonymousDataobject"
import { Console } from "console"


  const AnonDataObj: React.FC<AnonymousDataobjProps> = (props) => {
    return (
      <Layout>
        <Pane>
          <AnonymousDataobject dobj={props} />
        </Pane>
      </Layout>
    )
  }
  
export const getServerSideProps: GetServerSideProps = async (context) => {
    const res = await fetch(`http://localhost:3000/api/anonobj/${context.query.id}`)
    const data = await res.json()
    return {props: {...data}}
  }
  
export default AnonDataObj