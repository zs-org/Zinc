usingnamespace @import("../zinc/zincstd.zig");
fn complex_test()  !void{
    var __local_allocator_1 = std.heap.ArenaAllocator.init(zinc_allocator);
    defer __local_allocator_1.deinit();

    const a = try __local_allocator_1.allocator().create(i32); a.* = 1;
    {
        var b: ?*i32 = try _zinc_alloc(i32); defer _zinc_dealloc(&b); b.* = 2;
        {
            var c: ?*i32 = try _zinc_alloc(i32); defer _zinc_dealloc(&c); c.* = 3;
            var d: ?*i32 = try _zinc_alloc(i32); d.* = 4;
            var e = d; d = null;
            _zinc_dealloc(&e);
        }
    }
    {
    var __fix_buffer_1: [512]u8 = undefined;
    var __fix_allocator_1 = std.heap.FixedBufferAllocator.init(&__fix_buffer_1);

        const f = try __fix_allocator_1.allocator().create(i32); f.* = 6;
        {
    var __fix_buffer_2: [256]u8 = undefined;
    var __fix_allocator_2 = std.heap.FixedBufferAllocator.init(&__fix_buffer_2);

            const g = try __fix_allocator_2.allocator().create(i32); g.* = 7;
        }
    }
}
