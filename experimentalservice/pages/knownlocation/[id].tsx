import React from "react"
import { GetServerSideProps } from "next"
import Layout from "../../components/Layout"
import { UserSelect } from "@prisma/client"
import { Heading, Pane } from 'evergreen-ui'
import KnownLocation, { KnownLocationProps } from "../../components/KnownLocation"
import { Console } from "console"
import { useRouter } from 'next/router'


  const KnownLocationObj: React.FC<KnownLocationProps> = (props) => {
    return (
      <Layout>
        <Pane>
          <KnownLocation dobj={props} />
        </Pane>
      </Layout>
    )
  }

export const getServerSideProps: GetServerSideProps = async (context) => {
    const res = await fetch(`http://localhost:5000/knownlocationdata/${context.query.id}`)
    const data = await res.json()

    return {props: {...data, ...context.query}}
  }

export default KnownLocationObj
