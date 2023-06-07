import { Show } from "@refinedev/antd";
const { Title, Text } = Typography;
import { Typography } from "antd";

 
export default function Example3() {
  
  return (
    <Show>
      <Title level={5}>Example 3 - What to do when the AuthE proxy censors you or is unresponsive</Title>
    <br></br> 
    <br></br>
    <br></br>
    <Title level={5}>TODO - But basically on the smart contract there should be an update enforcement mechanism that forces AuthE to use the new permission document. If this is not done then there should be a slashing enforcement.</Title>
    <Text> 
      Also you can imagine a breakglass account that will make each transaction passthrough no matter what.
    </Text>

  </Show>
    
    
  );
}