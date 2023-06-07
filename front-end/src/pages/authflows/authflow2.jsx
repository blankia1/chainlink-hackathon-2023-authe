import { useNavigate } from 'react-router-dom';

import { useEffect, useCallback, useState } from 'react';
import ReactFlow, {
  ReactFlowProvider,
  Panel,
  useReactFlow,
  addEdge,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
} from 'reactflow';

import { nodes as initialNodes, edges as initialEdges } from './MainExample/initial-elements';
import CustomNode from './MainExample/ContractNode';
import ProxyNode from './MainExample/ProxyNode';
import ContractNode from './MainExample/ProxyNode';
import axios from 'axios';
import { useAccount } from 'wagmi'

import 'reactflow/dist/style.css';
import './MainExample/overview.css';
import './MainExample/overview-proxy.css';
import './MainExample/overview-contract.css';


const nodeTypes = {
  custom: CustomNode,
  proxy: ProxyNode,
  contract: ContractNode,
};

const minimapStyle = {
  height: 120,
};

const onInit = (reactFlowInstance) => console.log('flow loaded:', reactFlowInstance);


const flowKey = 'example2-flow';



const Authflow = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [rfInstance, setRfInstance] = useState(null);
  const { setViewport } = useReactFlow();

  const onConnect = useCallback((params) => setEdges((eds) => addEdge(params, eds), params)), []);
  const navigate = useNavigate();
  const [session, setSession] = useState({});

  let connected_actions = []
  const { address, isConnected } = useAccount()

  useEffect(() => {
    axios(`${process.env.REACT_APP_SERVER_URL}/authenticate`, {
      withCredentials: true,
    })
      .then(({ data }) => {
        const { iat, ...authData } = data; // remove unimportant iat value

        setSession(authData);
      })
      .catch((err) => {
        console.log(err)
        navigate('/signin');
      });
  }, []);

  const permission_document = {
    "address": "0x71C7656EC7ab88b098defB751B7401B5f6d8976F",
    "status": "draft",
    "chain": "sepolia",
    "signature": "SIGNATURE_HERE",
    "permission_document": { 
        "Version": "2023-05-11",
        "Statement": [
            {
                "Resource": [
                    "*"
                ],
                "Effect": "Allow",
                "Action": [
                    "*"
                ],
                "Principal": [
                    "*"
                ],
                "Sid": "AllowAllPermissions"
            }
        ],
        "Signature": "9434903948034389439843834900920-320-3-2024904209429049033490430--340"
    }
}

  const onEdgeUpdateEnd = () => {
        console.log('onEdgeUpdateEnd loaded:')

  };

const onSave = useCallback(() => {
    console.log('Save button clicked:');

    if (rfInstance) {
        const flow = rfInstance.toObject();
        localStorage.setItem(flowKey, JSON.stringify(flow));
      }

    async function createDraftPermissionDocumentsVersion() {
        // const url = `${apiUrl}/${resource}`;
        console.log("Sending the request")
        const flow = rfInstance.toObject();
        console.log(flow)

        const url = "https://api.authe.io/public/ANY/v0/utils/extract-auth-flow?address=" + address
        const { data, status } = await axios.post(
            url,
            JSON.stringify(flow)
          );
      
        console.log("Permission document draft created with id: " + data.id)
        navigate('/permission-documents/edit/' + data.id);

        return {
            data,
        };

        // navigate('/permission-documents');
    }

    createDraftPermissionDocumentsVersion()
  }, [rfInstance]);

  const onExit = () => {
    console.log('Exit button clicked:');
    // redirect to /permission-documents
    navigate('/permission-documents');
  } 

  const isValidConnection = (connection) => {
    console.log(connection)

    // if connection source is user then only allow action connections
    if (connection.source === 'user'){
        if (connection.target.includes("action") ){
            connected_actions.indexOf(connection.target) === -1 ? connected_actions.push(connection.target) : "";
            console.log(connected_actions)
            return true
        }
    }

    // if connection source is action then only allow effect connections
    if (connection.source.includes("action")){
        if (connection.target.includes("effect") ){
            return true
        }
    }

    return false
  }

  // we are using a bit of a shortcut here to adjust the edge type
  // this could also be done with a custom edge for example
  const edgesWithUpdatedTypes = edges.map((edge) => {
    if (edge.sourceHandle) {
    //   const edgeType = nodes.find((node) => node.type === 'custom').data.selects[edge.sourceHandle];
    //   edge.type = edgeType;
    }

    return edge;
  });

  return (
    <div style={{ height: 800 }}>
    <ReactFlow
      nodes={nodes}
      edges={edgesWithUpdatedTypes}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onEdgeUpdateEnd={onEdgeUpdateEnd}
      isValidConnection={isValidConnection}
      onConnect={onConnect}
      onInit={setRfInstance}
      fitView
      attributionPosition="bottom-left"
      nodeTypes={nodeTypes}
    >
      <MiniMap style={minimapStyle} zoomable pannable />
      <Controls />
      <Background color="#aaa" gap={16} />
      <Panel position="top-right">
        <button onClick={onSave}>save</button>
        <button onClick={onExit}>exit</button>
      </Panel>
    </ReactFlow>
    </div>
  );
};

  export default () => (
    <ReactFlowProvider>
      <Authflow />
    </ReactFlowProvider>
  );