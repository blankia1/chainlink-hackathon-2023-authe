// Test validate permissions with api call
// Retrieves a signed permission document from the API
// Recalculates the approved action and returns the result
// TODO Needs to check signatures 
console.log("Test validate permissions with api")
const dispute_id = args[2]; // [0] resource address [1] call data [2] dispute_id
const api_url = "https://api.authe.io/public/GET/v0/disputes" 

const authEDisputeRequest = Functions.makeHttpRequest({
    url: `${api_url}/${dispute_id}`,
  })

// First, execute all the API requests are executed concurrently, then wait for the responses
const [authEDisputeResponse] = await Promise.all([
    authEDisputeRequest,
  ])

if (!authEDisputeResponse.error) {
    console.log("Successfully retrieved the dispute from the API")
    // console.log(authEDisputeResponse)
} else {
    console.log("autheDisputeRequest Error")
}

const action = authEDisputeResponse.data.action // args[i] // The action that was done by the user // Needs to be retrieved from the Blockchain so that it has not been tempered with
const permission_document = JSON.parse(authEDisputeResponse.data.permission_document) // Needs to be compared with the result_proof_hash to check if it has not been tempered with

result = 0 // 0 = Deny / 1 = Allow
let i = 0

// For the hackathon only check 'action' permissions to keep it simple
while (i < permission_document.Statement.length) {
    // console.log(permission_document.Statement[i]);
    effect = permission_document.Statement[i].Effect
    if(effect == "Allow"){
        if(permission_document.Statement[i].Action.includes(action) || permission_document.Statement[i].Action.includes("*")){
            result = 1 // Allow
            console.log(action + " is allowed in this statement")
        }
    }
    else if (effect == "Deny"){
        if(permission_document.Statement[i].Action.includes(action) || permission_document.Statement[i].Action.includes("*")){
            console.log(action + " is denied in this statement")
            result = 0; // Deny
            break;   
        }
    }
    else{
        console.log("Effect is unknown")
    }

    i++;
}

if(result == 1){
    console.log("Validation result is: Allowed")
}
else{
    console.log("Validation result is: Denied")
}
return Functions.encodeUint256(result) // 0 = Deny / 1 = Allow
