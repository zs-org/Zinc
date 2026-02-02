usingnamespace @import("../zinc/zincstd.zig");
fn test_move()  !void{
    var x: ?*i32 = null; x = try _zinc_alloc(i32); x.* = 10;
    var y = x; x = null;
    _zinc_dealloc(&y);
}
