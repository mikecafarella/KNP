import React, { useState } from 'react'
import Router from 'next/router'
import Layout from '../components/Layout'
import SearchRst, { SearchRstProps } from "../components/SearchRst"
import { Heading } from 'evergreen-ui'

// let hits = []

const SearchPage: React.FC = () => {
  const [searchText, setSearchText] = useState('')
  const [hits, setHits] = useState([])



  // curl -X GET 'localhost:9200/kgpl/_search' -H 'Content-Type: application/json' -d'
  // {
  //   "query": {
  //     "multi_match": {
  //         "query": "Int",
  //         "fields": [ "url", "comment", "owner", "pytype" ] 
  //     }
  //   }
  // }' > zjyout.json

  const submitData = async (e: React.SyntheticEvent) => {
    e.preventDefault()
    try {
      // const body = {searchText}
      const body = {
        "query": {
          "multi_match": {
            "query": { searchText },
            "fields": ["url", "comment", "owner", "pytype"]
          }
        }
      }
      // const res = await fetch(`http://localhost:9200/kgpl/_search`, {
      //   method: 'GET',
      //   headers: { 'Content-Type': 'application/json' },
      //   // body: JSON.stringify(body),
      // })
      const res = await fetch("http://localhost:9200/kgpl/_search")
      const data = await res.json()
      setHits(data.hits.hits)
      this.forceUpdate();
    } catch (error) {
      console.error(error)
    }
  }

  return (
    <Layout>
      <div className="page">
        <form
          onSubmit={submitData}>
          <h1>Search</h1>
          <input
            autoFocus
            onChange={e => setSearchText(e.target.value)}
            placeholder="Search Object"
            type="text"
            value={searchText}
          />
          <input
            disabled={!searchText}
            type="submit"
            value="Search"
          />
          <a className="back" href="#" onClick={() => Router.push('/')}>
            or Cancel
        </a>
        </form>
      </div>

        <Heading size={800}>Search Results</Heading>
        <br></br>
        <main>
          {hits.map((s) => (
            <div key={s._id} className="SearchRst">
              <SearchRst searchrst={s} />
            </div>
          ))}
        </main>

      <style jsx>{`
      .page {
        background: white;
        padding: 3rem;
        display: flex;
        justify-content: center;
      }

      input[type='text'] {
        width: 100%;
        padding: 0.5rem;
        margin: 0.5rem 0;
        border-radius: 0.25rem;
        border: 0.125rem solid rgba(0, 0, 0, 0.2);
      }

      input[type='submit'] {
        background: #ececec;
        border: 0;
        padding: 1rem 2rem;
      }

      .back {
        margin-left: 1rem;
      }
    `}</style>
    </Layout>
  )
}

export default SearchPage
// export { hits, SearchPage }