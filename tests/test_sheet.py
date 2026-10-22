"""Folha Excel: modelo (D-05..D-07) e leitura da folha do utilizador (D-08, D-09, LIST-05)."""

from decimal import Decimal

import pytest
from openpyxl import Workbook, load_workbook

from strata import sheet
from strata.__main__ import main

HEADERS = ("Produto", "Família", "Tamanho", "Unidade", "Qty", "Referência", "Notas")


# --- modelo -----------------------------------------------------------------


def test_modelo_cabecalhos_e_exemplos(tmp_path):
    path = tmp_path / "modelo.xlsx"
    sheet.write_template(path)
    rows = list(load_workbook(path).active.iter_rows(min_row=1, max_row=3, values_only=True))
    assert rows[0] == HEADERS
    assert rows[1][:5] == ("OSB 12 mm", "Madeira", "2500x1250x12 mm", "un", 30)
    assert (rows[2][0], rows[2][3], rows[2][4]) == ("cimento", "saco", 10)


def test_modelo_lista_pendente_da_unidade(tmp_path):
    path = tmp_path / "modelo.xlsx"
    sheet.write_template(path)
    dvs = load_workbook(path).active.data_validations.dataValidation
    assert len(dvs) == 1
    assert dvs[0].type == "list"
    assert dvs[0].formula1 == '"un,m²,m,kg,L,saco"'
    assert str(dvs[0].sqref) == "D2:D1000"


def test_modelo_nunca_sobrescreve(tmp_path):
    path = tmp_path / "modelo.xlsx"
    sheet.write_template(path)
    before = path.read_bytes()
    with pytest.raises(FileExistsError):
        sheet.write_template(path)
    assert path.read_bytes() == before


def test_modelo_comando_duas_vezes(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert main(["modelo"]) == 0
    assert (tmp_path / "modelo.xlsx").exists()
    before = (tmp_path / "modelo.xlsx").read_bytes()
    capsys.readouterr()
    assert main(["modelo"]) == 1
    assert "modelo.xlsx já existe nesta pasta; não foi alterado." in capsys.readouterr().out
    assert (tmp_path / "modelo.xlsx").read_bytes() == before


def test_modelo_lido_pela_app(tmp_path):
    path = tmp_path / "modelo.xlsx"
    sheet.write_template(path)
    items, invalid = sheet.read_sheet(path)
    assert invalid == []
    assert [i.unit for i in items] == ["un", "saco"]
    assert items[0].family == "Madeira"
    assert items[0].qty == Decimal(30)


# --- folha do utilizador ----------------------------------------------------


def make(tmp_path, *sheets, name="lista.xlsx"):
    """Cada argumento é uma folha: lista de linhas (listas de valores)."""
    wb = Workbook()
    wb.remove(wb.active)
    for i, rows in enumerate(sheets):
        ws = wb.create_sheet(f"F{i + 1}")
        for row in rows:
            ws.append(row)
    path = tmp_path / name
    wb.save(path)
    return path


HDR = ["Produto", "Unidade", "Qty"]


def reasons(tmp_path, *rows):
    _, invalid = sheet.read_sheet(make(tmp_path, [HDR, *rows]))
    return [(i.row, i.reason) for i in invalid]


def test_cabecalho_na_linha_3(tmp_path):
    path = make(tmp_path, [["Lista de compras"], [], HDR, ["osb", "un", 30], ["cimento", "caixa", 10]])
    items, invalid = sheet.read_sheet(path)
    assert [i.row for i in items] == [4]
    assert [(i.row, i.reason) for i in invalid] == [(5, "unidade desconhecida: caixa")]


def test_colunas_por_nome_ordem_acentos_e_extra(tmp_path):
    path = make(tmp_path, [
        ["QTY", "Obra", "unidade", "PRODUTO", "familia", "Referencia", " Notas "],
        [12, "Casa A", "un", "OSB 12mm", "Madeira", "R-1", "urgente"],
    ])
    items, invalid = sheet.read_sheet(path)
    assert invalid == []
    it = items[0]
    assert (it.product, it.qty, it.unit) == ("OSB 12mm", Decimal(12), "un")
    assert (it.family, it.reference, it.notes) == ("Madeira", "R-1", "urgente")


def test_segunda_folha_quando_a_primeira_nao_tem_cabecalhos(tmp_path):
    path = make(tmp_path, [["Resumo"], ["nada", "aqui"]], [HDR, ["osb", "un", 3]])
    items, _ = sheet.read_sheet(path)
    assert [(i.product, i.row) for i in items] == [("osb", 2)]


def test_nenhuma_folha_com_cabecalhos(tmp_path):
    path = make(tmp_path, [["Produto", "Unidade"], ["osb", "un"]])
    with pytest.raises(sheet.SheetError, match="faltam qty"):
        sheet.read_sheet(path)


def test_motivos_de_linha_invalida(tmp_path):
    assert reasons(
        tmp_path,
        [None, "un", 1],
        ["a", None, 1],
        ["b", "un", None],
        ["c", "un", "abc"],
        ["d", "un", 0],
        ["e", "un", -3],
        ["f", "un", True],
        ["g", "caixa", 1],
        [None, "un", None],
    ) == [
        (2, "Produto vazio"),
        (3, "Unidade vazia"),
        (4, "Qty vazia"),
        (5, "Qty não é um número positivo: abc"),
        (6, "Qty não é um número positivo: 0"),
        (7, "Qty não é um número positivo: -3"),
        (8, "Qty não é um número positivo: True"),
        (9, "unidade desconhecida: caixa"),
        (10, "Produto vazio; Qty vazia"),
    ]


def test_qty_com_virgula_e_numero_decimal(tmp_path):
    items, _ = sheet.read_sheet(make(tmp_path, [HDR, ["a", "m2", "2,5"], ["b", "m2", 2.5]]))
    assert [i.qty for i in items] == [Decimal("2.5"), Decimal("2.5")]


def test_sinonimos_de_unidade(tmp_path):
    units = ["M2", "m²", "Unid", "uni", "LT", "l", "Sacos"]
    items, invalid = sheet.read_sheet(make(tmp_path, [HDR, *[["x", u, 1] for u in units]]))
    assert invalid == []
    assert [i.unit for i in items] == ["m²", "m²", "un", "un", "L", "L", "saco"]


def test_linhas_vazias_no_meio_ignoradas(tmp_path):
    items, invalid = sheet.read_sheet(make(tmp_path, [HDR, ["a", "un", 1], [], [None, " ", None], ["b", "un", 2]]))
    assert invalid == []
    assert [(i.product, i.row) for i in items] == [("a", 2), ("b", 5)]


def test_linhas_iguais_sao_dois_itens_pela_ordem(tmp_path):
    items, _ = sheet.read_sheet(make(tmp_path, [HDR, ["osb", "un", 1], ["cimento", "saco", 2], ["osb", "un", 1]]))
    assert [(i.product, i.row) for i in items] == [("osb", 2), ("cimento", 3), ("osb", 4)]


def test_opcionais_guardados_e_produto_tal_como_escrito(tmp_path):
    path = make(tmp_path, [list(HEADERS), ["  OSB 12 mm Hidrófugo ", "Madeira", "2500x1250", "un", 1, "REF9", "nota"]])
    it = sheet.read_sheet(path)[0][0]
    assert it.product == "OSB 12 mm Hidrófugo"
    assert (it.family, it.size, it.reference, it.notes) == ("Madeira", "2500x1250", "REF9", "nota")


def test_ficheiro_xls(tmp_path):
    path = tmp_path / "lista.xls"
    path.write_bytes(b"\xd0\xcf\x11\xe0 nao e zip")
    with pytest.raises(sheet.SheetError, match=r"não consegui abrir lista\.xls: é \.xls ou não é um \.xlsx válido"):
        sheet.read_sheet(path)


def test_ficheiro_corrompido(tmp_path):
    path = tmp_path / "lista.xlsx"
    path.write_bytes(b"PK\x03\x04 lixo")
    with pytest.raises(sheet.SheetError, match=r"não consegui abrir lista\.xlsx: é \.xls ou não é um \.xlsx válido"):
        sheet.read_sheet(path)


def test_ficheiro_inexistente(tmp_path):
    path = tmp_path / "nao_existe.xlsx"
    with pytest.raises(sheet.SheetError, match="ficheiro não encontrado: "):
        sheet.read_sheet(path)


def test_comando_com_ficheiro_ilegivel_sai_com_2_sem_traceback(tmp_path, capsys):
    path = tmp_path / "lista.xlsx"
    path.write_bytes(b"isto nao e um xlsx")
    assert main(["pesquisar", str(path)]) == 2
    captured = capsys.readouterr()
    assert "Traceback" not in captured.out + captured.err
    assert "não consegui abrir lista.xlsx" in captured.err


def test_folha_so_com_cabecalhos(tmp_path, fake, capsys):
    path = make(tmp_path, [HDR, [], []])
    assert main(["pesquisar", str(path)], fetch=fake) == 2
    assert "A folha não tem linhas para pesquisar." in capsys.readouterr().err
    assert fake.calls == []
