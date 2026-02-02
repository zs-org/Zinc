usingnamespace @import("../zinc/zincstd.zig");
fn test_post_move()  !void{
    var a: ?*i32 = null; a = try _zinc_alloc(i32); a.* = 10;
    var b = a; a = null;

        @import("std").debug.print("a: {any}\n", .{a});

    _zinc_dealloc(&b);
}

fn test_move_again()  !void{
    var c: ?*i32 = null; c = try _zinc_alloc(i32); c.* = 20;
    var d = c; c = null;
    var e = c; c = null;
    _zinc_dealloc(&d);
}

fn test_borrow_after_move()  !void{
    var f: ?*i32 = null; f = try _zinc_alloc(i32); f.* = 30;
    var g = f; f = null;
    const h = f;
    _zinc_dealloc(&g);
}

fn test_free_after_move()  !void{
    var i: ?*i32 = null; i = try _zinc_alloc(i32); i.* = 40;
    var j = i; i = null;
    _zinc_dealloc(&i);
    _zinc_dealloc(&j);
}
