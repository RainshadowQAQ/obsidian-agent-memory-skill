#!/usr/bin/env python3
"""知识库小工具：只输出需要的片段，减少 AI 读取整篇文件。

用法（在任意目录运行，默认检查仓库内的 example-vault/，也可用 --kb 指定任意知识库目录）：
  python3 tools/kb.py [--kb PATH] notes [--area AREA] [--kind KIND]   列出笔记及属性
  python3 tools/kb.py [--kb PATH] outline NOTE                        列出标题与行号
  python3 tools/kb.py [--kb PATH] section NOTE HEADING                读取一个段落（标题可部分匹配）
  python3 tools/kb.py [--kb PATH] lines NOTE START END                读取指定行
  python3 tools/kb.py [--kb PATH] find KEYWORD [--area AREA] [--sources]  搜索关键词
  python3 tools/kb.py [--kb PATH] src SOURCE_ID                       读取一条来源记录
  python3 tools/kb.py [--kb PATH] next-id PREFIX                      给出下一个来源编号，如 src-alpha-20261009
  python3 tools/kb.py [--kb PATH] check                               检查内部链接与 src 锚点

NOTE 可写文件名（不带 .md）、部分名称或相对知识库根的路径。
"""
import os
import re
import sys
import urllib.parse

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_KB = os.path.join(REPO_ROOT, "example-vault")
SKIP = ("/Pages/", "/Extracts/", "/Originals/")

KB = os.path.abspath(os.environ.get("OBSIDIAN_KB_DIR", DEFAULT_KB))
VAULT = os.path.dirname(KB)


def md_files(sub=""):
    root = os.path.join(KB, sub) if sub else KB
    if not os.path.exists(root):
        return
    for d, dirs, fs in os.walk(root):
        dirs[:] = [x for x in dirs if not x.startswith(".")]
        for f in sorted(fs):
            p = os.path.join(d, f)
            if f.endswith(".md") and not any(s in p for s in SKIP):
                yield p


def rel(p):
    return os.path.relpath(p, KB)


def read(p):
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def frontmatter(text):
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    fm = {}
    for line in text[4:end].split("\n"):
        m = re.match(r"^([A-Za-z_]+):\s*(.*)$", line)
        if m and m.group(2):
            fm[m.group(1)] = m.group(2).strip("'\"")
    return fm


def resolve(name):
    cand = os.path.join(KB, name if name.endswith(".md") else name + ".md")
    if os.path.exists(cand):
        return cand
    allp = list(md_files())
    exact = [p for p in allp if os.path.basename(p)[:-3] == name]
    if len(exact) == 1:
        return exact[0]
    part = [p for p in allp if name.lower() in os.path.basename(p).lower()]
    if len(part) == 1:
        return part[0]
    topics = [p for p in part if rel(p).startswith("Topics")]
    if len(topics) == 1:
        return topics[0]
    if not part:
        sys.exit(f"找不到笔记：{name}")
    sys.exit("匹配多篇，请写得更具体：\n" + "\n".join(rel(p) for p in part))


def headings(lines):
    for i, l in enumerate(lines, 1):
        m = re.match(r"^(#{1,6})\s+(.*)$", l)
        if m:
            yield i, len(m.group(1)), m.group(2).strip()


def section_of(lines, lineno):
    cur = ""
    for i, _, h in headings(lines):
        if i > lineno:
            break
        cur = h
    return cur


def cmd_notes(args):
    area = args[args.index("--area") + 1] if "--area" in args else None
    kind = args[args.index("--kind") + 1] if "--kind" in args else None
    sub = "Sources" if kind == "source" else "Topics"
    for p in md_files(sub):
        t = read(p)
        fm = frontmatter(t)
        if area and fm.get("area") != area:
            continue
        if kind and fm.get("kind") != kind:
            continue
        kb = len(t.encode("utf-8")) // 1024
        print(f"{rel(p)} | area={fm.get('area','-')} kind={fm.get('kind','-')} "
              f"status={fm.get('status','-')} updated={fm.get('updated','-')} | {kb}KB")


def cmd_outline(args):
    p = resolve(args[0])
    lines = read(p).split("\n")
    print(f"{rel(p)}（{len(lines)} 行）")
    for i, lvl, h in headings(lines):
        print(f"{i:>5}  {'  ' * (lvl - 1)}{h}")


def cmd_section(args):
    p = resolve(args[0])
    key = " ".join(args[1:])
    lines = read(p).split("\n")
    hs = list(headings(lines))
    hits = [(i, lvl, h) for i, lvl, h in hs if key in h]
    if not hits:
        sys.exit(f"{rel(p)} 中没有包含“{key}”的标题")
    if len(hits) > 1:
        sys.exit("多个标题匹配：\n" + "\n".join(f"{i} {h}" for i, _, h in hits))
    start, lvl, _ = hits[0]
    end = len(lines)
    for i, l2, _ in hs:
        if i > start and l2 <= lvl:
            end = i - 1
            break
    print(f"# {rel(p)} L{start}-{end}")
    print("\n".join(lines[start - 1:end]).rstrip())


def cmd_lines(args):
    p = resolve(args[0])
    a, b = int(args[1]), int(args[2])
    lines = read(p).split("\n")
    print(f"# {rel(p)} L{a}-{b}")
    print("\n".join(lines[a - 1:b]))


def cmd_find(args):
    area = args[args.index("--area") + 1] if "--area" in args else None
    words = [a for i, a in enumerate(args) if not a.startswith("--")
             and (i == 0 or args[i - 1] != "--area")]
    key = " ".join(words).lower()
    subs = ["Topics", "Sources"] if "--sources" in args else ["Topics"]
    n = 0
    for sub in subs:
        for p in md_files(sub):
            t = read(p)
            if area and frontmatter(t).get("area") != area:
                continue
            lines = t.split("\n")
            for i, l in enumerate(lines, 1):
                if key in l.lower():
                    n += 1
                    if n > 40:
                        print("……结果超过 40 条，请缩小关键词")
                        return
                    snippet = l.strip()
                    pos = snippet.lower().find(key)
                    snippet = snippet[max(0, pos - 40):pos + 80]
                    print(f"{rel(p)}:{i} [{section_of(lines, i)}] {snippet}")
    if n == 0:
        print("无结果")


def cmd_src(args):
    sid = args[0]
    for p in md_files("Sources"):
        lines = read(p).split("\n")
        for i, l in enumerate(lines):
            if l.strip() == f"## {sid}":
                j = i + 1
                while j < len(lines) and not lines[j].startswith("## "):
                    j += 1
                print(f"# {rel(p)} L{i + 1}-{j}")
                print("\n".join(lines[i:j]).rstrip())
                return
    sys.exit(f"找不到来源：{sid}")


def cmd_next_id(args):
    prefix = args[0].rstrip("-")
    best, where = 0, None
    pat = re.compile(r"^## " + re.escape(prefix) + r"-(\d+)\s*$")
    for p in md_files("Sources"):
        for l in read(p).split("\n"):
            m = pat.match(l)
            if m and int(m.group(1)) >= best:
                best, where = int(m.group(1)), rel(p)
    print(f"{prefix}-{best + 1:02d}" + (f"（现有最大编号在 {where}）" if where else "（此前缀尚无记录）"))


def cmd_check(args):
    allfiles = []
    for d, dirs, fs in os.walk(KB):
        dirs[:] = [x for x in dirs if not x.startswith(".")]
        allfiles += [os.path.join(d, f) for f in fs]
    names = {}
    for p in allfiles:
        b = os.path.basename(p)
        names.setdefault(b, []).append(p)
        if b.endswith(".md"):
            names.setdefault(b[:-3], []).append(p)
    cache = {}

    def anchors(path):
        if path not in cache:
            s = set()
            try:
                t = read(path)
            except (OSError, UnicodeDecodeError):
                t = ""
            for m in re.finditer(r"^#{1,6}\s+(.*)$", t, re.M):
                s.add(m.group(1).strip())
            for m in re.finditer(r'<a (?:id|name)="([^"]+)"', t):
                s.add(m.group(1))
            for m in re.finditer(r"\^([A-Za-z0-9-]+)\s*$", t, re.M):
                s.add("^" + m.group(1))
            cache[path] = s
        return cache[path]

    md_re = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)\)")
    wk_re = re.compile(r"!?\[\[([^\]|#]+)")
    bad = total = 0
    for p in allfiles:
        if not p.endswith((".md", ".base")):
            continue
        t = re.sub(r"```.*?```", "", read(p), flags=re.S)
        for u in md_re.findall(t):
            if re.match(r"^[a-z]+:", u) or u.startswith("#"):
                continue
            total += 1
            path, _, anc = u.partition("#")
            tgt = os.path.normpath(os.path.join(os.path.dirname(p), urllib.parse.unquote(path)))
            if not os.path.exists(tgt):
                bad += 1
                print("缺文件", rel(p), "->", u)
            elif anc and tgt.endswith(".md") and urllib.parse.unquote(anc) not in anchors(tgt):
                bad += 1
                print("缺锚点", rel(p), "->", u)
        for w in wk_re.findall(t):
            w = w.strip().replace("\\", "")
            total += 1
            in_kb = os.path.join(KB, w)
            in_vault = os.path.join(VAULT, w)
            if not (os.path.exists(in_kb) or os.path.exists(in_kb + ".md")
                    or os.path.exists(in_vault) or os.path.exists(in_vault + ".md")
                    or ("/" not in w and (w in names or w + ".md" in names))):
                bad += 1
                print("缺 wikilink", rel(p), "->", w)
    print(f"检查 {total} 条链接，问题 {bad} 条")
    sys.exit(1 if bad else 0)


CMDS = {"notes": cmd_notes, "outline": cmd_outline, "section": cmd_section, "lines": cmd_lines,
        "find": cmd_find, "src": cmd_src, "next-id": cmd_next_id, "check": cmd_check}


def parse_kb_arg(argv):
    global KB, VAULT
    if "--kb" in argv:
        idx = argv.index("--kb")
        if idx + 1 >= len(argv):
            sys.exit("--kb 需要指定目录路径")
        KB = os.path.abspath(argv[idx + 1])
        VAULT = os.path.dirname(KB)
        argv = argv[:idx] + argv[idx + 2:]
    return argv


if __name__ == "__main__":
    argv = parse_kb_arg(sys.argv[1:])
    if not argv or argv[0] not in CMDS:
        print(__doc__)
        sys.exit(0)
    if not os.path.isdir(KB):
        sys.exit(f"知识库目录不存在：{KB}")
    CMDS[argv[0]](argv[1:])
