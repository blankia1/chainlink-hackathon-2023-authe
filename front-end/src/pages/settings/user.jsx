import { useEffect, useState } from 'react';

import { useNavigate } from 'react-router-dom';

import axios from 'axios';
import { useNetwork } from 'wagmi'

import { useAccount, useConnect, useDisconnect } from 'wagmi'
import {CreateTransaction} from './create-transaction'
import {MintNFT} from './create-transaction2'

export default function User() {
  const navigate = useNavigate();

  const [session, setSession] = useState({});
  const { chain, chains } = useNetwork()

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

  async function signOut() {
    await axios(`${process.env.REACT_APP_SERVER_URL}/logout`, {
      withCredentials: true,
    });
    setSession()
    navigate('/signin');
  }

  const { isConnected } = useAccount()
  const { connect, connectors, error, isLoading, pendingConnector } =
    useConnect()
  const { disconnect } = useDisconnect()

  return (
    <div>
      <h3>User session:</h3>
      <pre>{JSON.stringify(session, null, 2)}</pre>
      <button type="button" onClick={signOut}>
        Sign out
      </button>

      <>
      {chain && <div>Connected to {chain.name}</div>}
      {chains && (
        <div>Available chains: {chains.map((chain) => chain.name)}</div>
      )}
    </>
    <br></br>
    <br></br>
    <br></br>
    <div>
        {/* Account content goes here */}
        {/* <SignMessage /> */}
        {/* {<CreateTransaction />} */}
        {/* {<MintNFT />} */}
      </div>
    </div>
    
  );
}