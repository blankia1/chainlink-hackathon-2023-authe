// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@chainlink/contracts/src/v0.8/ChainlinkClient.sol";
import "@chainlink/contracts/src/v0.8/ConfirmedOwner.sol";
import "./strings.sol";

// Needed for Chainlink functions
import {Functions, FunctionsClient} from "./dev/functions/FunctionsClient.sol";

/**
 * @title The AuthEProxy V0.3 contract
 * @notice A Proxy contract that makes requests to AuthE before authorizing the transaction
 * @notice The proxy needs to be unique per user. Otherwise you can set approved transactions for other people. Depending on the setup
 */
contract AuthEProxyV3 is ChainlinkClient, FunctionsClient, ConfirmedOwner {
    using Chainlink for Chainlink.Request;
    using Functions for Functions.Request;
    using strings for *;

    string public api_url;
    bytes32 public hash_result;
    bool public oracle_result;
    string public authe_message_temp;

    mapping(string => string) approved_transactions;    
    mapping(string => address) approved_transactions_msg_sender;   
    mapping(string => address) approved_transactions_resource_address;  
    
    address private immutable oracle;
    bytes32 private immutable jobId;
    uint256 private immutable fee;

    bytes32 public latestRequestId;
    bytes public latestResponse;
    bytes public latestError;

    event OCRResponse(bytes32 indexed requestId, bytes result, bytes err);

    constructor(address _oracle, address _functionsOracleProxy, bytes32 _jobId, uint256 _fee, address _link) FunctionsClient(_functionsOracleProxy) ConfirmedOwner(msg.sender) {
        if (_link == address(0)) {
            setPublicChainlinkToken();
        } else {
            setChainlinkToken(_link);
        }

        oracle = _oracle;
        jobId = _jobId;
        fee = _fee;
    }

    // TODO Function name should be retrieved from the call data
    function requestApproval(address _resource_address, string memory _functionName, bytes memory _data) public {
        // TODO Function name should be retrieved from the call data
        
        // Cast the bytes callData to string for the api request and hashing
        string memory call_data_string = convertCallDataToString(_data);

        // Use the hash as the mapping key
        hash_result = keccak256(abi.encode(msg.sender, _resource_address, call_data_string)); // Need to use callData as string for backend

        // Cast the hash to string / for backend
        string memory hash_result_string = convertHashToString(hash_result);

        // Store the resource address and msg_sender
        approved_transactions_msg_sender[hash_result_string] = msg.sender;
        approved_transactions_resource_address[hash_result_string] = _resource_address;

        // Make oracle request
        string memory query = string.concat("?f=0x", toAsciiString(msg.sender), "&t=0x", toAsciiString(_resource_address), "&n=", _functionName, "&d=", call_data_string, "&r=0x", toAsciiString(_resource_address));
        string memory url = string.concat(api_url, query);

        Chainlink.Request memory req = buildChainlinkRequest(
            jobId,
            address(this),
            this.fulfillBytes.selector
        );
        req.add(
            "get",
            url
        );
        req.add("path", "message");
        
        sendChainlinkRequestTo(oracle, req, fee); 
    }

    /**
     * @notice Fulfillment function for variable bytes
     * @dev This is called by the oracle. recordChainlinkFulfillment must be used.
     */
    function fulfillBytes(
        bytes32 requestId,
        bytes memory bytesData
    ) public recordChainlinkFulfillment(requestId) {
        string memory authe_message = string(bytesData);

        // Split the string in array
        strings.slice memory s = authe_message.toSlice();                
        strings.slice memory delim = "_".toSlice();                            
        string[] memory parts = new string[](s.count(delim));                  
        for (uint i = 0; i < parts.length; i++) {                              
           parts[i] = s.split(delim).toString();  
        }  

        string memory request_hash = parts[0];
        // Mapping string => string
        approved_transactions[request_hash] = authe_message;

        address msg_sender = approved_transactions_msg_sender[request_hash];
        address resource_address = approved_transactions_resource_address[request_hash];

        // Set the approval in the resource_contact so that the user can later execute it
        (bool success, ) = resource_address.call(
            abi.encodeWithSignature("setApprovedTransaction(address,string)", msg_sender, request_hash)
        );

        oracle_result = true;
    }

    /**
     * @notice Chainlink functions
     * @dev Chainlink functions
     */
    function executeRequest(
        string calldata source,
        bytes calldata secrets,
        string[] calldata args,
        uint64 subscriptionId,
        uint32 gasLimit
    ) public onlyOwner returns (bytes32) {
        // Get the proof from the state stored in the contract
        // Use the hash as the mapping key
        hash_result = keccak256(abi.encode(msg.sender, args[0], args[1]));

        // Cast the hash to string / for backend
        string memory hash_result_string = convertHashToString(hash_result);

        // Recover auth message proof. This needs to be send to the ChainLink Function to verify the proof
        string memory authe_message = approved_transactions[hash_result_string];
        authe_message_temp = authe_message;
        
        // Make the request
        Functions.Request memory req;
        req.initializeRequest(Functions.Location.Inline, Functions.CodeLanguage.JavaScript, source);
        if (secrets.length > 0) {
        req.addRemoteSecrets(secrets);
        }
        if (args.length > 0) req.addArgs(args);

        bytes32 assignedReqID = sendRequest(req, subscriptionId, gasLimit);
        latestRequestId = assignedReqID;
        return assignedReqID;
    }

    /**
     * @notice Callback that is invoked once the DON has resolved the request or hit an error
     */
    function fulfillRequest(bytes32 requestId, bytes memory response, bytes memory err) internal override {
        // TODO Based on the result you can decide to slash some deposit or to trigger an insurance mechanism

        latestResponse = response;
        latestError = err;
        emit OCRResponse(requestId, response, err);
    }
  
    /**
     * @notice Helper functions
     * @dev Helper functions
     */
    function convertCallDataToString(bytes memory _data) public pure returns (string memory) {
        return iToHex(abi.encodePacked(_data));
    }

    function convertHashToString(bytes32 _data) public pure returns (string memory) {
        return iToHex(abi.encodePacked(_data));
    }

    function iToHex(bytes memory buffer) public pure returns (string memory) {
        // Fixed buffer size for hexadecimal convertion
        bytes memory converted = new bytes(buffer.length * 2);

        bytes memory _base = "0123456789abcdef";

        for (uint256 i = 0; i < buffer.length; i++) {
            converted[i * 2] = _base[uint8(buffer[i]) / _base.length];
            converted[i * 2 + 1] = _base[uint8(buffer[i]) % _base.length];
        }

        return string(abi.encodePacked("0x", converted));
    }

    function setApiUrl(string memory _value) onlyOwner public {
        api_url = _value;
    }

    function getApprovedTransaction(string memory key) public view returns(string memory) {
        return approved_transactions[key];
    }

    function toAsciiString(address x) internal pure returns (string memory) {
        bytes memory s = new bytes(40);
        for (uint i = 0; i < 20; i++) {
            bytes1 b = bytes1(uint8(uint(uint160(x)) / (2**(8*(19 - i)))));
            bytes1 hi = bytes1(uint8(b) / 16);
            bytes1 lo = bytes1(uint8(b) - 16 * uint8(hi));
            s[2*i] = char(hi);
            s[2*i+1] = char(lo);            
        }
        return string(s);
    }

    function char(bytes1 b) internal pure returns (bytes1 c) {
        if (uint8(b) < 10) return bytes1(uint8(b) + 0x30);
        else return bytes1(uint8(b) + 0x57);
    }

    /**
     * @notice Withdraws LINK from the contract
     * @dev Implement a withdraw function to avoid locking your LINK in the contract
     */
    function withdrawLink() public onlyOwner {
        LinkTokenInterface link = LinkTokenInterface(chainlinkTokenAddress());
        require(
            link.transfer(msg.sender, link.balanceOf(address(this))),
            "Unable to transfer"
        );
    }
}