"""Linha de comandos: uv run python -m strata {pesquisar,modelo}."""

import argparse
import asyncio
import sys
from pathlib import Path

from strata import report, search, sheet, text
from strata.fetch import Fetcher


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="strata", description="Procura o preço mais baixo de cada produto em lojas online portuguesas."
    )
    sub = p.add_subparsers(dest="cmd", required=True, metavar="comando")
    ps = sub.add_parser("pesquisar", help="pesquisar os produtos de uma folha .xlsx (ou colados no terminal)")
    ps.add_argument("ficheiro", nargs="?", help="folha .xlsx com Produto, Unidade e Qty; sem ficheiro, lê as linhas coladas")
    ps.add_argument(
        "--record", metavar="DIR", type=Path,
        help="(desenvolvimento) grava o corpo de cada resposta das lojas em DIR, para fixtures de teste",
    )
    sub.add_parser("modelo", help="gravar modelo.xlsx na pasta atual (nunca sobrescreve)")
    return p


async def _search(items, fetch, record, out) -> None:
    if fetch is None:
        from curl_cffi.requests import AsyncSession

        async with AsyncSession(impersonate="chrome", timeout=(10, 30)) as session:
            await _search(items, Fetcher(session, record), record, out)
        return
    async for result in search.run(items, fetch):
        report.print_item(result, out)
        out.flush()


def cmd_pesquisar(args, fetch, out) -> int:
    if args.ficheiro:
        try:
            items, invalid = sheet.read_sheet(args.ficheiro)
        except sheet.SheetError as e:
            print(f"Erro na folha: {e}", file=sys.stderr)
            return 2
        empty = "A folha não tem linhas para pesquisar."
    else:  # D-10: sem ficheiro, lê as linhas coladas até uma linha vazia
        if hasattr(sys.stdin, "reconfigure"):
            sys.stdin.reconfigure(encoding="utf-8")  # pipe no Windows chega em cp1252 (Pitfall 8)
        print("Cole a lista (uma linha por produto, ex.: OSB 12mm 30 un) e termine com uma linha vazia:",
              file=sys.stderr)
        items, invalid = text.read_pasted(sys.stdin)
        if not items and not invalid:
            print("Nenhuma linha colada.", file=sys.stderr)
            return 2
        empty = "Nenhuma linha válida para pesquisar."
    report.print_invalid(invalid, out)
    if not items:
        print(empty, file=sys.stderr)
        return 2
    n = len(search.STORES)
    print(f"A pesquisar {len(items)} itens em {n} {'loja' if n == 1 else 'lojas'}…", file=sys.stderr)
    asyncio.run(_search(items, fetch, args.record, out))
    return 0


def cmd_modelo(out) -> int:
    path = Path.cwd() / "modelo.xlsx"
    try:
        sheet.write_template(path)
    except FileExistsError:
        print("modelo.xlsx já existe nesta pasta; não foi alterado.", file=out)
        return 1
    print(
        f"Modelo gravado: {path}. Preencha uma linha por produto e corra: "
        "uv run python -m strata pesquisar modelo.xlsx",
        file=out,
    )
    return 0


def main(argv=None, fetch=None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")  # "m²" e acentos certos em pipe no Windows (Pitfall 8)
    args = build_parser().parse_args(argv)
    out = sys.stdout
    if args.cmd == "modelo":
        return cmd_modelo(out)
    return cmd_pesquisar(args, fetch, out)


if __name__ == "__main__":
    raise SystemExit(main())
