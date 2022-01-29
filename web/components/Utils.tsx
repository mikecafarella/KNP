import KnownLocation, { KnownLocationProps, SubgraphNodeProps } from "./KnownLocation";
import MD5 from "crypto-js/md5";

export const isValidSubgraph = (
    graph, 
    nodeIds: any[],
    rootId: any, 
    selectedNodes: any[],
    ) => {
    // Valid Subgraph is defined as: being a graph where there is a single root and it is a complete sub tree
    // complete subtree means that it contains all the nodes in the original tree starting from the subtree root
    // visually: 
    //  x   x                            
    //   \ /                               
    //    x   x        also   x   x  also  x   x
    //     \ /                 \ /          \ /
    //      x                   x            x   x
    //                                        \ /
    //                                         x
    //   this is a validSubgraph (doing a dataset join) if the original graph looks like:
    //  x   x             x   x
    //   \ /               \  /
    //    x   x              x   x
    //     \ /       or       \ /
    //      x                  x   x   
    //       \                  \ /
    //        X                  x
    // 
    // x
    //  \
    //   x
    //    \
    //     x
    //  this is a validSubgraph (applying a function to a single dataset) if the original graph looks like:
    // x               x
    //  \               \
    //   x               x
    //    \               \
    //     x     or        x   x
    //      \               \ /
    //       x               x

    if (selectedNodes.length <= 1) {
        return true;
    }
    let depths = {}
    for (let nodeId of nodeIds) {
        depths[nodeId] = 0;
    }
    let queue = [rootId];
    let depth = 0;
    while (queue.length > 0) {
        let newQueue = [];
        for (let nodeId of queue) {
            depths[nodeId] = depth;
            if (graph.hasOwnProperty(nodeId)) {
                for (let childId of graph[nodeId]) {
                    newQueue.push(childId);
                }
            }  
        }
        depth++;
        queue = newQueue;
    }
    let src = [];
    let lowestDepth = depth+1;
    let visited = {};
    for (let id of selectedNodes) {
        visited[id] = false;
        if (depths[id] < lowestDepth) {
            src = [id];
            lowestDepth = depths[id];
        } else if (depths[id] == lowestDepth) {
            src.push(id);
        }
    }
    // impossible to have valid subgraph
    if (src.length > 1) {
        return true;
    }
    queue = src;
    while (queue.length > 0) {
        let id = queue.shift();
        if (!selectedNodes.includes(id)) {
            return true;
        }
        if (visited.hasOwnProperty(id)) {
            visited[id] = true;
            if (Object.values(visited).reduce((ans, cur) => cur && ans, true)) {
                return false;
            }
        }
        if (graph.hasOwnProperty(id)) {
            for (let childId of graph[id]) {
                queue.push(childId);
            }
        }
    } 
    return false;
}

export const getUUID = (nodeDatum) => {
    let uuid;
    if (nodeDatum.uuid) {
      uuid = nodeDatum.uuid;
    } else {
      uuid = MD5(nodeDatum.receivedOnOrBefore).toString();
    }
    return uuid;
  }

//can clean this up if we need to, might give a slight performance boost also if the provenance graphs get a lot bigger,
//but would also be better to make this a backend call if it comes down to it 
export const isValidSubgraphKnownLocations = (
    selectedSubgraphNodesObj: any[],
    dobj: KnownLocationProps
) => {
    let selectedSubgraphNodes = selectedSubgraphNodesObj.map(nd => nd.uuid);
    if (selectedSubgraphNodes.length <= 1 ) {
        return {validSubgraph: false, rootNode: 'invalid', rootNodeLongName: 'invalid', rootId: 'invalid'};
    }
    let descendentData = dobj.descendentData;
    let visited = {}
    // let depth = 0;
    // let depths = {}
    // let queue = [descendentData];
    // while (queue.length > 0) {
    //     let newQueue = [];
    //     for (let node of queue) {
    //         let nodeUUID = getUUID(node);
    //         depths[nodeUUID] = depth;
    //         for (let child of node.children) {
    //             newQueue.push(child);
    //         }
    //     }
    //     depth++;
    //     queue = newQueue;
    // }
    let src = [];
    let curMinDepth = Infinity;
    for (let node of selectedSubgraphNodesObj) {
        visited[node.uuid] = false;
        if (node.depth < curMinDepth) {
            src = [node.uuid];
            curMinDepth = node.depth;
        } else if (node.depth == curMinDepth) {
            src.push(node.uuid);
        }
    }
    if (src.length > 1) {
        return {validSubgraph: false, rootNode: 'invalid', rootNodeLongName: 'invalid', rootId: 'invalid'};
    }
    let foundSrc = false;
    let queue = [descendentData];
    let srcID = src[0];
    let rootNodeName;
    let rootNodeLongName;
    let rootId;
    while (queue.length > 0) {   
        let node  = queue.shift();
        let identifier = getUUID(node);
        if (identifier === srcID) {
            //found the start, it must be a file observation
            if (node.kind !== 'FileObservation') {
                return {validSubgraph: false, rootNode: 'invalid', rootNodeLongName: 'invalid', rootId: 'invalid'}
            }
            foundSrc = true;
            rootNodeName = node.shortName;
            rootNodeLongName = node.longName;
            rootId = node.uuid;
        }
        if (!selectedSubgraphNodes.includes(identifier) && foundSrc) {
            return {validSubgraph: false, rootNode: 'invalid', rootNodeLongName: 'invalid', rootId: 'invalid'};
        }
        if (visited.hasOwnProperty(identifier)) {
            visited[identifier] = true;
            // if we have visited all nodes in our subgraph 
            if (node.kind === 'FileObservation' && Object.values(visited).reduce((ans, cur) => cur && ans, true) && foundSrc) {
                return {validSubgraph: true, rootNode: rootNodeName, rootNodeLongName: rootNodeLongName, rootId}
            }
        }
        for (let child of node.children) {
            queue.push(child)
        }

    }
    return {validSubgraph: true, rootNode: rootNodeName, rootNodeLongName: rootNodeLongName, rootId};
}

// credit to here: https://flexiple.com/javascript-array-equality/
export function arrayEquals(a: any[], b: any[]) {
    return Array.isArray(a) &&
        Array.isArray(b) &&
        a.length === b.length &&
        a.every((val, index) => val === b[index]);
}

export function getSelectedSubgraphInfo(node: SubgraphNodeProps) {
    return JSON.parse(node.subgraphNodesInfo);
}


