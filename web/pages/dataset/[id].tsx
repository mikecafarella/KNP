import React from "react"
import { GetServerSideProps } from "next"
import Layout from "../../components/Layout"
import { UserSelect } from "@prisma/client"
import { Heading, Pane } from 'evergreen-ui'
import Dataset, { DatasetProps } from "../../components/Dataset"
import { Console } from "console"
import { useRouter } from 'next/router'

  const DatasetObj: React.FC<DatasetProps> = (props) => {
    return (
      <Layout>
        <Pane>
          <Dataset dobj={props} />
        </Pane>
      </Layout>
    )
  }

export const getServerSideProps: GetServerSideProps = async (context) => {
    const res = await fetch(`http://localhost:5000/dataset/${context.query.id}`)
    const data = await res.json()

    return {props: {...data, ...context.query}}
  }

export default DatasetObj
