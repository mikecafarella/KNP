import React from "react"
import { GetServerSideProps } from "next"
import Layout from "../../components/Layout"
import { UserSelect } from "@prisma/client"
import { Heading, Pane } from 'evergreen-ui'
import Dataobject, { DataobjProps } from "../../components/Dataobject"
import { Console } from "console"


  const DataObj: React.FC<DataobjProps> = (props) => {
    return (
      <Layout>
        <Pane>
          <Dataobject dobj={props} />
        </Pane>
      </Layout>
    )
  }
  
export const getServerSideProps: GetServerSideProps = async (context) => {
    const res = await fetch(`http://localhost:3000/api/dobj/${context.query.id}`)
    const data = await res.json()
    return {props: {...data}}
  }
  
export default DataObj