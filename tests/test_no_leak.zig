usingnamespace @import("../zinc/zincstd.zig");
fn no_leak_test()  !void{
    var x: ?*i32 = null; x = try _zinc_alloc(i32); x.* = 42;
    _zinc_dealloc(&x);
}
