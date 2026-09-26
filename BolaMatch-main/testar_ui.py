"""
Teste da INTERFACE (sem abrir janela real).

O Flet renderiza de verdade só com um servidor/janela. Aqui usamos uma
'page' simulada (mock) que imita ft.Page (add/update/open/close) e chamamos
a função main() do app. Depois disparamos os eventos de interface
(abrir detalhes do jogador, abrir ranking, trocar filtros) e verificamos
que a UI é construída sem erros.

Como rodar (PowerShell, dentro da pasta do projeto):
    py app\testar_ui.py
"""

import sys
import flet as ft

import main as app  # importa o modulo main.py


class FakePage:
    """Imita o mínimo de ft.Page que o app usa."""
    def __init__(self):
        self.controls = []
        self.title = ""
        self.theme_mode = None
        self.padding = None
        self.bgcolor = None
        self.updates = 0
        self.dialogs_abertos = []

    def add(self, *controls):
        self.controls.extend(controls)

    def update(self):
        self.updates += 1

    def open(self, dlg):
        self.dialogs_abertos.append(dlg)

    def close(self, dlg):
        if dlg in self.dialogs_abertos:
            self.dialogs_abertos.remove(dlg)


class FakeEvent:
    def __init__(self, control):
        self.control = control


def contar_controles(controle, tipo, achados=None):
    """Percorre recursivamente a árvore de controles procurando um tipo."""
    if achados is None:
        achados = []
    if isinstance(controle, tipo):
        achados.append(controle)
    for attr in ("controls", "tabs", "content"):
        val = getattr(controle, attr, None)
        if val is None:
            continue
        if isinstance(val, (list, tuple)):
            for c in val:
                contar_controles(c, tipo, achados)
        else:
            contar_controles(val, tipo, achados)
    return achados


def check(nome, cond, detalhe=""):
    status = "OK  " if cond else "FALHOU"
    print(f"[{status}] {nome}" + (f"  -> {detalhe}" if detalhe else ""))
    return bool(cond)


def main():
    ok = True
    page = FakePage()

    print("Construindo a interface com dados reais...\n")
    app.main(page)
    ok &= check("main() executou e adicionou controles à página",
                len(page.controls) > 0, f"{len(page.controls)} no topo")
    ok &= check("página configurada", page.title == "NFL Player Stats",
                page.title)

    grades = contar_controles(ft.Container(content=ft.Column(page.controls)),
                              ft.GridView)
    grade = grades[0] if grades else None
    ok &= check("grade de avatares criada", grade is not None
                and len(grade.controls) > 0,
                f"{len(grade.controls) if grade else 0} avatares")

    primeiro_avatar = grade.controls[0]
    ok &= check("avatar tem on_click", getattr(primeiro_avatar, "on_click", None)
                is not None)
    try:
        primeiro_avatar.on_click(FakeEvent(primeiro_avatar))
        abriu = len(page.dialogs_abertos) > 0
    except Exception as e:  # noqa
        abriu = False
        print("   erro ao abrir detalhes:", e)
    ok &= check("clique no avatar abre o painel de detalhes", abriu,
                f"{len(page.dialogs_abertos)} dialog(s)")

    if page.dialogs_abertos:
        dlg = page.dialogs_abertos[-1]
        tabs = contar_controles(dlg.content, ft.Tabs)
        n_abas = len(tabs[0].tabs) if tabs else 0
        textos_abas = [t.text for t in tabs[0].tabs] if tabs else []
        ok &= check("painel tem 6 abas", n_abas == 6, str(textos_abas))
        esperadas = {"Lances", "Jogos", "Minutagem", "Desempenho",
                     "Participação", "Posição"}
        ok &= check("abas corretas presentes",
                    esperadas.issubset(set(textos_abas)),
                    str(sorted(set(textos_abas))))
        page.close(dlg)

    botoes = contar_controles(ft.Container(content=ft.Column(page.controls)),
                              ft.ElevatedButton)
    btn_ranking = next((b for b in botoes if b.text == "Ranking"), None)
    ok &= check("botão Ranking existe", btn_ranking is not None)
    if btn_ranking:
        try:
            btn_ranking.on_click(FakeEvent(btn_ranking))
            abriu_rk = any(contar_controles(d.content, ft.Dropdown)
                           for d in page.dialogs_abertos)
        except Exception as e:  # noqa
            abriu_rk = False
            print("   erro ao abrir ranking:", e)
        ok &= check("ranking abre com dropdowns de filtro", abriu_rk)

        if page.dialogs_abertos:
            dlg_rk = page.dialogs_abertos[-1]
            drops = contar_controles(dlg_rk.content, ft.Dropdown)
            ok &= check("ranking tem 3 filtros (ordenar/posição/time)",
                        len(drops) >= 3, f"{len(drops)} dropdowns")

            try:
                filtro_pos = drops[1]
                filtro_pos.value = "QB"
                filtro_pos.on_change(FakeEvent(filtro_pos))
                trocou = True
            except Exception as e:  # noqa
                trocou = False
                print("   erro ao trocar posição:", e)
            ok &= check("trocar filtro de posição funciona", trocou)

            try:
                filtro_time = drops[2]
                filtro_time.value = "KC"
                filtro_time.on_change(FakeEvent(filtro_time))
                trocou_t = True
            except Exception as e:  # noqa
                trocou_t = False
                print("   erro ao trocar time:", e)
            ok &= check("trocar filtro de time funciona", trocou_t)

    print()
    if ok:
        print("==============================")
        print("  TESTES DE INTERFACE PASSARAM")
        print("==============================")
        return 0
    print("!!! ALGUM TESTE DE INTERFACE FALHOU - veja [FALHOU] acima")
    return 1


if __name__ == "__main__":
    sys.exit(main())
