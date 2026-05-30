#include <bits/stdc++.h>
using namespace std;

bool parseBool(const string& value) {
    string normalized = value;
    for (char& ch : normalized) {
        ch = static_cast<char>(tolower(static_cast<unsigned char>(ch)));
    }
    return normalized == "true" || normalized == "1";
}

string boolToString(bool value) {
    return value ? "true" : "false";
}

<USER_CODE>

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int a;
    cin >> a;
    int b;
    cin >> b;
    int c;
    cin >> c;

    auto result = sum_three(a, b, c);
    cout << result;
    return 0;
}
