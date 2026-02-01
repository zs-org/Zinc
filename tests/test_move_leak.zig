usingnamespace @import("../zinc/zincstd.zig");
fn move_leak_test()  !void{
    var x: ?*i32 = try _zinc_alloc(i32); x.* = 42
    var y = x; x = null
}
