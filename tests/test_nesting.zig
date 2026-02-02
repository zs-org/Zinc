usingnamespace @import("../zinc/zincstd.zig");
fn nested_test()  !void{
    if (true) {
        var a: ?*i32 = null; defer _zinc_dealloc(&a); a = try _zinc_alloc(i32); a.* = 1;
        while (false) {
            var b: ?*i32 = null; defer _zinc_dealloc(&b); b = try _zinc_alloc(i32); b.* = 2;
            if (true) {
                var c: ?*i32 = null; c = try _zinc_alloc(i32); c.* = 3;
                _zinc_dealloc(&c);
            }
        }
    }
}
