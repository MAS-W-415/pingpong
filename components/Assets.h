#ifndef ASSET_H
#define ASSET_H

#include <fstream>
#include <future>
#include <map>
#include <raylib.h>
#include <sstream>
#include <string>
#include <vector>

enum AssetType
{
    LOOP,
    ONCE
};

typedef struct  
{
    std::vector<Rectangle> frame;
    int time;
    AssetType type;
}_Asset;

inline static Rectangle fetchFrame(const std::string& frame_name)
{
    std::ifstream file("assets/pingpong-art/pingpong-art.spritepos", std::ifstream::in);
    
    std::string line;
    Rectangle ans;
    std::string tmp;
    while(std::getline(file, line))
    {
        if(line.find(frame_name) != std::string::npos)
        {
            std::istringstream iss(line);
            iss >> tmp;
            iss >> ans.x;
            iss >> ans.y;
            iss >> ans.width;
            iss >> ans.height;
            return ans;
        }
    }
}

inline static const std::map<std::string, _Asset> assetMap = []
{
    std::map<std::string, _Asset> map;
    std::ifstream file("assets/pingpong-art/pingpong-art.spritepos", std::ifstream::in);
    
    std::string line;
    bool isInAnimation = false;
    std::string name;
    std::string type_name;
    while(std::getline(file, line))
    {
        if(line.find("[animations]") != std::string::npos)
        {
            isInAnimation = true;
            continue;
        }
        if(isInAnimation)
        {
            _Asset tmp;
            std::istringstream iss(line);
            iss >> name;
            iss >> tmp.time;
            iss >> type_name;
            tmp.type = (type_name == "loop") ? LOOP : ONCE;
            std::string frame_name;
            while(iss >> frame_name)
            {
                std::future<Rectangle> result = std::async(std::launch::async, fetchFrame, frame_name);
                tmp.frame.push_back(result.get());
            }
            map[name] = tmp;      
        }
    }
    return map;
}();


#endif 
