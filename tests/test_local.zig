usingnamespace @import("../zinc/zincstd.zig");
fn test_local()  !void{
    var __local_allocator_1 = std.heap.ArenaAllocator.init(zinc_allocator);
    defer __local_allocator_1.deinit();

    const a = try __local_allocator_1.allocator().create(i32); a.* = 5;
    const b = try __local_allocator_1.allocator().create(i32); b.* = 10;
}
