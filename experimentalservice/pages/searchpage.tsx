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
  const [searchTime, setSearchTime] = useState(false)
  const [searchTimeStart, setSearchTimeStart] = useState('')
  const [searchTimeEnd, setSearchTimeEnd] = useState('')

  const pairSeperator = ':';
  const validKeyNames = [
    'url',
    'owner',
    'comment',
    'pytype',
    'timestamp'
  ];

  function isValidKeyValuePair(input) {
    const possiblePair = input.split(pairSeperator);
    if (possiblePair.length == 2) {
      return validKeyNames.indexOf(possiblePair[0]) > -1;
    }
    return false;
  }
  function checkFieldSearch(searchTerms) {
    const searchTermList = searchTerms.split(' ')
    if (searchTermList.length == 1) {
      if (isValidKeyValuePair(searchTerms)) {
        return true;
      }
    }
    return false;
  }
  // this is function which handles your searchTerm
  function parseSearch(searchTerm) {
    return searchTerm.split(pairSeperator);
  }
  const submitData = async (e: React.SyntheticEvent) => {
    e.preventDefault()
    var searchField = ['url', 'comment', 'owner', 'pytype']
    if (fieldText === "") {
      searchField = ['url', 'comment', 'owner', 'pytype']
    } else {
      searchField = [fieldText]
    }
    console.log(searchField)

    try {
      if (searchTime) {
        var local_start = searchTimeStart
        var local_end = searchTimeEnd
        const res = await client.search({
          index: 'knps',
          body: {
            query: {
              range: {
                "timestamp": {
                  "gte": local_start,
                  "lte": local_end
                }
              }
            }
          }
        })
        for (const searchrst of res.hits.hits) {
          console.log('test:', searchrst);
        }
        setHits(res.hits.hits)
      } else {
        console.log(searchText)
        var parsed = [];
        var q;
        var f;
        if (checkFieldSearch(searchText)) {
          parsed = parseSearch(searchText);
          q = parsed[1];
          f = parsed[0];
        } else {
          q = searchText;
          f = searchField;
        }
        if (f === 'timestamp') {
          var local_start = searchTimeStart
          var local_end = searchTimeEnd
          if (searchTimeStart === "" || searchTimeEnd === "") {
            local_start = q[1].split(',')[0]
            local_end = q[1].split(',')[1]
          }
          console.log(local_start)
          console.log(local_end)
          const res = await client.search({
            index: 'knps',
            body: {
              query: {
                range: {
                  "timestamp": {
                    "gte": local_start,
                    "lte": local_end
                  }
                }
              }
            }
          })
          for (const searchrst of res.hits.hits) {
            console.log('test:', searchrst);
          }
          setHits(res.hits.hits)
        } else {
          const res = await client.search({
            index: 'knps',
            body: {
              query: {
                multi_match: {
                  query: q,
                  fields: f,
                  fuzziness: "AUTO"
                }
              }
            }
          })
          for (const searchrst of res.hits.hits) {
            console.log('test:', searchrst);
          }
          setHits(res.hits.hits)
        }
      }
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
          {/* <input
            onChange={e => setFieldText(e.target.value)}
            placeholder="Search Field. Leave empty for all fields"
            type="text"
            value={fieldText}
          /> */}

          {
            searchTime == true &&
            <input type="datetime-local" id="meeting-time"
              name="searching-time-start" step="1"
              onChange={e => setSearchTimeStart(e.target.value)} />
          }
          {
            searchTime == true &&
            <input type="datetime-local" id="meeting-time"
              name="searching-time-start" step="1"
              onChange={e => {
                setSearchTimeEnd(e.target.value);
              }}
            />
          }


          <input
            // disabled={!searchText}
            type="submit"
            value="Search"
          />
          <a className="back" href="#" onClick={() => Router.push('/')}>
            or Cancel
          </a>
          <br></br>
          <br></br>

          <button onClick={e => {
            if (searchTime) {
              setSearchTime(false)
              setSearchTimeStart('')
              setSearchTimeEnd('')
              setFieldText('')
              setSearchText('')
              setHits([])
            } else {
              setSearchTime(true)
              setSearchTimeStart('')
              setSearchTimeEnd('')
              setFieldText('')
              setSearchText('')
              setHits([])
            }
          }}>Search Time</button>


        </form>

      </div>

      <Heading size={800}>Search Results</Heading>
      <br></br>
      <main>
        {hits.length === 0 && <h1> No Matched Results</h1>}

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


      button {
        background: #ececec;
        border: 0;
        padding: 1rem 2rem;
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
