#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#include <iostream>
#include "trace.h"
#include "predictor.h"

using namespace std;

int main(int argc, char ** argv){
    int opt;
    unsigned int m = 6; //Global branch history (up to 12)
    unsigned int n = 1; //n-bit predictor ( 1 or 2)
    unsigned int addressBits = 8; //how many bits of address is used (up to 12)
    bool debug = false;
    string fileName = "";
    while ((opt = getopt(argc,argv,"i:m:n:a:d")) != EOF){
        switch(opt){
            case 'i': fileName.assign(optarg); break;
            case 'm': m = atoi(optarg); break;  // Global history size
            case 'n': n = atoi(optarg); break; // n-bit predictor
            case 'a': addressBits = atoi(optarg); break; // how many LSB of address is used for indexing
            case 'd': debug = true; break;
	    case '?': printf("usage is \n -i : fileName \n -m : history length\n -n : n-bit\n -a : address length\n -d : debug\n");
            default: exit(1);
        }
    }
    if(fileName.empty()){
            printf("usage is \n -i : fileName \n -m : history length\n -n : n-bit\n -a : address length\n -d: debug\n");
	    exit(1);
    }

    // Initialize Trace File
    TraceFile trace(fileName);

    // Initialize Predictor
    Predictor pred(m,n, addressBits, debug);
    string address = "";
    bool expected, predicted;

    // Execute trace through Predictor
    while(trace.getNextBranch(address,expected)){
        predicted = pred.makePrediction(address,expected);
    	if(debug){
		printf("Branch address: 0x%s, predicted: %d, expected: %d\n", address.c_str(), predicted, expected);
    	}
    }

    // Print results
    pred.printStats();
    return 0;
}
