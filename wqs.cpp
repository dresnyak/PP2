#include <bits/stdc++.h>
using namespace std;
const int N = 1e2;

int o[N], n = 0;

int find_min(int a[]){
    int ans = N;
    for(int i = 1; i <= n; i++){
        ans = min(ans, a[i]);
    }
    return ans;
}

int prob1(){
    cin>>n;
    for(int i = 1; i <= n; i++){
        cin>>o[i];
    }
    return find_min(o);

}//O(N)

double find_avg(int a[]){
    double ans = 0;
    for(int i = 1; i <= n; i++){
        ans += o[i];
    }
    return ans / n;
}

double prob2(){
    cin>>n;
    for(int i = 1; i <= n; i++){
        cin>>o[i];
    }
    return find_avg(o);
}//O(N)

string erat(int n){
    o[0] = o[1] = 1;
    for(int i = 2; i * i <= n; i++){
        if(!o[i]){
            if(i * i <= n){
                for(int j = i * i; j <= n; j += i){
                    o[j] = 1;
                }
            }
        }
    }
    if(o[n]){
            return "Composite";
    }
    else{
        return "Prime";
    }
}

string prob3(){
    cin>>n;
    return erat(n);    
}//O(n loglog n)

int fac(int i){
    if(i == 1){
        return 1;
    }
    else{
        return i * fac(i - 1);
    }
}

int prob4(){
    int n;
    cin>>n;
    return fac(n);
}//O(N)

int fib(int i){
    if(i == 1){
        return 1;
    }
    else if(i == 0){
        return 0;
    }
    return fib(i - 2) + fib(i - 1);
}

int prob5(){
    int n;
    cin>>n;
    return fib(n);
}//O(2^n)

int power(int q, int w){
    int ans = 1;
    for(int i = 1; i <= w; i++){
        ans *= q;
    }
    return ans;
}

int prob6(){
    int a;
    cin>>a>>n;
    return power(a, n);
}//O(N)

string pr(char a[]){
    string b = "";
    for(int i = 0; i < n; i++){
        b += a[i];
    }
    return b;
}

void prob7(){
    cin>>n;
    char a[N];
    for(int i = 0; i < n; i++){
        cin>>a[i];
    }
    cout << pr(a) << endl;
    for(int i = 0; i < n; i++){
        for(int j = i + 1; j < n; j++){
            swap(a[i], a[j]);
            cout << pr(a) << endl;
        }
    }
}//O(N^2)

void prob8(){
    string s;
    cin>>s;
    for(int i = 0; i < s.size(); i++){
        if(s[i] >= '0' && s[i] <= '9'){
            continue;
        }
        else {
            cout << "No";
            return;
        }
    }
    cout << "Yes";
}//O(S)

int bin_cof(int a, int b){
    if(a == b || b == 0){
        return 1;
    }
    return bin_cof(a - 1, b - 1) + bin_cof(a - 1, b);
}

void prob9(){
    int a, b;
    cin>>a>>b;
    cout << bin_cof(a, b);
}//O(2^n)

int gcd(int a, int b){
    if(b == 0){
        return a;
    }
    else{
        return gcd(b, a % b);
    }
}

void prob10(){
    int a, b;
    cin>>a>>b;
    cout << gcd(a, b);
}//O(log min(a, b))

int main(){
    prob10();      
}