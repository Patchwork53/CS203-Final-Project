COMPILE = g++
CFLAGS = -O3 -Wall 

OBJ_DIR = build

SRC_FILES = $(wildcard *.cpp)
OBJ_FILES = $(patsubst %.cpp,$(OBJ_DIR)/%.o,$(SRC_FILES))

all: $(OBJ_DIR) branchsim

branchsim: $(OBJ_FILES)
	$(COMPILE) $(CFLAGS) -o $@ $^

$(OBJ_DIR)/%.o: %.cpp 
	$(COMPILE) $(CFLAGS) -c -o $@ $<

$(OBJ_DIR):
	mkdir -p $(OBJ_DIR)

clean: 
	-rm $(OBJ_DIR)/* branchsim 

