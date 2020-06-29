#!/usr/bin/env python
#import utils
from neo4j import GraphDatabase

class HelloWorldExample:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def print_greeting(self, message):
        with self.driver.session() as session:
            returnedItem = session.write_transaction(self._getWikidataEntity, message)
            print(greeting)

    @staticmethod
    def _getWikidataEntity(tx, qId):
        query = tx.run('MATCH (n:Resource:ns0__Item { uri: "http://www.wikidata.org/entity/$qid" }) ' +
                       'RETURN n ' +
                       'LIMIT 1', qid=qId)
        return result.single()[0]


if __name__ == "__main__":
    greeter = HelloWorldExample("bolt://gelato.eecs.umich.edu:7687", "neo4j", "gelato")
    try:
        # Get Biden
        greeter.print_greeting("Q6279")
    finally:
        greeter.close()

