#ifndef MY_RAYLIB_OVERLAY_H
#define MY_RAYLIB_OVERLAY_H

#if defined(__GNUC__) || defined(__clang__)
#  include_next <raylib.h>
#else
#  error "This overlay requires GCC or Clang. Use -include or copy the real raylib.h instead."
#endif

#ifdef __cplusplus
extern "C" {
#endif

static inline bool MyCheckCollisionRecLine(Rectangle rec, Vector2 p1, Vector2 p2, Vector2& point)
{
    if (CheckCollisionPointRec(p1, rec) ||
        CheckCollisionPointRec(p2, rec)) return true;

    Vector2 a = { rec.x, rec.y };
    Vector2 b = { rec.x + rec.width, rec.y };
    Vector2 c = { rec.x + rec.width, rec.y + rec.height };
    Vector2 d = { rec.x, rec.y + rec.height };


    return CheckCollisionLines(p1, p2, a, b, &point)
        || CheckCollisionLines(p1, p2, b, c, &point)
        || CheckCollisionLines(p1, p2, c, d, &point)
        || CheckCollisionLines(p1, p2, d, a, &point);
}

#ifdef __cplusplus
}
#endif

#endif
