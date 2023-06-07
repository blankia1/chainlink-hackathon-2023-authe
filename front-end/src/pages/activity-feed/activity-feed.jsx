import { useEffect, useState } from 'react';
import { Row, Col, Card, Typography } from "antd";
const { Title, Text } = Typography;

import { useNavigate } from 'react-router-dom';

import axios from 'axios';
import { useNetwork } from 'wagmi'
import { useAccount, useConnect, useDisconnect } from 'wagmi'

import {OrderTimeline} from "./orderTimeline"

export default function ActivityFeed() {
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
    <Row gutter={[16, 16]}>
        <Title level={5}>TimeLine</Title>
        <Col md={24}>
        {/* <div text-align='right'>
                <Space wrap >
                  <Button
                      shape="round"
                      type="primary"
                      text="Refresh"
                      align="rceight"
                      // onClick={() => {
                      //     setFilterCategories([]);
                      //     onChange?.([]);
                      // }}
                  >
                    Refresh
                  </Button>
              </Space>
              </div> */}
          <Row gutter={[16, 16]}>
              <Col xl={10} lg={24} md={24} sm={24} xs={24}>
                  <Card
                      bodyStyle={{
                          padding: 10,
                          paddingBottom: 0,
                      }}
                      style={{
                          background: "url(images/daily-revenue.png)",
                          backgroundRepeat: "no-repeat",
                          backgroundPosition: "right",
                          backgroundSize: "cover",
                      }}
                  >
                  <OrderTimeline />    
                  </Card>
              </Col>
          </Row>
      </Col>
    </Row>
    
  );
}