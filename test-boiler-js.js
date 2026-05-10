
function sum(a, b){
    return a+b
}

const fs = require('fs');

const data = fs.readFileSync("/dev/stdin", 'utf8');


const inputBatches = data.split("\r\n")

const inputLength = inputBatches[0]
const inputValues = inputBatches.slice(1)


for(let i = 0; i< inputLength ; i++){
    const inputs = inputValues[i].split(" ")
   const result = sum(Number(inputs[0]), Number(inputs[1]))
   console.log(result) 
}