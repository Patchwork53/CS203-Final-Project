#include "predictor.h"
#include <sstream>
#include <iomanip>
#include <cassert>

Predictor::Predictor(unsigned int m, unsigned int n, unsigned int addrLength, bool debug){
    assert((m + addrLength) < (8u * sizeof(unsigned int)));
    this->historyBits = m; // Size of global history
    this->counterBits = n; // Size of counter
    this->globalHistory = 0; 
    this->addrBits = addrLength;
    this->debug = debug;
    this->correct = 0;
    this->total = 0;
    size_t phtSize = 1u << (m + this->addrBits);
    unsigned int initCounter = 0;
    this->pht.assign(phtSize, initCounter);
    this->phtUsed.resize(phtSize, 0);
    this->usedEntries = 0;
    printf("BHT: %u-bit\n", n);
    printf("Address length: %u\n", this->addrBits);
    printf("History length: %u\n", this->historyBits);
    printf("Debug mode: %u\n", this->debug);
};


void Predictor::updateGlobalHistory(bool expected){
    globalHistory = globalHistory << 1;
    globalHistory = globalHistory | expected;
    unsigned int mask = (1 << this->historyBits) - 1;
    globalHistory = globalHistory & mask; 
}

void Predictor::updateCounter(unsigned int index, bool expected){
    unsigned int maxValue = (1u << this->counterBits) - 1;
    unsigned int threshold = 1u << (this->counterBits - 1);
    if(expected){
        if(pht[index] == (threshold - 1)){
            pht[index] = maxValue;
        }
        else if(pht[index] < maxValue){
            pht[index]++;
        }
    }
    else{
        if(pht[index] == threshold){
            pht[index] = 0;
        }
        else if(pht[index] > 0){
            pht[index]--;
        }
    }
}

bool Predictor::makePrediction(string input, bool expected){
    // Convert Hex address to integer address
    unsigned int address = truncateAddress(hexToInt(input));

    unsigned int index = (address << this->historyBits) | globalHistory;
    assert(index < this->pht.size());
    if(!phtUsed[index]){
        phtUsed[index] = 1;
        usedEntries++;
    }
    unsigned int threshold = 1u << (this->counterBits - 1);
    bool predicted = pht[index] >= threshold;

    updateCounter(index, expected);

    // Update global history
    updateGlobalHistory(expected);

    // Update statistics
    if(predicted == expected){
        this->correct++;
    }
    this->total++;

    return predicted;
}

/*
 * Print out branch predictor statistics
 */
void Predictor::printStats(){ 
    printf("------------------------------------------\n"); 
    if(total == 0){
        printf("Error, Cannot get rate \n");
    }
    else{
        printf("Misclassification rate: %.2f%%\n", 100.00 * (1 - (double)(this->correct)/this->total));
    } 
    
    printf("correct: %d\n", this->correct);
    printf("total: %d\n",this->total);


    // Update the following line to print out the number of BHT entires used.
    // double usage = 100.00 * (double)(this->usedEntries) / this->pht.size();
    // printf("BHT used %.2f%%\n", usage);
    printf("BHT used %lu entries\n", this->usedEntries);
}

/*
 * DO NOT MODIFY BELOW THIS
 */


/*
 * Convert Hex string from trace file to integer address
 */
unsigned int Predictor::hexToInt(string input){
    istringstream converter(input);
    unsigned int result;
    converter >> std::hex >> result; 
    return result;
}

/*
 * Truncate Address to specified number of address bits
 */
unsigned int Predictor::truncateAddress(unsigned int input){
    unsigned int mask = (1 << this->addrBits) - 1;
    unsigned int result = input & mask;

    return result;
}

