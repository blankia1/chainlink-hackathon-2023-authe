import { useEffect, useState } from 'react';
import { Show } from "@refinedev/antd";
const { Title, Text } = Typography;
import { Typography } from "antd";
import { useNavigate } from 'react-router-dom';

import axios from 'axios';
import { useNetwork } from 'wagmi'
import { useAccount, useConnect, useDisconnect } from 'wagmi'

export default function Examples() {
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
        navigate('/signin');
      });
  }, []);

  const { isConnected } = useAccount()
  const { connect, connectors, error, isLoading, pendingConnector } =
    useConnect()
  const { disconnect } = useDisconnect()

 return (
        <Show isLoading={isLoading}>
            <Title level={5}>Example 1</Title>
            <Text><a href="/examples/show/example1"> ERC20 token transfer via the AuthE Proxy </a></Text>

            <Title level={5}>Example 2</Title>
            <Text><a href="/examples/show/example2"> Dispute an incorrect approval response </a></Text>

            <Title level={5}>Example 3</Title>
            <Text><a href="/examples/show/example3"> What to do when the AuthE proxy censors you or is unresponsive </a></Text>

            <Title level={5}>Example 4</Title>
            <Text><a href="/examples/show/example4"> What to do when you sign multiple permission documents and not upload them to AuthE </a></Text>

            {/* <Title level={5}>Example 2</Title>
            <Text><a href="/examples/show/example2"> Create a complex transaction with the AuthE Proxy </a></Text> */}

            {/* <Title level={5}>Example 3</Title>
            <Text><a href="/examples/show/example3"> The AuthE proxy is unresponsive </a></Text>

            <Title level={5}>Example 4</Title>
            <Text><a href="/examples/show/example4"> The AuthE proxy censors transactions </a></Text>

            <Title level={5}>Example 5</Title>
            <Text><a href="/examples/show/example5"> The Breakglass account </a></Text>

            <Title level={5}>Example 6</Title>
            <Text><a href="/examples/show/example6"> The 2nd Approver account </a></Text>

            <Title level={5}>Example 7</Title>
            <Text><a href="/examples/show/example7"> The 2nd Signer account </a></Text>

            <Title level={5}>Example 8</Title>
            <Text><a href="/examples/show/example8"> Metamask turn on/off AuthE proxy use </a></Text>

            <Title level={5}>Example 9</Title>
            <Text><a href="/examples/show/example9"> ERC20 token contract with an opt-in / opt-out policy for AuthE Proxy </a></Text>

            <Title level={5}>Example 10</Title>
            <Text><a href="/examples/show/example10"> Put assets on another contract that forces the use of AuthE proxy </a></Text>

            <Title level={5}>Example 11</Title>
            <Text><a href="/examples/show/example11"> Dispute an incorrect transaction </a></Text> */}
        </Show>
    );
};
