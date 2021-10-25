import React from "react"
import { GetServerSideProps } from "next"
import Layout from "../../components/Layout"
import { UserSelect } from "@prisma/client"
import { Heading, Pane } from 'evergreen-ui'
import Dataobject, { DataobjProps } from "../../components/Dataobject"
import { Console } from "console"
import { useRouter } from 'next/router'


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
    const res = await fetch(`http://localhost:5000/dobjs/${context.query.id}`)
    const data = await res.json()

    let version = context.query.v ? context.query.v : data.versions[0].id

    const versionRes = await fetch(`http://localhost:5000/version/${version}`)
    const versionData = await versionRes.json()

    data.displayVersion = versionData

    return {props: {...data, ...context.query}}
  }

export default DataObj
