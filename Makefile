CXX ?= g++
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra
# Force-include the local raylib.h overlay. It uses #include_next to load the
# system header, so it must not also be found through -I.
ifneq ($(wildcard raylib.h),)
CPPFLAGS += -include $(CURDIR)/raylib.h
endif
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
