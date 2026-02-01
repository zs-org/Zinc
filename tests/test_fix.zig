usingnamespace @import("../zinc/zincstd.zig");
fn test_fix()  !void{
    {
    var __fix_buffer_1: [1024]u8 = undefined;
    var __fix_allocator_1 = std.heap.FixedBufferAllocator.init(&__fix_buffer_1);

        const x = try __fix_allocator_1.allocator().create(i32); x.* = 42;
    }
}
