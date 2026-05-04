#!/usr/bin/env python3
from html import escape
from pathlib import Path

BOARD = 32
X0 = 48
Y0 = 58

pieces = {
    "a1": "♖", "b1": "♘", "c1": "♗", "d1": "♕", "e1": "♔", "f1": "♗", "g1": "♘", "h1": "♖",
    "a2": "♙", "b2": "♙", "c2": "♙", "d2": "♙", "e2": "♙", "f2": "♙", "g2": "♙", "h2": "♙",
    "a7": "♟", "b7": "♟", "c7": "♟", "d7": "♟", "e7": "♟", "f7": "♟", "g7": "♟", "h7": "♟",
    "a8": "♜", "b8": "♞", "c8": "♝", "d8": "♛", "e8": "♚", "f8": "♝", "g8": "♞", "h8": "♜",
}

# Legal trap: 1. e4 e5 2. Nf3 d6 3. Bc4 Bg4 4. Nc3 g6 5. Nxe5 Bxd1 6. Bxf7+ Ke7 7. Nd5#
moves = [
    ("1. e4", "e2", "e4"),
    ("1... e5", "e7", "e5"),
    ("2. Nf3", "g1", "f3"),
    ("2... d6", "d7", "d6"),
    ("3. Bc4", "f1", "c4"),
    ("3... Bg4", "c8", "g4"),
    ("4. Nc3", "b1", "c3"),
    ("4... g6", "g7", "g6"),
    ("5. Nxe5", "f3", "e5"),
    ("5... Bxd1", "g4", "d1"),
    ("6. Bxf7+", "c4", "f7"),
    ("6... Ke7", "e8", "e7"),
    ("7. Nd5#", "c3", "d5"),
]

states = [pieces.copy()]
state = pieces.copy()
for _, src, dst in moves:
    piece = state.pop(src)
    state.pop(dst, None)
    state[dst] = piece
    states.append(state.copy())


def square_xy(square):
    file = ord(square[0]) - ord("a")
    rank = int(square[1])
    return X0 + file * BOARD + BOARD / 2, Y0 + (8 - rank) * BOARD + BOARD / 2


def visibility(values, dur="14s"):
    return f'<animate attributeName="opacity" values="{values}" dur="{dur}" repeatCount="indefinite" calcMode="discrete"/>'


def piece_color(piece):
    return "white-piece" if piece in "♔♕♖♗♘♙" else "black-piece"


def render_board():
    out = [f'<g transform="translate(0 0)">']
    out.append(f'<rect x="{X0-2}" y="{Y0-2}" width="{BOARD*8+4}" height="{BOARD*8+4}" rx="10" fill="#0b1118" stroke="#30363d"/>')
    for r in range(8):
        for f in range(8):
            x = X0 + f * BOARD
            y = Y0 + r * BOARD
            cls = "sq-light" if (r + f) % 2 == 0 else "sq-dark"
            out.append(f'<rect class="{cls}" x="{x}" y="{y}" width="{BOARD}" height="{BOARD}"/>')
    for f, letter in enumerate("abcdefgh"):
        out.append(f'<text class="coord" x="{X0 + f*BOARD + BOARD/2}" y="{Y0 + BOARD*8 + 18}">{letter}</text>')
    for r in range(8):
        out.append(f'<text class="coord" x="{X0 - 14}" y="{Y0 + r*BOARD + BOARD/2 + 4}">{8-r}</text>')
    out.append('</g>')
    return "\n".join(out)


def render_state_pieces():
    out = []
    total = len(states)
    for i, st in enumerate(states):
        vals = ["1" if j == i else "0" for j in range(total)]
        # Keep final board visible slightly longer by making state 13 visible for the wrap frame too.
        if i == total - 1:
            vals[-1] = "1"
        out.append(f'<g opacity="0">{visibility(";".join(vals))}')
        for sq, pc in sorted(st.items()):
            x, y = square_xy(sq)
            out.append(f'<text class="piece {piece_color(pc)}" x="{x:.1f}" y="{y:.1f}">{pc}</text>')
        out.append('</g>')
    return "\n".join(out)

def render_current_move():
    labels = ["start"] + [m[0] for m in moves]
    out = []
    for i, label in enumerate(labels):
        vals = ["1" if j == i else "0" for j in range(len(labels))]
        if i == len(labels) - 1:
            vals[-1] = "1"
        out.append(f'<text class="status" x="610" y="108" opacity="0">move: {escape(label)}{visibility(";".join(vals))}</text>')
    return "\n".join(out)

svg = f'''<svg width="900" height="380" viewBox="0 0 900 380" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="title desc">
  <title id="title">Legal Trap chess replay</title>
  <desc id="desc">Animated replay of the Legal Trap chess sequence ending with 7. Nd5 checkmate.</desc>
  <defs>
    <filter id="glow" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <style>
      .bg {{ fill: #0d1117; }}
      .sq-dark {{ fill: #161b22; }}
      .sq-light {{ fill: #1f2937; }}
      .white-piece {{ fill: #f0f6fc; }}
      .black-piece {{ fill: #8b949e; }}
      .piece {{ font: 23px Georgia, serif; text-anchor: middle; dominant-baseline: middle; }}
      .prompt {{ fill: #7ee787; font: 600 15px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
      .dim {{ fill: #6e7681; font: 13px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
      .move {{ fill: #8b949e; font: 14px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
      .move-hot {{ fill: #ffa657; font: 700 14px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; filter: url(#glow); }}
      .status {{ fill: #7ee787; font: 700 15px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
      .mate {{ fill: #ff7b72; font: 800 28px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; filter: url(#glow); }}
      .coord {{ fill: #6e7681; font: 11px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; text-anchor: middle; }}
      .box {{ fill: #0b1118; stroke: #30363d; }}
    </style>
  </defs>

  <rect class="bg" width="900" height="380" rx="14"/>
  <text class="prompt" x="34" y="34">plastfw@github:~$ ./chess --replay legal-trap</text>
  <text class="dim" x="34" y="350">full replay · Legal Trap · final move: 7. Nd5#</text>

  {render_board()}
  {render_state_pieces()}

  <rect class="box" x="340" y="56" width="220" height="214" rx="10"/>
  <text class="prompt" x="360" y="36">moves.pgn</text>
  {render_move_list()}

  <rect class="box" x="590" y="56" width="260" height="214" rx="10"/>
  <text class="prompt" x="610" y="84">engine</text>
  {render_current_move()}
  <text class="dim" x="610" y="142">queen sacrifice accepted</text>
  <text class="dim" x="610" y="168">king dragged to e7</text>
  <text class="dim" x="610" y="194">knight fork becomes mate</text>
  <text class="mate" x="610" y="236" opacity="0">CHECKMATE{visibility('0;0;0;0;0;0;0;0;0;0;0;0;0;1')}</text>
</svg>
'''

Path("assets/legal-trap.svg").write_text(svg, encoding="utf-8")
