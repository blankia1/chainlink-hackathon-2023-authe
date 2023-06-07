import { memo } from 'react';
import { Handle, useReactFlow, useStoreApi, Position } from 'reactflow';

const options = [
  // {
  //   value: 'ethereum',
  //   label: 'Ethereum Mainnet',
  // },
  {
    value: 'sepolia',
    label: 'Sepolia',
  },
  // {
  //   value: 'goerli',
  //   label: 'Goerli',
  // },
];

function Select({ value, handleId, nodeId }) {
  const { setNodes } = useReactFlow();
  const store = useStoreApi();

  const onChange = (evt) => {
    const { nodeInternals } = store.getState();
    setNodes(
      Array.from(nodeInternals.values()).map((node) => {
        if (node.id === nodeId) {
          node.data = {
            ...node.data,
            selects: {
              ...node.data.selects,
              [handleId]: evt.target.value,
            },
          };
        }

        return node;
      })
    );
  };

  return (
    <div className="proxy-node__select">
      <div>Chain</div>
      <select className="nodrag" onChange={onChange} value={value}>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      <Handle type="source" position={Position.Top} id={handleId} />
      <Handle type="target" position={Position.Top} id={handleId} />
    </div>
  );
}

function ProxyNode({ id, data }) {
  return (
    <>
      <div className="proxy-node__header">
        This is the <strong>AuthE proxy contract</strong>
      </div>
      <div className="proxy-node__body">
        {Object.keys(data.selects).map((handleId) => (
          <Select key={handleId} nodeId={id} value={data.selects[handleId]} handleId={handleId} />
        ))}
      </div>
    </>
  );
}

export default memo(ProxyNode);