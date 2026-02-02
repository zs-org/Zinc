usingnamespace @import("../zinc/zincstd.zig");
fn test_local_escape()  !void{
    var __local_allocator_1 = std.heap.ArenaAllocator.init(zinc_allocator);
    defer __local_allocator_1.deinit();

    const x = try __local_allocator_1.allocator().create(i32); x.* = 10;
    return x
}

fn test_def_escape()  !void{
    {
        var y: ?*i32 = try _zinc_alloc(i32); defer _zinc_dealloc(&y); y.* = 20;
        return y
    }
}
