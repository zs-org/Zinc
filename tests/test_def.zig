usingnamespace @import("../zinc/zincstd.zig");
fn test_def()  !void{
    {
        var x: ?*i32 = try _zinc_alloc(i32); defer _zinc_dealloc(&x); x.* = 100
    }
}
