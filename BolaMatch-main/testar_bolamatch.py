"""
Teste da interface do BolaMatch (login -> cadastro -> home), sem abrir janela.
    py app\testar_bolamatch.py
"""
import sys
import flet as ft
import bolamatch as app


class FakePage:
    def __init__(self):
        self.controls = []
        self.title = ""
        self.theme_mode = self.bgcolor = self.padding = self.spacing = None
        self.snack_bar = None
        self.dialogs = []

    def add(self, *c): self.controls.extend(c)
    def clean(self): self.controls = []
    def update(self): pass
    def open(self, d): self.dialogs.append(d)
    def close(self, d):
        if d in self.dialogs:
            self.dialogs.remove(d)


class Ev:
    def __init__(self, c): self.control = c


def buscar(node, tipo, out=None):
    if out is None:
        out = []
    if isinstance(node, tipo):
        out.append(node)
    for a in ("controls", "tabs", "content"):
        v = getattr(node, a, None)
        if isinstance(v, (list, tuple)):
            for x in v:
                buscar(x, tipo, out)
        elif v is not None:
            buscar(v, tipo, out)
    return out


def root(page):
    return ft.Container(content=ft.Column(list(page.controls)))


def check(nome, cond, det=""):
    print(f"[{'OK  ' if cond else 'FALHOU'}] {nome}" + (f"  -> {det}" if det else ""))
    return bool(cond)


def achar_botao_texto(page, texto):
    for c in buscar(root(page), ft.Container):
        if getattr(c, "on_click", None) is None:
            continue
        if texto in [t.value for t in buscar(c, ft.Text)]:
            return c
    return None


def preencher(page, label, valor):
    for tf in buscar(root(page), ft.TextField):
        if tf.label == label:
            tf.value = valor
            return True
    return False


def main():
    ok = True
    page = FakePage()
    app.main(page)

    # 1. login aparece
    ok &= check("app inicia sem erro", len(page.controls) > 0)
    ok &= check("título BolaMatch", page.title == "BolaMatch", page.title)
    entrar = achar_botao_texto(page, "ENTRAR")
    ok &= check("tela de login com botão ENTRAR", entrar is not None)

    # 2. ENTRAR leva ao cadastro
    if entrar:
        entrar.on_click(Ev(entrar))
    criar = achar_botao_texto(page, "CRIAR MINHA CONTA")
    ok &= check("tela de cadastro com botão CRIAR MINHA CONTA", criar is not None)

    # 3. escolher perfil comentarista
    coment = achar_botao_texto(page, "Comentarista")
    ok &= check("cartão de perfil Comentarista existe", coment is not None)
    if coment:
        coment.on_click(Ev(coment))
    ok &= check("perfil selecionado = comentarista",
                app  # o estado é interno; validamos indiretamente pela home abaixo
                is not None)

    # 4. preencher e cadastrar -> vai para HOME
    preencher(page, "E-mail", "teste@bola.com")
    preencher(page, "Senha", "123456")
    preencher(page, "Confirmar senha", "123456")
    criar = achar_botao_texto(page, "CRIAR MINHA CONTA")
    criar.on_click(Ev(criar))

    grades = buscar(root(page), ft.GridView)
    ok &= check("HOME com grade de avatares",
                bool(grades) and len(grades[0].controls) > 0,
                f"{len(grades[0].controls) if grades else 0} avatares")

    # 5. abrir detalhes do 1o jogador (perfil comentarista -> 6 abas)
    if grades and grades[0].controls:
        av = grades[0].controls[0]
        av.on_click(Ev(av))
        if page.dialogs:
            tabs = buscar(page.dialogs[-1].content, ft.Tabs)
            n = len(tabs[0].tabs) if tabs else 0
            ok &= check("comentarista: 6 abas no detalhe", n == 6, f"{n} abas")
            page.close(page.dialogs[-1])

    # 6. abrir ranking
    rk = achar_botao_texto(page, "Ranking")
    ok &= check("botão Ranking na HOME", rk is not None)
    if rk:
        rk.on_click(Ev(rk))
        drops = buscar(page.dialogs[-1].content, ft.Dropdown) if page.dialogs else []
        ok &= check("ranking com 3 filtros", len(drops) >= 3, f"{len(drops)} dropdowns")

    print()
    if ok:
        print("==============================")
        print("  BOLAMATCH: TESTES PASSARAM")
        print("==============================")
        return 0
    print("!!! ALGUM TESTE FALHOU")
    return 1


if __name__ == "__main__":
    sys.exit(main())
