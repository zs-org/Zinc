usingnamespace @import("../zinc/zincstd.zig");
fn first()  !void{
    var __local_allocator_1 = std.heap.ArenaAllocator.init(zinc_allocator);
    defer __local_allocator_1.deinit();

    const a = try __local_allocator_1.allocator().create(i32); a.* = 10;
}

fn second()  !void{
    var __local_allocator_2 = std.heap.ArenaAllocator.init(zinc_allocator);
    defer __local_allocator_2.deinit();

    const b = try __local_allocator_2.allocator().create(f32); b.* = 20.0;
    const c = try __local_allocator_2.allocator().create(i32); c.* = 30;
}
