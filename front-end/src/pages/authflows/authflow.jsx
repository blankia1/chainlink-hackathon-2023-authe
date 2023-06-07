import { useCallback } from 'react';
import ReactFlow, { useNodesState, useEdgesState, addEdge, Handle, Position } from 'reactflow';

import 'reactflow/dist/style.css';
import './index.css';

const initialNodes = [
  { id: 'User', type: 'user', position: { x: 0, y: 150 } },
  { id: 'Approve', type: 'action', position: { x: 250, y: 0 } },
  { id: 'Transfer', type: 'action', position: { x: 250, y: 150 } },
  { id: 'Mint', type: 'action', position: { x: 250, y: 300 } },
  { id: 'Target', type: 'target', position: { x: 250, y: 450 } },
  { id: 'Contract', type: 'contract', position: { x: 450, y: 600 } },
  { id: 'Approve', type: 'effect', position: { x: 350, y: 600 } },
  { id: 'Deny', type: 'effect', position: { x: 350, y: 600 } },
];

const isValidConnection = (connection) => {
    // connection.target === 'B';

    if (connection.source === 'Transfer'){
        if (connection.target === 'Approve' || connection.target === 'Deny'){
            const test = { id: 'Mint', type: 'action', position: { x: 250, y: 300 } }
            return true
        }

        
    }
    return false
}
const onConnectStart = (_, { nodeId, handleType }) =>
  console.log('on connect start', { nodeId, handleType });
const onConnectEnd = (event) => console.log('on connect end', event);

const CustomInput = ({ id }) => (
  <>
    <div>{id}</div>
    <Handle type="source" position={Position.Right} />
  </>
);

const User = ({ id }) => (
    <>
      <div>{id}</div>
      <Handle type="source" position={Position.Right} />
    </>
  );

const Contract = ({ id }) => (
    <>
    <Handle type="target" position={Position.Left} />
    <div>{id}</div>
    <Handle type="source" position={Position.Right} />
    </>
  );

  const Effect = ({ id }) => (
    <>
    <Handle type="target" position={Position.Left} />
    <div>{id}</div>
    <Handle type="source" position={Position.Right} />
    </>
  );

  const Target = ({ id }) => (
    <>
    <Handle type="target" position={Position.Left} />
    <div>{id}</div>
    </>
  );

  const Action = ({ id }) => (
    <>
    <Handle type="target" position={Position.Left} />
    <div>{id}</div>
    <Handle type="source" position={Position.Right} />
    </>
  );

const CustomNode = ({ id }) => (
  <>
    <Handle type="target" position={Position.Left} />
    <div>{id}</div>
    <Handle type="source" position={Position.Right} />
  </>
);

const nodeTypes = {
  custominput: CustomInput,
  customnode: CustomNode,
  target: Target,
  contract: Contract,
  action: Action,
  user: User,
  effect: Effect,
};

const Authflow = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  const onConnect = useCallback((params) => setEdges((els) => addEdge(params, els)), []);

  return (
    <div style={{ height: 800 }}>
    <ReactFlow 
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onConnect={onConnect}
      isValidConnection={isValidConnection}
      selectNodesOnDrag={false}
      className="validationflow"
      nodeTypes={nodeTypes}
      onConnectStart={onConnectStart}
      onConnectEnd={onConnectEnd}
      fitView
      attributionPosition="bottom-left"
    />
    </div>
  );
};

export default Authflow;
