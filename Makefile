CXX ?= g++
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra
CPPFLAGS += $(shell pkg-config --cflags raylib 2>/dev/null)
LDLIBS += $(shell pkg-config --libs raylib 2>/dev/null || echo -lraylib)

TARGET := pingpong
SRC := $(wildcard *.cpp) $(wildcard components/*.cpp)
HDR := $(wildcard *.h) $(wildcard components/*.h)

.PHONY: all run clean

all: $(TARGET)

$(TARGET): $(SRC) $(HDR)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $(SRC) -o $@ $(LDLIBS)

run: $(TARGET)
	./$(TARGET)

clean:
	rm -f $(TARGET)
