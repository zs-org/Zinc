usingnamespace @import("../zinc/zincstd.zig");
fn test_leak()  !void{
    var x: ?*i32 = try _zinc_alloc(i32); x.* = 10;

}

fn test_no_leak()  !void{
    var y: ?*i32 = try _zinc_alloc(i32); y.* = 20;
    _zinc_dealloc(&y);
}

fn test_move_no_leak()  !void{
    var a: ?*i32 = try _zinc_alloc(i32); a.* = 30;
    var b = a; a = null;
    _zinc_dealloc(&b);
}

fn test_move_leak()  !void{
    var c: ?*i32 = try _zinc_alloc(i32); c.* = 40;
    var d = c; c = null;

}
