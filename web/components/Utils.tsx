import KnownLocation, { KnownLocationProps } from "./KnownLocation";
import MD5 from "crypto-js/md5";

export const isValidSubgraph = (
    graph, 
    nodes:  {
        id: any;
        color: string;
        x: number;
        y: number;
        labelPosition: string;
        }[],
    rootId: any, 
    selectedNodes: any[],
    ) => {
    // Valid Subgraph is defined as: being a graph where there is a single root and it is a complete sub tree
    // complete subtree means that it contains all the nodes in the original tree starting from the subtree root
    // visually: 
    //  x   x
    //   \ /
    //    x   x
    //     \ /
    //      x       
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
    let nodeIds = nodes.map(node => node.id);
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
    // console.log(depths);
    let src = [];
    let lowestDepth = depth+1;
    for (let id of selectedNodes) {
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
    let numIterations = 0;
    while (queue.length > 0) {
        let newQueue = [];
        for (let id of queue) {
            if (!selectedNodes.includes(id)) {
                return true;
            }
            if (graph.hasOwnProperty(id)) {
                for (let childId of graph[id]) {
                    newQueue.push(childId);
                }
            }
        }
        queue = newQueue;
        numIterations++;
    }    
    return (numIterations <= 1);
}

export const isValidSubgraphKnownLocations = (
    selectedSubgraphNodes: any[],
    dobj: KnownLocationProps
) => {
    // returns true if every node after once we begin to check for connectivity is selected
    if (selectedSubgraphNodes.length === 0 ) {
        return false;
    }
    let descendentData = dobj.descendentData;
    let visited = {}
    for (let node of selectedSubgraphNodes) {
        visited[node] = false;
    }
    let beginConnectivityCheck = false;
    let nodeCount = 1;

    let queue = [descendentData];
    while (queue.length > 0) {
        if (beginConnectivityCheck) {
            nodeCount++;
        }
        let node  = queue.shift();
        let identifier = (node.md5hash) ? node.md5hash : MD5(node.startedOn).toString();
        // checking to see if we have a valid start
        // TODO: I am unsure if we also want to include Sharing events as valid starts as well
        if (selectedSubgraphNodes.includes(identifier) 
            && !beginConnectivityCheck 
            && (node.kind === 'FileObservation' || node.kind === 'SharingEvent')
            ) {
            beginConnectivityCheck = true;
        }
        if (beginConnectivityCheck && !selectedSubgraphNodes.includes(identifier)) {
            return false;
        }
        for (let child of node.children) {
            queue.push(child)
        }

    }
    return beginConnectivityCheck && nodeCount > 1;
}


