"""
BolaMatch - App esportivo (mobile + web), roda offline.

Junta:
  - a BASE APP (login / cadastro / escolha de perfil, visual azul escuro)
  - o app NFL anterior (HOME com avatares, sub-dados, minutagem e ranking)

Tudo em um arquivo só. Os dados vêm dos CSVs locais (offline) via data_service.

Rodar:
    py -m flet run app/bolamatch.py          (janela desktop)
    py -m flet run --web app/bolamatch.py     (navegador)
    py -m flet run --android app/bolamatch.py (celular, app Flet)
"""

import flet as ft

from data_service import DataService, Player


# --------------------------------------------------------------------------- #
# Compatibilidade de API do Flet (funciona no 0.24.x e no 0.28+)
# --------------------------------------------------------------------------- #
Colors = getattr(ft, "Colors", None) or ft.colors
Icons = getattr(ft, "Icons", None) or ft.icons


def run_app(target):
    """ft.run no Flet novo, ft.app no antigo."""
    if hasattr(ft, "run"):
        ft.run(target)
    else:
        ft.app(target=target)


# --------------------------------------------------------------------------- #
# Paleta (a mesma da BASE APP - BolaMatch)
# --------------------------------------------------------------------------- #
PRETO = "#02060B"
FUNDO = "#06101C"
FUNDO_2 = "#081522"
AZUL = "#1769B5"
AZUL_CLARO = "#2D8FE8"
AZUL_SUAVE = "#163B5D"
BRANCO = "#F5F8FC"
CINZA = "#8798AA"
CINZA_2 = "#5C7187"
BORDA = "#17324A"
VERDE = "#27C77A"
VERMELHO = "#D9534F"
AMBAR = "#E8A13A"

# Cores por posição (para os avatares dos jogadores)
POS_CORES = {
    "QB": "#5A6BE0", "RB": VERDE, "WR": AMBAR, "TE": "#2BBBAD",
    "T": "#8D6E63", "G": "#A1887F", "C": "#6D4C41", "DE": VERMELHO,
    "DT": "#B71C1C", "OLB": "#8E44AD", "ILB": "#7B1FA2", "MLB": "#6A1B9A",
    "CB": AZUL_CLARO, "SS": "#00ACC1", "FS": "#4FC3F7", "NT": "#EC407A",
}


def cor_posicao(pos: str) -> str:
    return POS_CORES.get((pos or "").upper(), CINZA)


# --------------------------------------------------------------------------- #
# App
# --------------------------------------------------------------------------- #
def main(page: ft.Page):
    page.title = "BolaMatch"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = PRETO
    page.padding = 0
    page.spacing = 0

    servico = DataService()

    estado = {
        "tipo": "usuario",        # perfil escolhido no cadastro
        "comentarista": False,    # True quando o perfil é comentarista
        "dlg": None,
    }

    # ===================================================================== #
    # Helpers de UI
    # ===================================================================== #
    def mensagem(texto, cor=AZUL):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(texto, color=BRANCO, weight=ft.FontWeight.BOLD),
            bgcolor=cor,
        )
        page.snack_bar.open = True
        page.update()

    def campo(label, hint, icone, senha=False, tipo_teclado=None):
        return ft.TextField(
            label=label, hint_text=hint, prefix_icon=icone,
            password=senha, can_reveal_password=senha,
            keyboard_type=tipo_teclado, height=60, filled=True,
            bgcolor=FUNDO_2, border_radius=15, border_width=1,
            border_color=BORDA, focused_border_color=AZUL_CLARO,
            cursor_color=AZUL_CLARO,
            text_style=ft.TextStyle(color=BRANCO, size=14),
            label_style=ft.TextStyle(color=CINZA),
        )

    def criar_logo(tamanho=92):
        return ft.Container(
            width=tamanho, height=tamanho, border_radius=28,
            bgcolor="#071625", border=ft.border.all(1, "#1C527F"),
            alignment=ft.alignment.center,
            content=ft.Stack([
                ft.Container(alignment=ft.alignment.center,
                             content=ft.Icon(Icons.SHIELD_OUTLINED,
                                             size=tamanho * 0.75, color=AZUL_CLARO)),
                ft.Container(alignment=ft.alignment.center,
                             content=ft.Icon(Icons.SPORTS_FOOTBALL,
                                             size=tamanho * 0.37, color=BRANCO)),
            ]),
        )

    def marca(tamanho=34):
        return ft.Row(alignment=ft.MainAxisAlignment.CENTER, spacing=0, controls=[
            ft.Text("Bola", size=tamanho, weight=ft.FontWeight.BOLD, color=BRANCO),
            ft.Text("Match", size=tamanho, weight=ft.FontWeight.BOLD, color=AZUL_CLARO),
        ])

    def moldura(conteudo, largura=440):
        """Centraliza o conteúdo com largura máxima (responsivo web+mobile)."""
        fundo = ft.Stack(expand=True, controls=[
            ft.Container(expand=True, bgcolor=PRETO),
            ft.Container(width=500, height=500, left=-250, top=-300,
                         border_radius=300, bgcolor="#071C31"),
            ft.Container(width=450, height=450, right=-250, bottom=-300,
                         border_radius=300, bgcolor="#06192A"),
            ft.Container(
                expand=True,
                content=ft.ListView(expand=True, padding=20, controls=[
                    ft.Container(
                        alignment=ft.alignment.top_center,
                        content=ft.Container(width=largura, content=conteudo),
                    )
                ]),
            ),
        ])
        page.clean()
        page.add(fundo)
        page.update()

    # ===================================================================== #
    # TELA DE LOGIN
    # ===================================================================== #
    email_login = campo("E-mail", "seu@email.com", Icons.EMAIL_OUTLINED,
                        tipo_teclado=ft.KeyboardType.EMAIL)
    senha_login = campo("Senha", "Digite sua senha", Icons.LOCK_OUTLINE, senha=True)

    def botao(texto, icone, on_click, cor=AZUL):
        return ft.Container(
            height=56, border_radius=15, bgcolor=cor, ink=True,
            on_click=on_click, alignment=ft.alignment.center,
            content=ft.Row(alignment=ft.MainAxisAlignment.CENTER, spacing=10, controls=[
                ft.Icon(icone, size=20, color=BRANCO),
                ft.Text(texto, size=15, weight=ft.FontWeight.BOLD, color=BRANCO),
            ]),
        )

    def mostrar_login():
        conteudo = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0, controls=[
                criar_logo(),
                ft.Container(height=12),
                marca(),
                ft.Container(height=3),
                ft.Text("COMPARE  •  ANALISE  •  CONFRONTE", size=9, color=CINZA),
                ft.Container(height=27),
                email_login,
                ft.Container(height=11),
                senha_login,
                ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                    ft.Checkbox(label="Lembrar de mim", active_color=AZUL,
                                check_color=BRANCO),
                    ft.TextButton("Esqueci minha senha",
                                  on_click=lambda e: mensagem(
                                      "Digite seu e-mail para recuperar a senha."),
                                  style=ft.ButtonStyle(color=AZUL_CLARO)),
                ]),
                botao("ENTRAR", Icons.LOGIN_ROUNDED, lambda e: mostrar_cadastro()),
                ft.Container(height=16),
                ft.TextButton("Ainda não tem conta? Cadastre-se",
                              on_click=lambda e: mostrar_cadastro(),
                              style=ft.ButtonStyle(color=AZUL_CLARO)),
                ft.Container(height=20),
                ft.Text("BolaMatch • Sua plataforma esportiva", size=9, color=CINZA_2),
            ])
        moldura(conteudo)

    # ===================================================================== #
    # TELA DE CADASTRO (com escolha de perfil)
    # ===================================================================== #
    email_cad = campo("E-mail", "seu@email.com", Icons.EMAIL_OUTLINED,
                      tipo_teclado=ft.KeyboardType.EMAIL)
    senha_cad = campo("Senha", "Crie uma senha segura", Icons.LOCK_OUTLINE, senha=True)
    conf_cad = campo("Confirmar senha", "Digite a senha novamente",
                     Icons.LOCK_RESET_OUTLINED, senha=True)

    def cartao_perfil(titulo, subtitulo, icone):
        return ft.Container(
            expand=True, height=92, padding=12, border_radius=15,
            bgcolor="#071522", border=ft.border.all(1, BORDA), ink=True,
            content=ft.Row(spacing=10, controls=[
                ft.Container(width=43, height=43, border_radius=12, bgcolor="#0C2942",
                             alignment=ft.alignment.center,
                             content=ft.Icon(icone, color=AZUL_CLARO, size=23)),
                ft.Column(spacing=2, expand=True, controls=[
                    ft.Text(titulo, size=13, color=BRANCO, weight=ft.FontWeight.BOLD),
                    ft.Text(subtitulo, size=9, color=CINZA),
                ]),
            ]),
        )

    perfil_usuario = cartao_perfil("Usuário", "Acompanhar e comparar times",
                                   Icons.PERSON_OUTLINE)
    perfil_coment = cartao_perfil("Comentarista", "Análises completas e técnicas",
                                  Icons.MIC_OUTLINED)

    def selecionar_perfil(tipo):
        estado["tipo"] = tipo
        perfil_usuario.border = ft.border.all(
            2 if tipo == "usuario" else 1,
            AZUL_CLARO if tipo == "usuario" else BORDA)
        perfil_coment.border = ft.border.all(
            2 if tipo == "comentarista" else 1,
            AZUL_CLARO if tipo == "comentarista" else BORDA)
        page.update()

    perfil_usuario.on_click = lambda e: selecionar_perfil("usuario")
    perfil_coment.on_click = lambda e: selecionar_perfil("comentarista")

    def cadastrar(e):
        email = (email_cad.value or "").strip()
        senha = senha_cad.value or ""
        conf = conf_cad.value or ""
        if not email:
            return mensagem("Digite seu e-mail.", VERMELHO)
        if "@" not in email or "." not in email:
            return mensagem("Digite um e-mail válido.", VERMELHO)
        if len(senha) < 6:
            return mensagem("A senha precisa ter pelo menos 6 caracteres.", VERMELHO)
        if senha != conf:
            return mensagem("As senhas não são iguais.", VERMELHO)
        # entra na HOME com o perfil escolhido
        estado["comentarista"] = (estado["tipo"] == "comentarista")
        mensagem("Bem-vindo ao BolaMatch!", VERDE)
        mostrar_home()

    def mostrar_cadastro():
        selecionar_perfil(estado["tipo"])
        conteudo = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0, controls=[
                criar_logo(82),
                ft.Container(height=10),
                marca(),
                ft.Container(height=3),
                ft.Text("CRIE SEU PERFIL NO BOLAMATCH", size=9, color=CINZA),
                ft.Container(height=24),
                email_cad,
                ft.Container(height=11),
                senha_cad,
                ft.Container(height=11),
                conf_cad,
                ft.Container(height=20),
                ft.Text("ESCOLHA O TIPO DE PERFIL", size=9, color=CINZA,
                        weight=ft.FontWeight.BOLD),
                ft.Container(height=9),
                ft.Row(spacing=10, controls=[perfil_usuario, perfil_coment]),
                ft.Container(height=18),
                botao("CRIAR MINHA CONTA", Icons.PERSON_ADD_ALT_1, cadastrar),
                ft.Container(height=12),
                ft.TextButton("Já tenho conta - Entrar",
                              on_click=lambda e: mostrar_login(),
                              style=ft.ButtonStyle(color=AZUL_CLARO)),
                ft.Container(height=20),
            ])
        moldura(conteudo)

    # ===================================================================== #
    # HOME (nosso app NFL) - avatares, detalhes, minutagem, ranking
    # ===================================================================== #
    def frase_desempenho(p: Player) -> str:
        if estado["comentarista"]:
            return (f"Pressões: {p.hits} hits, {p.hurries} hurries, {p.sacks} sacks. "
                    f"Cedidos: {p.hits_allowed} hits, {p.hurries_allowed} hurries, "
                    f"{p.sacks_allowed} sacks.")
        if p.desempenho_score >= 65:
            return "Jogou muito! Fez a diferença em campo."
        if p.desempenho_score >= 45:
            return "Desempenho equilibrado, cumpriu o papel."
        return "Dia difícil, sofreu bastante pressão."

    def fechar_dialogo():
        if estado["dlg"]:
            page.close(estado["dlg"])

    def chip(txt, cor="#0C2942"):
        return ft.Container(
            content=ft.Text(txt, size=12, color=BRANCO),
            bgcolor=cor, padding=ft.padding.symmetric(6, 10), border_radius=20)

    def avatar_widget(p: Player, tamanho=64, clicavel=True):
        circulo = ft.CircleAvatar(
            content=ft.Text(p.initials, weight=ft.FontWeight.BOLD, color=BRANCO),
            bgcolor=cor_posicao(p.position), radius=tamanho / 2)
        if not clicavel:
            return circulo
        return ft.Container(
            content=ft.Column([
                circulo,
                ft.Text(p.name.split()[-1] if p.name else "?", size=11, color=BRANCO,
                        text_align=ft.TextAlign.CENTER, max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS, width=tamanho + 12),
                ft.Text(p.position, size=10, color=CINZA),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
            padding=6, border_radius=12, ink=True,
            on_click=lambda e, pl=p: abrir_detalhes(pl),
            tooltip=f"Ver dados de {p.name}")

    def abrir_detalhes(p: Player):
        # LANCES
        lances_view = ft.ListView(spacing=8, height=300, padding=10)
        for lance in p.lances[:40]:
            legenda = (f"Q{lance['quarter']} · {lance['role']} · {lance['position']}"
                       if estado["comentarista"] else lance["role"])
            lances_view.controls.append(ft.Container(
                bgcolor="#081522", border_radius=10, padding=10,
                content=ft.Column([
                    ft.Text(legenda, size=11, color=AMBAR),
                    ft.Text(lance["desc"] or "(sem descrição)", size=13, color=BRANCO),
                ], spacing=2)))
        if not lances_view.controls:
            lances_view.controls.append(ft.Text("Sem lances.", color=CINZA))

        # JOGOS
        jogos_view = ft.ListView(spacing=8, height=300, padding=10)
        for jogo in p.jogos[:15]:
            sub = (f"Semana {jogo['week']} · {jogo['date']} · {jogo['n_lances']} lances"
                   if estado["comentarista"]
                   else f"Semana {jogo['week']} · {jogo['date']}")
            jogos_view.controls.append(ft.Container(
                bgcolor="#081522", border_radius=10, padding=10,
                content=ft.Row([
                    ft.Icon(Icons.SPORTS_FOOTBALL, color=AMBAR),
                    ft.Column([
                        ft.Text(f"{jogo['visitor']} @ {jogo['home']}", size=14,
                                weight=ft.FontWeight.BOLD, color=BRANCO),
                        ft.Text(sub, size=11, color=CINZA),
                    ], spacing=1, expand=True),
                ])))
        if not jogos_view.controls:
            jogos_view.controls.append(ft.Text("Sem jogos.", color=CINZA))

        # MINUTAGEM
        min_rows = ft.ListView(spacing=6, height=250, padding=8)
        for m in p.minutagem_por_jogo():
            min_rows.controls.append(ft.Container(
                bgcolor="#081522", border_radius=10, padding=10,
                content=ft.Row([
                    ft.Container(width=48, content=ft.Text(f"Sem {m['week']}", size=11,
                                                           color=CINZA)),
                    ft.Column([
                        ft.Text(m["matchup"], size=13, color=BRANCO,
                                weight=ft.FontWeight.BOLD),
                        ft.Text(f"{m['n_lances']} lances", size=10, color=CINZA),
                    ], spacing=1, expand=True),
                    ft.Container(bgcolor=AZUL, border_radius=8,
                                 padding=ft.padding.symmetric(6, 12),
                                 content=ft.Text(f"⏱ {m['mmss']}", size=14,
                                                 color=BRANCO,
                                                 weight=ft.FontWeight.BOLD)),
                ])))
        minutagem_view = ft.Container(padding=14, content=ft.Column([
            ft.Row([chip(f"⏱ {p.minutos_totais} min"),
                    chip(f"📈 {p.minutos_por_jogo} min/jogo"),
                    chip(f"🏈 {p.total_lances} lances")],
                   wrap=True, spacing=6, run_spacing=6),
            ft.Text("Tempo em campo por jogo (bola em jogo)", size=11, color=CINZA),
            min_rows,
        ], spacing=8, scroll=ft.ScrollMode.AUTO))

        # DESEMPENHO
        nota = p.desempenho_score
        cor_nota = VERDE if nota >= 65 else (AMBAR if nota >= 45 else VERMELHO)
        chips_desemp = [chip(f"🏈 {p.total_lances} lances")]
        if estado["comentarista"]:
            chips_desemp += [chip(f"💥 {p.sacks} sacks", "#5A1A1A"),
                             chip(f"⚡ {p.hurries} hurries", "#5A3A10")]
        desempenho_view = ft.Container(padding=16, content=ft.Column([
            ft.Text("Nota geral", size=13, color=CINZA),
            ft.Row([ft.Text(str(nota), size=44, weight=ft.FontWeight.BOLD,
                            color=cor_nota),
                    ft.Text("/100", size=16, color=CINZA)],
                   vertical_alignment=ft.CrossAxisAlignment.END),
            ft.ProgressBar(value=nota / 100, color=cor_nota, bgcolor="#0C2942",
                           height=8),
            ft.Container(height=8),
            ft.Text(frase_desempenho(p), size=13, color=BRANCO),
            ft.Container(height=8),
            ft.Row(chips_desemp, wrap=True, spacing=6, run_spacing=6),
        ], spacing=6))

        # PARTICIPAÇÃO (só comentarista)
        part = p.participacao()
        barras = []
        for item in part["linha"]:
            cb = VERMELHO if item["queda"] else VERDE
            barras.append(ft.Row([
                ft.Container(width=60, content=ft.Text(f"Sem {item['week']}", size=11,
                                                       color=CINZA)),
                ft.Container(expand=True, content=ft.ProgressBar(
                    value=item["pct_pico"] / 100, color=cb, bgcolor="#0C2942",
                    height=14)),
                ft.Container(width=70, content=ft.Text(f"{item['n_lances']} lances",
                                                       size=11, color=BRANCO,
                                                       text_align=ft.TextAlign.RIGHT)),
            ], spacing=6))
        participacao_view = ft.Container(padding=14, content=ft.Column([
            ft.Row([chip(f"🎮 {part['jogos_disputados']} jogos"),
                    chip(f"📊 média {part['media']}"),
                    chip(f"⬆️ pico {part['pico']}")],
                   wrap=True, spacing=6, run_spacing=6),
            ft.Text(part["resumo"], size=12, color=BRANCO),
            ft.Column(barras, spacing=6, scroll=ft.ScrollMode.AUTO, height=180),
        ], spacing=8, scroll=ft.ScrollMode.AUTO))

        # POSIÇÃO
        aligns = sorted(p.aligned_positions.items(), key=lambda kv: kv[1], reverse=True)
        posicao_view = ft.Container(padding=16, content=ft.Column([
            ft.Text("Posição oficial", size=13, color=CINZA),
            ft.Text(p.position or "—", size=28, weight=ft.FontWeight.BOLD,
                    color=cor_posicao(p.position)),
            ft.Container(height=8),
            ft.Text("Onde se alinhou", size=13, color=CINZA),
            ft.Row([chip(f"{pos} ({n})", "#0C2942") for pos, n in aligns[:12]]
                   or [ft.Text("—", color=CINZA)], wrap=True, spacing=6, run_spacing=6),
            ft.Container(height=10),
            ft.Text(f"Altura {p.height} · Peso {p.weight} lb · {p.college}",
                    size=12, color=CINZA),
        ], spacing=6))

        abas_list = [
            ft.Tab(text="Lances", icon=Icons.PLAY_CIRCLE, content=lances_view),
            ft.Tab(text="Jogos", icon=Icons.CALENDAR_MONTH, content=jogos_view),
            ft.Tab(text="Minutagem", icon=Icons.TIMER, content=minutagem_view),
            ft.Tab(text="Desempenho", icon=Icons.INSIGHTS, content=desempenho_view),
        ]
        if estado["comentarista"]:
            abas_list.append(ft.Tab(text="Participação", icon=Icons.MONITOR_HEART,
                                    content=participacao_view))
        abas_list.append(ft.Tab(text="Posição", icon=Icons.PIN_DROP,
                                content=posicao_view))

        cabecalho = ft.Row([
            avatar_widget(p, 52, clicavel=False),
            ft.Column([
                ft.Text(p.name, size=18, weight=ft.FontWeight.BOLD, color=BRANCO),
                ft.Text(f"{p.position} · {p.team}" if p.team else p.position,
                        size=13, color=cor_posicao(p.position)),
            ], spacing=1, expand=True),
            ft.IconButton(Icons.CLOSE, icon_color=BRANCO,
                          on_click=lambda e: fechar_dialogo()),
        ])

        dlg = ft.AlertDialog(
            bgcolor=FUNDO,
            content=ft.Container(width=380, height=470, content=ft.Column([
                cabecalho, ft.Divider(color=BORDA),
                ft.Tabs(selected_index=0, scrollable=True, tabs=abas_list, expand=True),
            ], spacing=6)))
        page.open(dlg)
        estado["dlg"] = dlg

    # ---- Ranking ----
    def abrir_ranking():
        criterio = {"v": "minutagem"}
        posicao = {"v": None}
        time = {"v": None}
        lista = ft.ListView(spacing=6, expand=True, padding=6)

        def montar():
            lista.controls.clear()
            dados = servico.ranking(criterio["v"], limite=50,
                                    posicao=posicao["v"], time=time["v"])
            if not dados:
                lista.controls.append(ft.Text("Nenhum jogador nesse filtro.",
                                              color=CINZA))
            for pos, p, val in dados:
                medalha = ("🥇" if pos == 1 else "🥈" if pos == 2 else
                           "🥉" if pos == 3 else f"{pos}º")
                lista.controls.append(ft.Container(
                    bgcolor="#081522", border_radius=10,
                    padding=ft.padding.symmetric(8, 10), ink=True,
                    on_click=lambda e, pl=p: (fechar_dialogo(), abrir_detalhes(pl)),
                    content=ft.Row([
                        ft.Container(width=34, content=ft.Text(medalha, size=15,
                                                               color=AMBAR,
                                                               weight=ft.FontWeight.BOLD)),
                        ft.CircleAvatar(content=ft.Text(p.initials, size=12,
                                                        color=BRANCO),
                                        bgcolor=cor_posicao(p.position), radius=16),
                        ft.Column([
                            ft.Text(p.name, size=13, color=BRANCO,
                                    weight=ft.FontWeight.BOLD),
                            ft.Text(f"{p.position} · {p.team}" if p.team
                                    else p.position, size=10,
                                    color=cor_posicao(p.position)),
                        ], spacing=1, expand=True),
                        ft.Container(bgcolor=AZUL, border_radius=8,
                                     padding=ft.padding.symmetric(4, 10),
                                     content=ft.Text(f"{val:g}", size=14, color=BRANCO,
                                                     weight=ft.FontWeight.BOLD)),
                    ], spacing=8)))
            titulo.value = (f"{servico.rotulo_criterio(criterio['v'])} · "
                            f"{posicao['v'] or 'todas'} · {time['v'] or 'todos'}")
            page.update()

        def set_criterio(e):
            criterio["v"] = e.control.value
            montar()

        def set_pos(e):
            posicao["v"] = None if e.control.value == "__T__" else e.control.value
            montar()

        def set_time(e):
            time["v"] = None if e.control.value == "__T__" else e.control.value
            montar()

        d_criterio = ft.Dropdown(
            value="minutagem", on_change=set_criterio, width=190,
            options=[ft.dropdown.Option(k, v[0])
                     for k, v in servico.CRITERIOS_RANKING.items()],
            border_color=BORDA, color=BRANCO)
        d_pos = ft.Dropdown(
            value="__T__", on_change=set_pos, width=120,
            options=[ft.dropdown.Option("__T__", "Todas")]
                    + [ft.dropdown.Option(x, x) for x in servico.posicoes_disponiveis()],
            border_color=BORDA, color=BRANCO)
        d_time = ft.Dropdown(
            value="__T__", on_change=set_time, width=120,
            options=[ft.dropdown.Option("__T__", "Todos")]
                    + [ft.dropdown.Option(x, x) for x in servico.times_disponiveis()],
            border_color=BORDA, color=BRANCO)

        titulo = ft.Text("Ranking", size=16, weight=ft.FontWeight.BOLD,
                         color=BRANCO, expand=True)

        dlg = ft.AlertDialog(bgcolor=FUNDO, content=ft.Container(
            width=400, height=540, content=ft.Column([
                ft.Row([ft.Icon(Icons.LEADERBOARD, color=AMBAR), titulo,
                        ft.IconButton(Icons.CLOSE, icon_color=BRANCO,
                                      on_click=lambda e: fechar_dialogo())]),
                ft.Row([
                    ft.Column([ft.Text("Ordenar por:", size=11, color=CINZA),
                               d_criterio], spacing=2),
                    ft.Column([ft.Text("Posição:", size=11, color=CINZA), d_pos],
                              spacing=2),
                    ft.Column([ft.Text("Time:", size=11, color=CINZA), d_time],
                              spacing=2),
                ], spacing=10, wrap=True, run_spacing=8),
                ft.Divider(color=BORDA),
                lista,
            ], spacing=8)))
        page.open(dlg)
        estado["dlg"] = dlg
        montar()

    # ---- montagem da HOME ----
    grade = ft.GridView(expand=True, max_extent=110, child_aspect_ratio=0.8,
                        spacing=8, run_spacing=8, padding=12)

    def render(jogadores):
        grade.controls = [avatar_widget(p) for p in jogadores]
        page.update()

    def on_busca(e):
        render(servico.buscar(e.control.value))

    def mostrar_home():
        busca = ft.TextField(
            hint_text="Buscar jogador ou posição (ex: Brady, QB)...",
            prefix_icon=Icons.SEARCH, on_change=on_busca, height=52,
            border_color=BORDA, color=BRANCO, bgcolor=FUNDO_2, border_radius=12,
            text_style=ft.TextStyle(color=BRANCO),
            hint_style=ft.TextStyle(color=CINZA_2))

        perfil_txt = "Comentarista" if estado["comentarista"] else "Torcedor"
        topo = ft.Container(
            bgcolor=FUNDO, padding=ft.padding.only(16, 16, 16, 12),
            content=ft.Column([
                ft.Row([
                    criar_logo(40),
                    marca(20),
                    ft.Container(expand=True),
                    ft.Container(bgcolor="#0C2942", border_radius=20,
                                 padding=ft.padding.symmetric(4, 10),
                                 content=ft.Row([
                                     ft.Icon(Icons.PERSON, size=14, color=AZUL_CLARO),
                                     ft.Text(perfil_txt, size=12, color=AZUL_CLARO,
                                             weight=ft.FontWeight.BOLD)], spacing=4)),
                    ft.IconButton(Icons.LOGOUT, icon_color=CINZA, tooltip="Sair",
                                  on_click=lambda e: mostrar_login()),
                ]),
                ft.Row([
                    ft.Text("Toque no avatar para ver os dados", size=12,
                            color=CINZA, expand=True),
                    ft.Container(bgcolor=AZUL, border_radius=12, ink=True,
                                 padding=ft.padding.symmetric(8, 14),
                                 on_click=lambda e: abrir_ranking(),
                                 content=ft.Row([
                                     ft.Icon(Icons.LEADERBOARD, size=16, color=BRANCO),
                                     ft.Text("Ranking", size=13, color=BRANCO,
                                             weight=ft.FontWeight.BOLD)], spacing=6)),
                ]),
                busca,
            ], spacing=10))

        carregando = ft.Column([
            ft.ProgressRing(color=AZUL_CLARO),
            ft.Text("Carregando dados dos jogos...", color=CINZA),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
           alignment=ft.MainAxisAlignment.CENTER, expand=True)

        page.clean()
        page.add(ft.Container(expand=True, bgcolor=PRETO,
                              content=ft.Column([topo, carregando], spacing=0,
                                                expand=True)))
        page.update()

        jogadores = servico.jogadores_com_dados(limite=60)
        page.clean()
        page.add(ft.Container(expand=True, bgcolor=PRETO,
                              content=ft.Column([topo, grade], spacing=0, expand=True)))
        render(jogadores)

    # começa pela tela de login
    mostrar_login()


if __name__ == "__main__":
    run_app(main)
