function parseBool(value) {
    const normalized = String(value).trim().toLowerCase();
    return normalized === 'true' || normalized === '1';
}

<USER_CODE>

const fs = require('fs');

const rawInput = fs.readFileSync(0, 'utf8').replace(/\r\n/g, '\n').trim();
const lines = rawInput.length === 0 ? [] : rawInput.split('\n');
let index = 0;

    const a = Number(lines[index++]);
    const b = Number(lines[index++]);

const result = summation(a, b);
console.log(String(result));
