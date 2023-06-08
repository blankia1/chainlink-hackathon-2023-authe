// Test validate permissions locally without api call
console.log("Test validate permissions without api")
const action = "transfer" // args[i] // The action that was done by the user

const permission_document = {
    "Version": "2023-05-11",
    "Statement": [
        {
            "Resource": [
                "*"
            ],
            "Effect": "Allow",
            "Action": [
                "*"
            ],
            "Principal": [
                "*"
            ],
            "Sid": "AllowAllPermissions"
        },
        {
            "Resource": [
                "*"
            ],
            "Effect": "Deny",
            "Action": [
                "transfer", "mint", "transferFrom"
            ],
            "Principal": [
                "*"
            ],
            "Sid": "AllowAllPermissions"
        }
    ],
    "Signature": "9434903948034389439843834900920-320-3-2024904209429049033490430--340"
};

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
