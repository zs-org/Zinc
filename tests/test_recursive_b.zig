usingnamespace @import("../zinc/zincstd.zig");
const test_recursive_a = @import("test_recursive_a.zig");fn func_b()  !void{
    var __local_allocator_2 = std.heap.ArenaAllocator.init(zinc_allocator);
    defer __local_allocator_2.deinit();

    const y = try __local_allocator_2.allocator().create(i32); y.* = 2;
}
