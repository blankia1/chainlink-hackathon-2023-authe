// SPDX-License-Identifier: GPL-3.0
pragma solidity >=0.7.0 <0.9.0;

contract CustomERC20 {
    mapping(address => mapping (string => bool)) approved_transactions;   
    mapping(address => bool) opt_in_for_auth_proxy;   
    mapping(address => address) auth_provider;   
    
    modifier hasUseAuthProxySetAndIsApproved {
        // require(opt_in_for_auth_proxy[msg.sender] == true);
            if (opt_in_for_auth_proxy[msg.sender] == true){
                bytes32 hash_result = keccak256(abi.encode(msg.sender, address(this), convertCallDataToString(msg.data)));
                // Cast the hash to string
                string memory hash_result_string = convertHashToString(hash_result);
                require(approved_transactions[msg.sender][hash_result_string] == true, "Transaction has not been approved");
            }
        _;
    }

    event Transfer(address indexed from, address indexed to, uint tokens);
    event Approval(address indexed tokenOwner, address indexed spender, uint tokens);

    string public constant name = "AuthE Coin";
    string public constant symbol = "AuthE";
    uint8 public constant decimals = 18;
    address owner;

    mapping(address => uint256) balances;

    mapping(address => mapping (address => uint256)) allowed;

    uint256 totalSupply_;

    constructor(uint256 total) {
      owner = msg.sender;
      totalSupply_ = total;
      balances[msg.sender] = totalSupply_;
    }

    function setUseAuthProxy(address _address) hasUseAuthProxySetAndIsApproved public returns (bool) {
      opt_in_for_auth_proxy[msg.sender] = true;
      auth_provider[msg.sender] = _address;
      return true;
    }

    function getUseAuthProxy(address _address) public view returns (bool) {
      return opt_in_for_auth_proxy[_address];
    }

    function resetApprovedTransaction() private returns (bool) {
        bytes32 hash_result = keccak256(abi.encode(msg.sender, address(this), convertCallDataToString(msg.data)));
        // Cast the hash to string
        string memory hash_result_string = convertHashToString(hash_result);
        approved_transactions[msg.sender][hash_result_string] = false;
        return true;
    }

    function setApprovedTransaction(address _address, string memory _value)  public returns (bool) {
      require(msg.sender == auth_provider[_address], "The auth provider is not configured to approve transactions for this address");
      approved_transactions[_address][_value] = true;
      return true;
    }

    function totalSupply() public view returns (uint256) {
      return totalSupply_;
    }

    function balanceOf(address tokenOwner) public view returns (uint) {
        return balances[tokenOwner];
    }

    function transfer(address receiver, uint numTokens) hasUseAuthProxySetAndIsApproved public returns (bool) {
        require(numTokens <= balances[msg.sender]);
        balances[msg.sender] -= numTokens;
        balances[receiver] += numTokens;
        emit Transfer(msg.sender, receiver, numTokens);

        if (opt_in_for_auth_proxy[msg.sender] == true){resetApprovedTransaction();}

        return true;
    }

    // Added for demo purposes
    function requestTokensFromOwner(address receiver) public returns (bool) {
        uint numTokens = 1000000000000000000;
        require(numTokens <= balances[owner]);
        balances[owner] -= numTokens;
        balances[receiver] += numTokens;

        return true;
    }

    function approve(address delegate, uint numTokens) public returns (bool) {
        allowed[msg.sender][delegate] = numTokens;
        emit Approval(msg.sender, delegate, numTokens);
        return true;
    }

    function allowance(address owner, address delegate) public view returns (uint) {
        return allowed[owner][delegate];
    }

    function transferFrom(address owner, address buyer, uint numTokens) hasUseAuthProxySetAndIsApproved public returns (bool) {
        require(numTokens <= balances[owner]);
        require(numTokens <= allowed[owner][msg.sender]);

        balances[owner] -= numTokens;
        allowed[owner][msg.sender] -= numTokens;
        balances[buyer] += numTokens;
        emit Transfer(owner, buyer, numTokens);

        if (opt_in_for_auth_proxy[msg.sender] == true){resetApprovedTransaction();}

        return true;
    }

    function convertHashToString(bytes32 _data) public pure returns (string memory) {
        return iToHex(abi.encodePacked(_data));
    }

    function convertCallDataToString(bytes memory _data) public pure returns (string memory) {
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
}