usingnamespace @import("../zinc/zincstd.zig");
pub const Vector2 = struct {
    x: f32,
    y: f32,
};

pub const Player = struct {
    pos: Vector2,
    id: i32,
};

fn test_structs()  !void{
    var __local_allocator_1 = std.heap.ArenaAllocator.init(zinc_allocator);
    defer __local_allocator_1.deinit();

    const v1 = Vector2{ .x= 1.0, .y= 2.0 }
    const p1 = Player{
        .pos= Vector2{ .x= 3.0, .y= 4.0 },
        .id= 42,
    }

    const v2 = try __local_allocator_1.allocator().create(Vector2); v2.* = Vector2{ .x= 5.0, .y= 6.0;}
}
