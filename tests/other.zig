usingnamespace @import("../zinc/zincstd.zig");
pub fn foo()  !void{
    var __local_allocator_1 = std.heap.ArenaAllocator.init(zinc_allocator);
    defer __local_allocator_1.deinit();

    const x = try __local_allocator_1.allocator().create(i32); x.* = 1;
}
