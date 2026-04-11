#pragma once

#include <iostream>
#include <vector>
#include <string>

using namespace std;

// InputModel: Stores data parsed from the input CSV file
struct InputModel {
    int frameSize;                 // Number of frames available in memory
    vector<int> referenceString;   // The sequence of page requests (reference string)
    
    // Default constructor
    InputModel() : frameSize(0) {}
};

// StepResultModel: Stores the detailed state of memory at each step 
// (Used for drawing the Gantt chart in GUI and exporting detailed CSV)
struct StepResultModel {
    int step;                      // Step number (e.g., 1, 2, 3...)
    int pageRequest;               // The current page being requested
    vector<int> frames;            // State of frames. Use -1 to represent an empty frame '-'
    bool isPageFault;              // True if Page Fault occurs (FAULT), False if Hit (HIT)
    int currentTotalFaults;        // Cumulative number of page faults up to this step
    
    // Constructor for easy initialization
    StepResultModel(int s, int req, vector<int> f, bool fault, int tFaults) {
        step = s;
        pageRequest = req;
        frames = f;
        isPageFault = fault;
        currentTotalFaults = tFaults;
    }
};

// SummaryModel: Stores the overall performance metrics 
// (Crucial for Stress tests where we skip detailed steps)
struct SummaryModel {
    string algorithmName;          // e.g., "FIFO", "LRU", "OPT"
    int totalPageHits;             // Total number of hits
    int totalPageFaults;           // Total number of page faults
    double hitRatio;               // (Hits / Total Requests) * 100
    double faultRatio;             // (Faults / Total Requests) * 100
    double executionTimeMs;        // Execution time in milliseconds for performance tracking
    
    SummaryModel() : totalPageHits(0), totalPageFaults(0), hitRatio(0), faultRatio(0), executionTimeMs(0) {}
};
