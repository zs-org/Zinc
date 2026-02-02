usingnamespace @import("../zinc/zincstd.zig");
fn test_mut()  !void{
    var x: ?*i32 = null; defer _zinc_dealloc(&x); x = try _zinc_alloc(i32); x.* = 1;
    var y: ?*i32 = null; y = try _zinc_alloc(i32); y.* = 2;
    x.* = 10
    y.* = 20
    _zinc_dealloc(&y);
}
