usingnamespace @import("../zinc/zincstd.zig");
fn nested_test()  !void{
    if (true) {
        var a: ?*i32 = try _zinc_alloc(i32); defer _zinc_dealloc(&a); a.* = 1;
        while (false) {
            var b: ?*i32 = try _zinc_alloc(i32); defer _zinc_dealloc(&b); b.* = 2;
            if (true) {
                var c: ?*i32 = try _zinc_alloc(i32); c.* = 3;
                _zinc_dealloc(&c);
            }
        }
    }
}
