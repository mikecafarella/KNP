import KnownLocation, { KnownLocationProps } from "./KnownLocation";
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

export const getMD5 = (nodeDatum) => {
    let md5;
    if (nodeDatum.md5hash) {
      md5 = nodeDatum.md5hash;
    } else if (nodeDatum.startedOn) {
      md5 = MD5(nodeDatum.startedOn).toString();
    } else {
      md5 = MD5(nodeDatum.receivedOnOrBefore).toString();
    }
    return md5;
  }

//can clean this up if we need to, might give a slight performance boost also if the provenance graphs get a lot bigger,
//but would also be better to make this a backend call if it comes down to it 
export const isValidSubgraphKnownLocations = (
    selectedSubgraphNodes: any[],
    dobj: KnownLocationProps
) => {
    if (selectedSubgraphNodes.length <= 1 ) {
        return false;
    }
    let descendentData = dobj.descendentData;
    let visited = {}
    let depth = 0;
    let depths = {}
    let queue = [descendentData];
    while (queue.length > 0) {
        let newQueue = [];
        for (let node of queue) {
            let nodeMD5 = getMD5(node);
            depths[nodeMD5] = depth;
            for (let child of node.children) {
                newQueue.push(child);
            }
        }
        depth++;
        queue = newQueue;
    }
    let src = [];
    let curMinDepth = depth+1;
    for (let node of selectedSubgraphNodes) {
        visited[node] = false;
        if (depths[node] < curMinDepth) {
            src = [node];
            curMinDepth = depths[node];
        } else if (depths[node] == curMinDepth) {
            src.push(node);
        }
    }
    if (src.length > 1) {
        return false;
    }
    let foundSrc = false;
    queue = [descendentData];
    let srcID = src[0];
    while (queue.length > 0) {        
        let node  = queue.shift();
        let identifier = getMD5(node);
        if (identifier === srcID) {
            foundSrc = true;
        }
        if (!selectedSubgraphNodes.includes(identifier) && foundSrc) {
            return false;
        }
        if (visited.hasOwnProperty(identifier)) {
            visited[identifier] = true;
            // if we have visited all nodes in our subgraph 
            if (node.kind === 'FileObservation' && Object.values(visited).reduce((ans, cur) => cur && ans, true)) {
                return true;
            }
        }
        for (let child of node.children) {
            queue.push(child)
        }

    }
    return true;
}


