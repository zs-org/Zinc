import re
import os
import sys

class FZC:
    def __init__(self, root_dir=None):
        self.root_dir = os.path.abspath(root_dir or os.getcwd())
        self.processed_files = set()
        self.output_files = set()
        self.local_alloc_idx = 0
        self.fix_alloc_idx = 0
        self.current_local_arena = None
        self.fix_alloc_stack = []
        self.errors = []

    def get_next_local_arena_name(self):
        self.local_alloc_idx += 1
        return f"__local_allocator_{self.local_alloc_idx}"

    def get_next_fix_alloc_name(self):
        self.fix_alloc_idx += 1
        return f"__fix_allocator_{self.fix_alloc_idx}", f"__fix_buffer_{self.fix_alloc_idx}"

    def tokenize(self, code):
        token_specification = [
            ('ZIG_ESC',  r'@@[a-zA-Z_][a-zA-Z0-9_]*'),
            ('STRING',   r'"(?:[^"\\]|\\.)*"'),
            ('COMMENT',  r'//.*'),
            ('MOVE',     r'->'),
            ('ID',       r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('NUMBER',   r'\d+'),
            ('LBRACE',   r'\{'),
            ('RBRACE',   r'\}'),
            ('LPAREN',   r'\('),
            ('RPAREN',   r'\)'),
            ('COLON',    r':'),
            ('SEMICOLON',r';'),
            ('EQ',       r'='),
            ('COMMA',    r','),
            ('DOT',      r'\.'),
            ('WHITESPACE', r'\s+'),
            ('OTHER',    r'\S'),
        ]
        tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
        tokens = []
        for mo in re.finditer(tok_regex, code):
            kind = mo.lastgroup
            value = mo.group()
            if kind == 'COMMENT':
                continue
            tokens.append((kind, value))
        return tokens

    def transpile(self, zn_path):
        zn_path = os.path.abspath(zn_path)
        if zn_path in self.processed_files:
            return
        self.processed_files.add(zn_path)

        if not os.path.exists(zn_path):
            print(f"Error: {zn_path} not found")
            return

        with open(zn_path, 'r') as f:
            code = f.read()

        tokens = self.tokenize(code)

        zig_path = zn_path.replace('.zn', '.zig')
        self.output_files.add(zig_path)

        result = []

        # Calculate relative path to zinc/zincstd.zig
        rel_to_root = os.path.relpath(self.root_dir, os.path.dirname(zn_path))
        if rel_to_root == '.':
            zincstd_path = "zinc/zincstd.zig"
        else:
            zincstd_path = os.path.join(rel_to_root, "zinc/zincstd.zig").replace(os.sep, '/')

        result.append(f'usingnamespace @import("{zincstd_path}");\n')

        i = 0
        while i < len(tokens):
            kind, value = tokens[i]

            if kind == 'ID' and value == 'import':
                start_i = i
                i += 1
                while i < len(tokens) and tokens[i][0] == 'WHITESPACE': i += 1
                if i < len(tokens):
                    # Consume full import path
                    path_parts = []
                    allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_./')
                    while i < len(tokens) and tokens[i][0] in ('ID', 'DOT', 'OTHER'):
                        if all(c in allowed_chars for c in tokens[i][1]):
                            path_parts.append(tokens[i][1])
                            i += 1
                        else:
                            break
                    mod_name = "".join(path_parts)
                    alias = mod_name.split('/')[-1].split('.')[-1]
                    while i < len(tokens) and tokens[i][0] == 'WHITESPACE': i += 1
                    if i < len(tokens) and tokens[i][1] == 'as':
                        i += 1
                        while i < len(tokens) and tokens[i][0] == 'WHITESPACE': i += 1
                        if i < len(tokens):
                            alias = tokens[i][1]
                            i += 1

                    result.append(f'const {alias} = @import("{mod_name.replace(".zn", "").replace(os.sep, "/")}.zig");')

                    # Crawl
                    mod_path = os.path.join(os.path.dirname(zn_path), f"{mod_name}.zn")
                    if os.path.exists(mod_path):
                        self.transpile(mod_path)
                    continue
                else:
                    i = start_i

            if kind == 'ID' and value == 'fn':
                sig_tokens = []
                while i < len(tokens) and tokens[i][0] != 'LBRACE':
                    sig_tokens.append(tokens[i])
                    i += 1

                if i < len(tokens) and tokens[i][0] == 'LBRACE':
                    body_tokens, next_i = self.get_block(tokens, i)
                    result.append(self.transform_function(sig_tokens, body_tokens, zn_path))
                    i = next_i
                    continue

            if kind == 'ZIG_ESC':
                result.append(value[2:])
            else:
                result.append(value)
            i += 1

        with open(zig_path, 'w') as f:
            f.write("".join(result))

    def get_block(self, tokens, start_i):
        brace_level = 0
        block_tokens = []
        for i in range(start_i, len(tokens)):
            kind, value = tokens[i]
            block_tokens.append(tokens[i])
            if kind == 'LBRACE':
                brace_level += 1
            elif kind == 'RBRACE':
                brace_level -= 1
                if brace_level == 0:
                    return block_tokens, i + 1
        return block_tokens, len(tokens)

    def transform_function(self, sig_tokens, body_tokens, zn_path):
        uses_local = any(t[1] == 'local' for t in body_tokens)
        uses_def = any(t[1] == 'def' for t in body_tokens)
        uses_safe = any(t[1] == 'safe' for t in body_tokens)
        uses_raw = any(t[1] == 'raw' for t in body_tokens)
        uses_fix = any(t[1] == 'fix' or t[1] == 'fixblock' for t in body_tokens)

        needs_try = uses_local or uses_def or uses_safe or uses_raw or uses_fix or any(t[1] == 'try' for t in body_tokens)

        last_rparen_idx = -1
        for idx, t in enumerate(sig_tokens):
            if t[0] == 'RPAREN':
                last_rparen_idx = idx

        if last_rparen_idx != -1:
            has_ret = False
            for t in sig_tokens[last_rparen_idx+1:]:
                if t[0] == 'ID' or t[0] == 'OTHER' or t[0] == 'ZIG_ESC':
                    has_ret = True
                    break

            if not has_ret:
                sig_tokens.append(('WHITESPACE', ' '))
                if needs_try:
                    sig_tokens.append(('OTHER', '!'))
                sig_tokens.append(('ID', 'void'))
            elif needs_try:
                # Ensure it has !
                sig_str = "".join(t[1] for t in sig_tokens)
                if '!' not in sig_str:
                    for idx in range(last_rparen_idx + 1, len(sig_tokens)):
                        if sig_tokens[idx][0] in ('ID', 'OTHER'):
                            sig_tokens.insert(idx, ('OTHER', '!'))
                            break

        sig_res = "".join(t[1] for t in sig_tokens)

        old_local_arena = self.current_local_arena
        if uses_local:
            self.current_local_arena = self.get_next_local_arena_name()
        else:
            self.current_local_arena = None

        tracked_safe_vars = set()
        local_vars = set()
        if uses_local:
            # We will populate this as we parse the body
            pass

        transformed_body = self.transform_block(body_tokens, tracked_safe_vars, local_vars=local_vars, def_vars=set(), zn_path=zn_path)

        # Report leaks
        func_name_tokens = []
        for t in sig_tokens:
            if t[0] == 'LPAREN': break
            if t[0] == 'ID' and t[1] != 'fn':
                func_name_tokens.append(t[1])
        func_name = "".join(func_name_tokens).strip()
        for var in tracked_safe_vars:
            print(f"Error in {zn_path}: Function '{func_name}' forgets to free safe variable '{var}'")

        if uses_local:
            arena_init = f"\n    var {self.current_local_arena} = std.heap.ArenaAllocator.init(zinc_allocator);\n    defer {self.current_local_arena}.deinit();\n"
            transformed_body = transformed_body[0:1] + arena_init + transformed_body[1:]

        self.current_local_arena = old_local_arena
        return sig_res + transformed_body

    def transform_block(self, tokens, tracked_safe_vars, local_vars, def_vars, zn_path):
        res = []
        i = 0
        while i < len(tokens):
            kind, value = tokens[i]

            if kind == 'LBRACE':
                if i == 0:
                    res.append(value)
                    i += 1
                    continue
                else:
                    body_tokens, next_i = self.get_block(tokens, i)
                    inner_def_vars = set(def_vars)
                    transformed_inner_body = self.transform_block(body_tokens, tracked_safe_vars, local_vars, inner_def_vars, zn_path)
                    res.append(transformed_inner_body)
                    i = next_i
                    continue

            if kind == 'ID' and value == 'local':
                decl, next_i = self.parse_decl(tokens, i)
                res.append(f"const {decl['name']} = try {self.current_local_arena}.allocator().create({decl['type']}); {decl['name']}.* = {decl['expr']};")
                local_vars.add(decl['name'])
                i = next_i
                continue

            if kind == 'ID' and value == 'def':
                mut = False
                i += 1
                while i < len(tokens) and tokens[i][0] == 'WHITESPACE': i += 1
                if tokens[i][1] == 'mut':
                    mut = True
                    i += 1
                decl, next_i = self.parse_decl(tokens, i, skip_keyword=True)
                res.append(f"var {decl['name']}: ?*{decl['type']} = try _zinc_alloc({decl['type']}); defer _zinc_dealloc(&{decl['name']}); {decl['name']}.* = {decl['expr']};")
                def_vars.add(decl['name'])
                i = next_i
                continue

            if kind == 'ID' and value == 'safe':
                i += 1
                while i < len(tokens) and tokens[i][0] == 'WHITESPACE': i += 1
                if tokens[i][1] == 'mut':
                    i += 1
                decl, next_i = self.parse_decl(tokens, i, skip_keyword=True)
                res.append(f"var {decl['name']}: ?*{decl['type']} = try _zinc_alloc({decl['type']}); {decl['name']}.* = {decl['expr']};")
                tracked_safe_vars.add(decl['name'])
                i = next_i
                continue

            if kind == 'ID' and value == 'raw':
                i += 1
                while i < len(tokens) and tokens[i][0] == 'WHITESPACE': i += 1
                if tokens[i][1] == 'mut':
                    i += 1
                decl, next_i = self.parse_decl(tokens, i, skip_keyword=True)
                res.append(f"var {decl['name']}: ?*{decl['type']} = try zinc_allocator.create({decl['type']}); {decl['name']}.* = {decl['expr']};")
                i = next_i
                continue

            if kind == 'ID' and value == 'fixblock':
                i += 1
                while i < len(tokens) and tokens[i][0] != 'LPAREN': i += 1
                i += 1 # skip (
                limit_tokens = []
                while i < len(tokens) and tokens[i][0] != 'RPAREN':
                    limit_tokens.append(tokens[i][1])
                    i += 1
                limit = "".join(limit_tokens)
                i += 1 # skip )
                while i < len(tokens) and tokens[i][0] != 'LBRACE': i += 1

                body_tokens, next_i = self.get_block(tokens, i)
                fba_name, buf_name = self.get_next_fix_alloc_name()
                self.fix_alloc_stack.append(fba_name)
                # def_vars are block-scoped, so we create a new set for the inner block but it can see outer def_vars too?
                # Actually, Zinc design says def is block-scoped lifetime.
                inner_def_vars = set(def_vars)
                transformed_inner_body = self.transform_block(body_tokens, tracked_safe_vars, local_vars, inner_def_vars, zn_path)
                fixblock_res = f"{{\n    var {buf_name}: [{limit}]u8 = undefined;\n    var {fba_name} = std.heap.FixedBufferAllocator.init(&{buf_name});\n"
                fixblock_res += transformed_inner_body[1:]
                res.append(fixblock_res)
                self.fix_alloc_stack.pop()
                i = next_i
                continue

            if kind == 'ID' and value == 'fix':
                decl, next_i = self.parse_decl(tokens, i)
                fba_name = self.fix_alloc_stack[-1]
                res.append(f"const {decl['name']} = try {fba_name}.allocator().create({decl['type']}); {decl['name']}.* = {decl['expr']};")
                i = next_i
                continue

            if kind == 'ID' and value == 'move':
                i += 1
                while i < len(tokens) and tokens[i][0] == 'WHITESPACE': i += 1
                src = tokens[i][1]
                i += 1
                while i < len(tokens) and tokens[i][0] != 'MOVE': i += 1
                i += 1 # skip ->
                while i < len(tokens) and tokens[i][0] == 'WHITESPACE': i += 1
                dst = tokens[i][1]
                i += 1
                res.append(f"var {dst} = {src}; {src} = null;")
                if src in tracked_safe_vars:
                    tracked_safe_vars.remove(src)
                    tracked_safe_vars.add(dst)
                continue

            if kind == 'ID' and value == 'borrow':
                i += 1
                while i < len(tokens) and tokens[i][0] == 'WHITESPACE': i += 1
                src = tokens[i][1]
                i += 1
                while i < len(tokens) and tokens[i][0] != 'MOVE': i += 1
                i += 1 # skip ->
                while i < len(tokens) and tokens[i][0] == 'WHITESPACE': i += 1
                dst = tokens[i][1]
                i += 1
                res.append(f"const {dst} = {src};")
                continue

            if kind == 'ID' and value == 'free':
                i += 1
                while i < len(tokens) and tokens[i][0] != 'LPAREN': i += 1
                i += 1 # skip (
                while i < len(tokens) and tokens[i][0] == 'WHITESPACE': i += 1
                var_name = tokens[i][1]
                i += 1
                while i < len(tokens) and tokens[i][0] != 'RPAREN': i += 1
                i += 1 # skip )
                res.append(f"_zinc_dealloc(&{var_name});")
                if var_name in tracked_safe_vars:
                    tracked_safe_vars.remove(var_name)
                continue

            if kind == 'ID' and value == 'zig':
                i += 1
                while i < len(tokens) and tokens[i][0] != 'LBRACE': i += 1
                body_tokens, next_i = self.get_block(tokens, i)
                verbatim = "".join(t[1] for t in body_tokens[1:-1])
                res.append(verbatim)
                i = next_i
                continue

            if kind == 'ID' and value == 'return':
                j = i + 1
                while j < len(tokens) and tokens[j][0] == 'WHITESPACE': j += 1
                if j < len(tokens) and tokens[j][0] == 'ID':
                    ret_var = tokens[j][1]
                    if ret_var in local_vars:
                        print(f"Error in {zn_path}: Cannot return local variable '{ret_var}'")
                    if ret_var in def_vars:
                        print(f"Error in {zn_path}: Cannot return def variable '{ret_var}'")

            if kind == 'ZIG_ESC':
                res.append(value[2:])
            else:
                res.append(value)
            i += 1
        return "".join(res)

    def parse_decl(self, tokens, i, skip_keyword=False):
        if not skip_keyword:
            i += 1
        while i < len(tokens) and tokens[i][0] == 'WHITESPACE': i += 1
        name = tokens[i][1]
        i += 1
        while i < len(tokens) and tokens[i][0] != 'COLON': i += 1
        i += 1
        while i < len(tokens) and tokens[i][0] == 'WHITESPACE': i += 1
        type_tokens = []
        while i < len(tokens) and tokens[i][0] != 'EQ':
            type_tokens.append(tokens[i][1])
            i += 1
        type_name = "".join(type_tokens).strip()
        i += 1
        while i < len(tokens) and tokens[i][0] == 'WHITESPACE': i += 1
        expr_tokens = []
        while i < len(tokens) and '\n' not in tokens[i][1] and tokens[i][1] != ';' and tokens[i][0] != 'RBRACE':
            expr_tokens.append(tokens[i][1])
            i += 1
        expr = "".join(expr_tokens).strip()
        return {'name': name, 'type': type_name, 'expr': expr}, i

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: fzc.py <file.zn>")
        sys.exit(1)

    fzc = FZC()
    fzc.transpile(sys.argv[1])
