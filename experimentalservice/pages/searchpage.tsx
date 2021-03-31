import React, { useState } from 'react'
import Router from 'next/router'
import Layout from '../components/Layout'
import SearchRst, { SearchRstProps } from "../components/SearchRst"
import { Heading } from 'evergreen-ui'
var elasticsearch = require('elasticsearch');
var client = new elasticsearch.Client({
  host: 'localhost:9200'
});

const SearchPage: React.FC = () => {
  const [searchText, setSearchText] = useState('')
  const [hits, setHits] = useState([])
  const [fieldText, setFieldText] = useState('')


  const submitData = async (e: React.SyntheticEvent) => {
    e.preventDefault()
    var searchField =  [ 'url', 'comment', 'owner', 'pytype' ]
    if (fieldText===""){
      searchField =  [ 'url', 'comment', 'owner', 'pytype' ]
    }else{
      searchField =  [fieldText]
    }
    try {
      const res = await client.search({
        index: 'kgpl',
        body: {
          query: {
            multi_match: {
              query: searchText,
              fields: searchField,
              fuzziness: "AUTO"
            }
          }
        }
      })

      for (const searchrst of res.hits.hits) {
        console.log('test:', searchrst);
      }

      setHits(res.hits.hits)
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
          onChange={e => setFieldText(e.target.value)}
          placeholder="Search Field. Leave empty for all fields"
          type="text"
          value={fieldText}
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
        { hits.length===0 && <h1> No Matched Results</h1> }
        
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