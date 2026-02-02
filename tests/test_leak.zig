usingnamespace @import("../zinc/zincstd.zig");
fn leak_test()  !void{
    var x: ?*i32 = null; x = try _zinc_alloc(i32); x.* = 42;
}
