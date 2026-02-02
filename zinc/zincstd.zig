const std = @import("std");

var gpa = std.heap.GeneralPurposeAllocator(.{}){};
pub const zinc_gpa = gpa.allocator();
pub var zinc_allocator: std.mem.Allocator = zinc_gpa;

pub fn _zinc_alloc(comptime T: type) !*T {
    return zinc_allocator.create(T);
}

pub fn _zinc_dealloc(ptr_to_opt_ptr: anytype) void {
    // Expected type of ptr_to_opt_ptr is *?*T
    if (ptr_to_opt_ptr.*) |ptr| {
        zinc_allocator.destroy(ptr);
        ptr_to_opt_ptr.* = null;
    }
}

pub fn zinc_deinit() void {
    _ = gpa.deinit();
}
