"""
Simple CLI entrypoint to run common evaluation tasks.
Usage:
  python evaluation/cli.py gen --pred preds.jsonl --refs refs.jsonl --out res.json
  python evaluation/cli.py retriever --file retriever.jsonl --ks 1 3 5 10 --out res.json
"""
import argparse
import sys
from evaluation import eval_generation, eval_retriever

def main(argv=None):
    parser = argparse.ArgumentParser(prog="evaluation")
    sub = parser.add_subparsers(dest="cmd")

    g = sub.add_parser("gen")
    g.add_argument("--pred")
    g.add_argument("--refs")
    g.add_argument("--both")
    g.add_argument("--out")

    r = sub.add_parser("retriever")
    r.add_argument("--file")
    r.add_argument("--ks", nargs="+", type=int, default=[1,3,5,10])
    r.add_argument("--out")

    args = parser.parse_args(argv)
    if args.cmd == "gen":
        sys.argv = ["eval_generation.py", "--pred", args.pred or "", "--refs", args.refs or "", "--both", args.both or "", "--out", args.out or ""]
        eval_generation.main()
    elif args.cmd == "retriever":
        sys.argv = ["eval_retriever.py", "--file", args.file or "", "--ks", *map(str, args.ks), "--out", args.out or ""]
        eval_retriever.main()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()