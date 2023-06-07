import { useNavigate } from 'react-router-dom';

import { useAccount, useConnect, useSignMessage, useDisconnect } from 'wagmi';
import { InjectedConnector } from 'wagmi/connectors/injected';

import axios from 'axios';

import { useLogin } from "@refinedev/core";
import Icon from "@ant-design/icons";
import { Layout as AntdLayout, Button, Row, Col } from "antd";


export default function SignIn() {
    const { mutate: login, isLoading } = useLogin();
    
    const navigate = useNavigate();

    const { connectAsync } = useConnect();
    const { disconnectAsync } = useDisconnect();
    const { isConnected } = useAccount();
    const { signMessageAsync } = useSignMessage();

    const handleAuth = async () => {
        //disconnects the web3 provider if it's already active
        if (isConnected) {
          await disconnectAsync();
        }
        // enabling the web3 provider metamask
        const { account, chain } = await connectAsync({
          connector: new InjectedConnector(),
        });

        const userData = { address: account, chain: chain.id, network: 'evm' };
        // making a post request to our 'request-message' endpoint
        const { data } = await axios.post(
          `${process.env.REACT_APP_SERVER_URL}/request-message`,
          userData,
          {
            headers: {
              'content-type': 'application/json',
            },
          }
        );
        const message = data.message;
        // signing the received message via metamask
        const signature = await signMessageAsync({ message });
        const { res } = await axios.post(
          `${process.env.REACT_APP_SERVER_URL}/verify`,
          {
            message,
            signature,
          },
          { withCredentials: true }, // set cookie from Express server
          { credentials: 'include' },
          { sameSite: 'None' }
        );

        // redirect to /user
        navigate('/authflow');
      };

    return (
        <AntdLayout
            style={{
                background: `radial-gradient(50% 50% at 50% 50%, #63386A 0%, #310438 100%)`,
                backgroundSize: "cover",
            }}
        >
            <Row
                justify="center"
                align="middle"
                style={{
                    height: "100vh",
                }}
            >
                <Col xs={22}>
                    <div
                        style={{
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            marginBottom: "28px",
                        }}
                    >
                        {/* <img src="./refine.svg" alt="Refine" /> */}
                    </div>
                    <div style={{ display: "flex", justifyContent: "center" }}>
                        <Button
                            type="primary"
                            size="large"
                            icon={
                                <Icon
                                    component={() => (
                                        <img
                                            alt={"ethereum.png"}
                                            src="./ethereum.png"
                                        />
                                    )}
                                />
                            }
                            loading={isLoading}
                            onClick={() => handleAuth()}
                        >
                            SIGN-IN WITH METAMASK
                        </Button>
                    </div>
                </Col>
            </Row>
        </AntdLayout>
    );
}
