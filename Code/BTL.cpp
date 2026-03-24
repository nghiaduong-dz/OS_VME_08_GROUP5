#include<iostream>
#include<vector>
#include<algorithm>
#include<queue>
using namespace std;

int fifo (vector<int> pages, int capacity){
    vector<int> frame;
    queue<int> q;
    int page_faults = 0;
    for(int page : pages){
        if(find(frame.begin(), frame.end(), page) == frame.end()){
            page_faults++;
            if(frame.size() < capacity){
                frame.push_back(page);
                q.push(page);
            } else {
                int old_page = q.front();
                q.pop();
                frame.erase(remove(frame.begin(), frame.end(), old_page), frame.end());
                frame.push_back(page);
                q.push(page);
            }
        }
    }
    return page_faults;
}

int lru (vector<int> pages, int capacity){
    vector<int> frame;
    int page_faults = 0;
    for(int page : pages){
        auto it = find(frame.begin(), frame.end(), page);
        if(it == frame.end()){  
            page_faults++;
            if(frame.size() < capacity){
                frame.push_back(page);
            } else {
                frame.erase(frame.begin());
                frame.push_back(page);
            }
        } else {
            frame.erase(it);
            frame.push_back(page);
        }
    }
    return page_faults;
}

int opt (vector<int> pages, int capacity){
    vector<int> frame;
    int page_faults = 0;
    for(int i = 0; i < pages.size(); i++){
        int page = pages[i];
        if(find(frame.begin(), frame.end(), page) == frame.end()){
            page_faults++;
            if(frame.size() < capacity){
                frame.push_back(page);
            } else {
                int farthest = -1, index = -1;
                for(int j = 0; j < frame.size(); j++){
                    int k;
                    for(k = i + 1; k < pages.size(); k++){
                        if(frame[j] == pages[k]){
                            break;
                        }
                    }
                     if(k == pages.size()){
                        index = j;
                        break;
                    }
                    if(k > farthest){
                        farthest = k;
                        index = j;
                    }
                }
                frame.erase(frame.begin() + index);
                frame.push_back(page);
            }
        }
    }

    return page_faults;
}

int main(){
    int n, capacity;
    cout << "Nhap so luong trang: ";
    cin >> n;
    vector<int> pages(n);
    cout << "Nhap cac trang: ";
    for(int i = 0; i < n; i++){
        cin >> pages[i];
    }
    cout << "Nhap suc chua: ";
    cin >> capacity;

    cout << "So page fault FIFO: " << fifo(pages, capacity) << endl;
    cout << "So page fault LRU: " << lru(pages, capacity) << endl;
    cout << "So page fault OPT: " << opt(pages, capacity) << endl;

    return 0;
}
