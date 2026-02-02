usingnamespace @import("../zinc/zincstd.zig");
fn test_def()  !void{
    {
        var x: ?*i32 = null; defer _zinc_dealloc(&x); x = try _zinc_alloc(i32); x.* = 100;
    }
}
