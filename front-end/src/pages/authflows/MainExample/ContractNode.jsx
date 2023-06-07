import { memo } from 'react';
import { Handle, useReactFlow, useStoreApi, Position } from 'reactflow';

const token_options = [
  {
    value: 'weth',
    label: 'WETH',
  },
  {
    value: 'authe',
    label: 'AUTHE',
  },
  {
    value: 'custom_erc20',
    label: 'CUSTOM_ERC20',
  },
  {
    value: 'link',
    label: 'LINK',
  },
  {
    value: 'uni',
    label: 'UNI',
  },
  {
    value: '*',
    label: 'ALL',
  },
];

const contract_options = [
  {
    value: 'erc20',
    label: 'ERC20',
  },
  {
    value: 'erc721',
    label: 'NFT (ERC721)',
  },
  {
    value: 'erc1155',
    label: 'ERC-1155',
  }, 
  {
    value: '*',
    label: 'ALL',
  }, 
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
    <div className="contract-node__select">
      <div>Token</div>
      <select className="nodrag" onChange={onChange} value={value}>
        {token_options.map((option) => (
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

function ContractNode({ id, data }) {
  return (
    <>
      <div className="contract-node__header">
        This is a <strong>contract</strong> you are interacting with
      </div>
      <div className="contract-node__body">
        {Object.keys(data.selects).map((handleId) => (
          <Select key={handleId} nodeId={id} value={data.selects[handleId]} handleId={handleId} />
        ))}
      </div>
    </>
  );
}

export default memo(ContractNode);