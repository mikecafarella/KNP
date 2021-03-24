import React from "react"
import { GetServerSideProps } from "next"
import Layout from "../../components/Layout"
import { UserSelect } from "@prisma/client"
import { Heading, Pane } from 'evergreen-ui'
import Dataobject, { DataobjProps } from "../../components/Dataobject"
import { Console } from "console"
import { useRouter } from 'next/router'


  const DataObj: React.FC<DataobjProps> = (props) => {
    console.log(props)
    return (
      <Layout>
        <Pane>
          <Dataobject dobj={props} />
        </Pane>
      </Layout>
    )
  }

export const getServerSideProps: GetServerSideProps = async (context) => {
    console.log(context.query)
    let version = context.query.v ? '?v=' + context.query.v : ''
    const res = await fetch(`http://localhost:3000/api/dobj/${context.query.id}${version}`)
    const data = await res.json()
    return {props: {...data, ...context.query}}
  }

export default DataObj
