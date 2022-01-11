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
    selectedNodes: any[], ) => {
    // Valid Subgraph is defined as: being
    // return true only if the subgraph is connected
    // and has to be a tree 
    if (selectedNodes.length <= 1 ) {
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
    let visited = {};
    let lowestDepth = depth+1;
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
    let numIterations = 0;
    while (queue.length > 0) {
        let newQueue = [];
        for (let id of queue) {
            if (graph.hasOwnProperty(id)) {
                for (let childId of graph[id]) {
                    if (!selectedNodes.includes(childId)) {
                        return true;
                    } else {
                        newQueue.push(childId);
                    }
                }
            }
        }
        queue = newQueue;
        numIterations++;
    }
    return !(numIterations > 1);
}

