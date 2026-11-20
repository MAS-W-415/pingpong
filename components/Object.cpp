#include "Object.h"
#include <cstdio>

template <typename T>
void Object<T>::Move()
{
    //  check remove 
    if(isNeedRemove)
    {
        pre_state = isNeedRemove;
        isNeedRemove = false;
        reMove();
        return;
    }
    //  save old form 
    old_form = form;
    //  do the move 
    move_p();
    pre_state = isNeedRemove;
}

template <typename T>
void Object<T>::reMove()
{
    form = old_form;
}


template <typename T>
void Object<T>::drawAsset(Texture& tex)
{
    if(asset_name != asset.first)
    {
        index = 0;
        len_pos  = asset.second.frame.size();
        timer = 0.0f;
        asset_name = asset.first;
    }
    Rectangle pos = asset.second.frame[index];
    Rectangle dst = getRec();
    DrawTexturePro(
            tex,
            pos,
            dst,
            {0.0f, 0.0f},
            0.0f,
            WHITE 
            );
    timer += GetFrameTime();
    if(timer >= 1.0f / (float)asset.second.time)
    {
        timer -= 1.0f / (float)asset.second.time;
        index = (index + 1) % len_pos;
        if(asset.second.type == ONCE && index == 0)
        {
            asset = old_asset;
        }
        else if(asset.second.type == LOOP && index == 0 && asset.first != old_asset.first)
        {
            old_asset = asset;
        }
        else{;}
    }
}


template class Object<CIRCLE>;
template class Object<REC>;
