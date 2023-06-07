import { Position } from 'reactflow';

export const nodes = [
  {
    id: 'user',
    type: 'input',
    data: {
      label: 'User',
    },
    position: { x: 500, y: 0 },
    style: {
      background: '#ccd9f6',
    },
  },
  {
    id: 'transfer_action',
    data: {
      label: 'Transfer',
    },
    position: { x: 0, y: 100 },
  },
  {
    id: 'transferFrom_action',
    data: {
      label: 'TransferFrom',
    },
    position: { x: 250, y: 100 },
  },
  {
    id: 'approve_action',
    data: {
      label: 'Approve',
    },
    position: { x: 500, y: 100 },
  },
  {
    id: 'allowance_action',
    data: {
      label: 'Allowance',
    },
    position: { x: 750, y: 100 },
  },
  {
    id: 'mint_action',
    data: {
      label: 'Mint',
    },
    position: { x: 1000, y: 100 },
  },
  {
    id: 'allow_effect',
    type: 'effect',
    data: {
      label: 'Allow',
    },
    position: { x: 250, y: 200 },
    style: {
      background: '#2B6CB0',
      color: 'white',
    },
  },
  {
    id: 'deny_effect',
    type: 'effect',
    data: {
      label: 'Deny',
    },
    position: { x: 750, y: 200 },
    style: {
      background: '#2B6CB0',
      color: 'white',
    },
  },
  {
    id: 'proxy',
    type: 'proxy',
    position: { x: 490, y: 300 },
    data: {
      selects: {
        'handle-0': 'ethereum'
      },
    },
  },
  {
    id: 'contract',
    type: 'custom',
    position: { x: 490, y: 450 },
    data: {
      selects: {
        'handle-0': 'custom_erc20',
      },
    },
  },
  {
    id: 'target',
    type: 'output',
    data: {
      label: 'Target',
    },
    position: { x: 500, y: 650 },
    style: {
      background: '#D6D5E6',
    },
    targetPosition: Position.Top,
  },
  // {
  //   id: 'contract',
  //   type: 'contract',
  //   position: { x: 90, y: 450 },
  //   data: {
  //     selects: {
  //       'handle-0': 'smoothstep',
  //       'handle-1': 'smoothstep',
  //     },
  //   },
  // },
//   {
//     id: '5',
//     type: 'output',
//     data: {
//       label: 'custom style',
//     },
//     className: 'circle',
//     style: {
//       background: '#2B6CB0',
//       color: 'white',
//     },
//     position: { x: 400, y: 200 },
//     sourcePosition: Position.Right,
//     targetPosition: Position.Left,
//   },
//   {
//     id: '6',
//     type: 'output',
//     style: {
//       background: '#63B3ED',
//       color: 'white',
//       width: 100,
//     },
//     data: {
//       label: 'Node',
//     },
//     position: { x: 400, y: 325 },
//     sourcePosition: Position.Right,
//     targetPosition: Position.Left,
//   },
  {
    id: '7',
    type: 'default',
    className: 'annotation',
    data: {
      label: (
        <>
          Drag and drop the arrows to combine certain actions. After this click on <strong>Save</strong> in the top right corner and
          in the next screen you can <strong>Create</strong> the permission document 🥳
        </>
      ),
    },
    draggable: false,
    selectable: false,
    position: { x: 0, y: 600 },
  },
];

export const edges = [
  { id: 'user_to_transfer_action', source: 'user', target: 'transfer_action', label: 'The user performs the following action', animated: true },
  { id: 'action_to_effect', source: 'transfer_action', target: 'allow_effect', label: 'This action should be allowed. Or if denied then delete this arrow and drag another one to the deny button', animated: true },
  { id: 'allow_effect_to_proxy', source: 'allow_effect', target: 'proxy', animated: true, type: 'smoothstep' },
  { id: 'deny_effect_to_proxy', source: 'deny_effect', target: 'proxy', animated: true, type: 'smoothstep' },
  { id: 'proxy_to_contract', source: 'proxy', target: 'contract', animated: true, type: 'smoothstep' },
  { id: 'contract_to_target', source: 'contract', target: 'target', animated: true, type: 'smoothstep' },
];