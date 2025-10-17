#!/usr/bin/env python3
# Usage:
#   python make_latex_tables.py --in ./tables --out ./latex_tables --caption "My Caption" --label "tab:mylabel" --pattern "dlr_*.csv"
# The script will generate a .tex file per CSV with a booktabs table and reasonable column alignment.

import argparse
from pathlib import Path
import pandas as pd

def df_to_tabular(df: pd.DataFrame) -> str:
    # Escape LaTeX special chars in strings
    def esc(x):
        if pd.isna(x):
            return ""
        s = str(x)
        s = s.replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#")
        s = s.replace("$", "\\$").replace("{", "\\{").replace("}", "\\}").replace("^", "\\^{}").replace("~", "\\~{}")
        return s
    cols = [esc(c) for c in df.columns]
    colspec = "l" + "r"*(len(cols)-1)  # left for first col, right for others
    header = " & ".join(cols) + " \\"
    lines = ["\\begin{tabular}{" + colspec + "}", "\\toprule", header, "\\midrule"]
    for _, row in df.iterrows():
        line = " & ".join(esc(x) for x in row.values) + " \\"
        lines.append(line)
    lines += ["\\bottomrule", "\\end{tabular}"]
    return "\n".join(lines)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", type=str, default="./tables", help="Input directory with CSVs")
    ap.add_argument("--out", dest="out", type=str, default="./latex_tables", help="Output directory for .tex files")
    ap.add_argument("--caption", type=str, default="", help="Default caption if none specified per-file")
    ap.add_argument("--label", type=str, default="", help="Default label if none specified per-file")
    ap.add_argument("--pattern", type=str, default="*.csv", help="Glob pattern for CSV files to convert")
    args = ap.parse_args()

    in_dir = Path(args.inp)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(in_dir.glob(args.pattern))
    if not files:
        print(f"[WARN] No CSV files found under {in_dir} (pattern={args.pattern})")
        return

    for f in files:
        df = pd.read_csv(f)
        # For wide tables, limit decimals if numeric
        for c in df.columns:
            if pd.api.types.is_numeric_dtype(df[c]):
                df[c] = df[c].round(4)

        tabular = df_to_tabular(df)
        caption = args.caption or f"Auto-generated table from {f.name}"
        label = args.label or f"tab:{f.stem}"

        tex = "\\begin{table}[t]\n\\centering\n" + tabular + "\n" + f"\\caption{{{caption}}}\n" + f"\\label{{{label}}}\n\\end{table}\n"
        out_path = out_dir / f"{f.stem}.tex"
        out_path.write_text(tex, encoding="utf-8")
        print("[OK]", out_path)

if __name__ == "__main__":
    main()
