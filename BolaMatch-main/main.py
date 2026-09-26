"""
App mobile (Flet) - NFL Big Data Bowl.

Tela inicial: grade de avatares de jogadores.
Ao clicar no AVATAR abre um painel com os sub-dados:
    Lances | Últimos jogos | Desempenho | Posição

Modo de visão no topo:
    - Torcedor     -> linguagem simples e direta
    - Comentarista -> linguagem técnica com mais números

Rodar:  flet run app/main.py       (desktop)
        flet run --android app/main.py   (celular via app Flet)
"""

import flet as ft

from data_service import DataService, Player

# Compatibilidade de API do Flet:
# - Flet >= 0.25 expõe ft.Colors / ft.Icons (maiúsculo)
# - Flet 0.24.x (fixado no requirements) expõe ft.colors / ft.icons
# Usamos aliases para funcionar em ambas as versões.
Colors = getattr(ft, "Colors", None) or ft.colors
Icons = getattr(ft, "Icons", None) or ft.icons


# Paleta de cores por posição (só para deixar os avatares dinâmicos)
POS_CORES = {
    "QB": Colors.INDIGO, "RB": Colors.GREEN, "WR": Colors.ORANGE,
    "TE": Colors.TEAL, "T": Colors.BROWN, "G": Colors.BROWN_400,
    "C": Colors.BROWN_700, "DE": Colors.RED, "DT": Colors.RED_900,
    "OLB": Colors.PURPLE, "ILB": Colors.PURPLE_700, "MLB": Colors.DEEP_PURPLE,
    "CB": Colors.BLUE, "SS": Colors.CYAN, "FS": Colors.LIGHT_BLUE,
    "NT": Colors.PINK,
}


def cor_posicao(pos: str) -> str:
    return POS_CORES.get(pos, Colors.BLUE_GREY)


def main(page: ft.Page):
    page.title = "NFL Player Stats"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.bgcolor = Colors.BLACK

    servico = DataService()

    # Estado da visão: True = Comentarista, False = Torcedor
    estado = {"comentarista": False}

    # ------------------------------------------------------------------ #
    # Textos que mudam conforme o modo (Torcedor x Comentarista)
    # ------------------------------------------------------------------ #
    def frase_desempenho(p: Player) -> str:
        if estado["comentarista"]:
            return (f"Pressões: {p.hits} hits, {p.hurries} hurries, {p.sacks} sacks. "
                    f"Cedidos: {p.hits_allowed} hits, {p.hurries_allowed} hurries, "
                    f"{p.sacks_allowed} sacks, {p.beaten} vezes superado.")
        # Torcedor
        if p.desempenho_score >= 65:
            return "Jogou muito! Fez a diferença em campo."
        if p.desempenho_score >= 45:
            return "Desempenho equilibrado, cumpriu o papel."
        return "Dia difícil, sofreu bastante pressão."

    # ------------------------------------------------------------------ #
    # Painel de sub-dados (abre ao clicar no avatar)
    # ------------------------------------------------------------------ #
    def abrir_detalhes(p: Player):
        def chip(txt, cor=Colors.WHITE10):
            return ft.Container(
                content=ft.Text(txt, size=12, color=Colors.WHITE),
                bgcolor=cor, padding=ft.padding.symmetric(6, 10),
                border_radius=20,
            )

        # --- aba LANCES ---
        lances_view = ft.ListView(spacing=8, height=320, padding=10)
        for lance in p.lances[:40]:
            desc = lance["desc"] or "(sem descrição)"
            legenda = (f"Q{lance['quarter']} · {lance['role']} · {lance['position']}"
                       if estado["comentarista"]
                       else f"{lance['role']}")
            lances_view.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(legenda, size=11, color=Colors.AMBER),
                        ft.Text(desc, size=13, color=Colors.WHITE),
                    ], spacing=2),
                    bgcolor=Colors.WHITE10, border_radius=10, padding=10,
                )
            )
        if not lances_view.controls:
            lances_view.controls.append(ft.Text("Sem lances registrados."))

        # --- aba ÚLTIMOS JOGOS ---
        jogos_view = ft.ListView(spacing=8, height=320, padding=10)
        for jogo in p.jogos[:15]:
            titulo = f"{jogo['visitor']} @ {jogo['home']}"
            sub = (f"Semana {jogo['week']} · {jogo['date']} · {jogo['n_lances']} lances"
                   if estado["comentarista"]
                   else f"Semana {jogo['week']} · {jogo['date']}")
            jogos_view.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(Icons.SPORTS_FOOTBALL, color=Colors.AMBER),
                        ft.Column([
                            ft.Text(titulo, size=14, weight=ft.FontWeight.BOLD,
                                    color=Colors.WHITE),
                            ft.Text(sub, size=11, color=Colors.WHITE70),
                        ], spacing=1, expand=True),
                    ]),
                    bgcolor=Colors.WHITE10, border_radius=10, padding=10,
                )
            )
        if not jogos_view.controls:
            jogos_view.controls.append(ft.Text("Sem jogos registrados."))

        # --- aba DESEMPENHO ---
        nota = p.desempenho_score
        cor_nota = (Colors.GREEN if nota >= 65 else
                    Colors.AMBER if nota >= 45 else Colors.RED)
        desempenho_view = ft.Container(
            padding=16,
            content=ft.Column([
                ft.Text("Nota geral", size=13, color=Colors.WHITE70),
                ft.Row([
                    ft.Text(str(nota), size=44, weight=ft.FontWeight.BOLD, color=cor_nota),
                    ft.Text("/100", size=16, color=Colors.WHITE54),
                ], vertical_alignment=ft.CrossAxisAlignment.END),
                ft.ProgressBar(value=nota / 100, color=cor_nota,
                               bgcolor=Colors.WHITE10, height=8),
                ft.Container(height=8),
                ft.Text(frase_desempenho(p), size=13, color=Colors.WHITE),
                ft.Container(height=8),
                ft.Row([
                    chip(f"🏈 {p.total_lances} lances", Colors.INDIGO_700),
                    chip(f"💥 {p.sacks} sacks", Colors.RED_700),
                    chip(f"⚡ {p.hurries} hurries", Colors.ORANGE_800),
                ], wrap=True, spacing=6, run_spacing=6),
            ], spacing=6),
        )

        # --- aba POSIÇÃO ---
        aligns = sorted(p.aligned_positions.items(), key=lambda kv: kv[1], reverse=True)
        pos_chips = [chip(f"{pos} ({n})", cor_posicao(pos)) for pos, n in aligns[:12]]
        posicao_view = ft.Container(
            padding=16,
            content=ft.Column([
                ft.Text("Posição oficial", size=13, color=Colors.WHITE70),
                ft.Text(p.position or "—", size=28, weight=ft.FontWeight.BOLD,
                        color=cor_posicao(p.position)),
                ft.Container(height=8),
                ft.Text("Onde se alinhou em campo", size=13, color=Colors.WHITE70),
                ft.Row(pos_chips or [ft.Text("—")], wrap=True, spacing=6, run_spacing=6),
                ft.Container(height=10),
                ft.Text(f"Altura {p.height} · Peso {p.weight} lb · {p.college}",
                        size=12, color=Colors.WHITE54),
            ], spacing=6),
        )

        # --- aba PARTICIPAÇÃO (aproximação de rodízio / ausência) ---
        part = p.participacao()
        barras = []
        for item in part["linha"]:
            cor_barra = Colors.RED if item["queda"] else Colors.GREEN
            barras.append(
                ft.Row([
                    ft.Container(width=64, content=ft.Text(
                        f"Sem {item['week']}", size=11, color=Colors.WHITE70)),
                    ft.Container(
                        expand=True,
                        content=ft.ProgressBar(
                            value=item["pct_pico"] / 100, color=cor_barra,
                            bgcolor=Colors.WHITE10, height=14),
                    ),
                    ft.Container(width=70, content=ft.Text(
                        f"{item['n_lances']} lances", size=11,
                        color=Colors.WHITE, text_align=ft.TextAlign.RIGHT)),
                ], spacing=6)
            )

        # avisos de queda (linguagem depende do modo)
        avisos = []
        if part["alertas"]:
            for a in part["alertas"]:
                texto = a if estado["comentarista"] else \
                    a.split(" - ")[0] + " - participação baixa"
                avisos.append(
                    ft.Row([
                        ft.Icon(Icons.WARNING_AMBER, color=Colors.AMBER, size=16),
                        ft.Text(texto, size=12, color=Colors.AMBER, expand=True),
                    ])
                )
        else:
            avisos.append(
                ft.Row([
                    ft.Icon(Icons.CHECK_CIRCLE, color=Colors.GREEN, size=16),
                    ft.Text("Sem quedas relevantes de participação.",
                            size=12, color=Colors.GREEN, expand=True),
                ])
            )

        participacao_view = ft.Container(
            padding=14,
            content=ft.Column([
                ft.Row([
                    chip(f"🎮 {part['jogos_disputados']} jogos", Colors.INDIGO_700),
                    chip(f"📊 média {part['media']}/jogo", Colors.BLUE_700),
                    chip(f"⬆️ pico {part['pico']}", Colors.GREEN_700),
                ], wrap=True, spacing=6, run_spacing=6),
                ft.Text(part["resumo"], size=12, color=Colors.WHITE),
                ft.Divider(color=Colors.WHITE12),
                ft.Text("Lances por jogo (barra = % do seu pico)",
                        size=11, color=Colors.WHITE54),
                ft.Column(barras, spacing=6, scroll=ft.ScrollMode.AUTO, height=150),
                ft.Divider(color=Colors.WHITE12),
                ft.Column(avisos, spacing=4),
                ft.Text("Estimativa a partir do volume de lances. "
                        "Os arquivos não trazem lesão/substituição oficiais.",
                        size=10, color=Colors.WHITE38, italic=True),
            ], spacing=8, scroll=ft.ScrollMode.AUTO),
        )

        # --- aba MINUTAGEM (tempo em campo estimado por jogo) ---
        minutagem = p.minutagem_por_jogo()
        min_rows = ft.ListView(spacing=6, height=230, padding=8)
        for m in minutagem:
            min_rows.controls.append(
                ft.Container(
                    bgcolor=Colors.WHITE10, border_radius=10, padding=10,
                    content=ft.Row([
                        ft.Container(width=48, content=ft.Text(
                            f"Sem {m['week']}", size=11, color=Colors.WHITE70)),
                        ft.Column([
                            ft.Text(m["matchup"], size=13, color=Colors.WHITE,
                                    weight=ft.FontWeight.BOLD),
                            ft.Text(f"{m['n_lances']} lances", size=10,
                                    color=Colors.WHITE54),
                        ], spacing=1, expand=True),
                        ft.Container(
                            bgcolor=Colors.INDIGO_700, border_radius=8,
                            padding=ft.padding.symmetric(6, 12),
                            content=ft.Text(f"⏱ {m['mmss']}", size=14,
                                            color=Colors.WHITE,
                                            weight=ft.FontWeight.BOLD)),
                    ]),
                )
            )
        if not min_rows.controls:
            min_rows.controls.append(ft.Text("Sem jogos registrados."))

        minutagem_view = ft.Container(
            padding=14,
            content=ft.Column([
                ft.Row([
                    chip(f"⏱ {p.minutos_totais} min totais", Colors.INDIGO_700),
                    chip(f"📈 {p.minutos_por_jogo} min/jogo", Colors.BLUE_700),
                    chip(f"🏈 {p.total_lances} lances", Colors.GREEN_700),
                ], wrap=True, spacing=6, run_spacing=6),
                ft.Text("Tempo em campo por jogo (bola em jogo, snap→fim)",
                        size=11, color=Colors.WHITE54),
                min_rows,
                ft.Text("Estimativa: nº de lances × 4,2 s/jogada (média medida "
                        "no tracking). Não é o tempo total de relógio.",
                        size=10, color=Colors.WHITE38, italic=True),
            ], spacing=8, scroll=ft.ScrollMode.AUTO),
        )

        abas = ft.Tabs(
            selected_index=0,
            animation_duration=250,
            scrollable=True,
            tabs=[
                ft.Tab(text="Lances", icon=Icons.PLAY_CIRCLE, content=lances_view),
                ft.Tab(text="Jogos", icon=Icons.CALENDAR_MONTH, content=jogos_view),
                ft.Tab(text="Minutagem", icon=Icons.TIMER, content=minutagem_view),
                ft.Tab(text="Desempenho", icon=Icons.INSIGHTS, content=desempenho_view),
                ft.Tab(text="Participação", icon=Icons.MONITOR_HEART,
                       content=participacao_view),
                ft.Tab(text="Posição", icon=Icons.PIN_DROP, content=posicao_view),
            ],
            expand=True,
        )

        cabecalho = ft.Row([
            avatar_widget(p, tamanho=52, clicavel=False),
            ft.Column([
                ft.Text(p.name, size=18, weight=ft.FontWeight.BOLD, color=Colors.WHITE),
                ft.Text(f"{p.position} · {p.team}" if p.team else p.position,
                        size=13, color=cor_posicao(p.position)),
            ], spacing=1, expand=True),
            ft.IconButton(Icons.CLOSE, icon_color=Colors.WHITE,
                          on_click=lambda e: fechar_dialogo()),
        ])

        dlg = ft.AlertDialog(
            content=ft.Container(
                width=380, height=470,
                content=ft.Column([cabecalho, ft.Divider(color=Colors.WHITE24), abas],
                                  spacing=6),
            ),
            bgcolor=Colors.GREY_900,
        )
        page.open(dlg)
        estado["dlg"] = dlg

    def fechar_dialogo():
        dlg = estado.get("dlg")
        if dlg:
            page.close(dlg)

    # ------------------------------------------------------------------ #
    # Ranking de jogadores
    # ------------------------------------------------------------------ #
    def abrir_ranking():
        criterio_atual = {"valor": "minutagem"}
        posicao_atual = {"valor": None}  # None = todas
        time_atual = {"valor": None}     # None = todos
        lista = ft.ListView(spacing=6, expand=True, padding=6)

        def montar_lista():
            lista.controls.clear()
            dados = servico.ranking(criterio_atual["valor"], limite=50,
                                    posicao=posicao_atual["valor"],
                                    time=time_atual["valor"])
            rotulo = servico.rotulo_criterio(criterio_atual["valor"])
            if not dados:
                lista.controls.append(
                    ft.Container(padding=20, content=ft.Text(
                        "Nenhum jogador nessa posição.", size=13,
                        color=Colors.WHITE54)))
            for pos, p, valor in dados:
                # medalhas para o pódio
                if pos == 1:
                    medalha, cor_pos = "🥇", Colors.AMBER
                elif pos == 2:
                    medalha, cor_pos = "🥈", Colors.BLUE_GREY_200
                elif pos == 3:
                    medalha, cor_pos = "🥉", Colors.BROWN_300
                else:
                    medalha, cor_pos = f"{pos}º", Colors.WHITE54

                valor_txt = f"{valor:g}"
                lista.controls.append(
                    ft.Container(
                        bgcolor=Colors.WHITE10, border_radius=10,
                        padding=ft.padding.symmetric(8, 10),
                        on_click=lambda e, pl=p: (fechar_dialogo(), abrir_detalhes(pl)),
                        ink=True,
                        content=ft.Row([
                            ft.Container(width=34, content=ft.Text(
                                medalha, size=15, color=cor_pos,
                                weight=ft.FontWeight.BOLD)),
                            ft.CircleAvatar(
                                content=ft.Text(p.initials, size=12,
                                                color=Colors.WHITE),
                                bgcolor=cor_posicao(p.position), radius=16),
                            ft.Column([
                                ft.Text(p.name, size=13, color=Colors.WHITE,
                                        weight=ft.FontWeight.BOLD),
                                ft.Text(f"{p.position} · {p.team}" if p.team
                                        else p.position, size=10,
                                        color=cor_posicao(p.position)),
                            ], spacing=1, expand=True),
                            ft.Container(
                                bgcolor=Colors.INDIGO_700, border_radius=8,
                                padding=ft.padding.symmetric(4, 10),
                                content=ft.Text(valor_txt, size=14,
                                                color=Colors.WHITE,
                                                weight=ft.FontWeight.BOLD)),
                        ], spacing=8),
                    )
                )
            pos_txt = posicao_atual["valor"] or "todas as pos."
            time_txt = time_atual["valor"] or "todos os times"
            titulo_ranking.value = f"{rotulo} · {pos_txt} · {time_txt}"
            page.update()

        def trocar_criterio(e):
            criterio_atual["valor"] = e.control.value
            montar_lista()

        def trocar_posicao(e):
            v = e.control.value
            posicao_atual["valor"] = None if v == "__TODAS__" else v
            montar_lista()

        def trocar_time(e):
            v = e.control.value
            time_atual["valor"] = None if v == "__TODOS__" else v
            montar_lista()

        seletor = ft.Dropdown(
            value="minutagem",
            on_change=trocar_criterio,
            width=200,
            options=[ft.dropdown.Option(k, v[0])
                     for k, v in servico.CRITERIOS_RANKING.items()],
            border_color=Colors.WHITE24, color=Colors.WHITE,
        )

        seletor_pos = ft.Dropdown(
            value="__TODAS__",
            on_change=trocar_posicao,
            width=130,
            options=[ft.dropdown.Option("__TODAS__", "Todas")]
                    + [ft.dropdown.Option(pos, pos)
                       for pos in servico.posicoes_disponiveis()],
            border_color=Colors.WHITE24, color=Colors.WHITE,
        )

        seletor_time = ft.Dropdown(
            value="__TODOS__",
            on_change=trocar_time,
            width=130,
            options=[ft.dropdown.Option("__TODOS__", "Todos")]
                    + [ft.dropdown.Option(t, t)
                       for t in servico.times_disponiveis()],
            border_color=Colors.WHITE24, color=Colors.WHITE,
        )

        titulo_ranking = ft.Text("Ranking", size=18, weight=ft.FontWeight.BOLD,
                                 color=Colors.WHITE, expand=True)

        dlg = ft.AlertDialog(
            content=ft.Container(
                width=390, height=520,
                content=ft.Column([
                    ft.Row([
                        ft.Icon(Icons.LEADERBOARD, color=Colors.AMBER),
                        titulo_ranking,
                        ft.IconButton(Icons.CLOSE, icon_color=Colors.WHITE,
                                      on_click=lambda e: fechar_dialogo()),
                    ]),
                    ft.Row([
                        ft.Column([ft.Text("Ordenar por:", size=11,
                                           color=Colors.WHITE54), seletor],
                                  spacing=2),
                        ft.Column([ft.Text("Posição:", size=11,
                                           color=Colors.WHITE54), seletor_pos],
                                  spacing=2),
                        ft.Column([ft.Text("Time:", size=11,
                                           color=Colors.WHITE54), seletor_time],
                                  spacing=2),
                    ], spacing=10, wrap=True, run_spacing=8),
                    ft.Text("Toque em um jogador para ver os detalhes.",
                            size=10, color=Colors.WHITE38),
                    ft.Divider(color=Colors.WHITE24),
                    lista,
                ], spacing=8),
            ),
            bgcolor=Colors.GREY_900,
        )
        page.open(dlg)
        estado["dlg"] = dlg
        montar_lista()

    # ------------------------------------------------------------------ #
    # Avatar clicável
    # ------------------------------------------------------------------ #
    def avatar_widget(p: Player, tamanho: int = 64, clicavel: bool = True) -> ft.Control:
        circulo = ft.CircleAvatar(
            content=ft.Text(p.initials, weight=ft.FontWeight.BOLD, color=Colors.WHITE),
            bgcolor=cor_posicao(p.position),
            radius=tamanho / 2,
        )
        if not clicavel:
            return circulo
        return ft.Container(
            content=ft.Column([
                circulo,
                ft.Text(p.name.split()[-1] if p.name else "?", size=11,
                        color=Colors.WHITE, text_align=ft.TextAlign.CENTER,
                        max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, width=tamanho + 12),
                ft.Text(p.position, size=10, color=Colors.WHITE54),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
            padding=6, border_radius=12, ink=True,
            on_click=lambda e, pl=p: abrir_detalhes(pl),
            tooltip=f"Ver dados de {p.name}",
        )

    # ------------------------------------------------------------------ #
    # Grade de avatares + busca
    # ------------------------------------------------------------------ #
    grade = ft.GridView(expand=True, runs_count=4, max_extent=110,
                        child_aspect_ratio=0.8, spacing=8, run_spacing=8, padding=12)

    def render(jogadores):
        grade.controls = [avatar_widget(p) for p in jogadores]
        page.update()

    def on_busca(e):
        render(servico.buscar(e.control.value))

    busca = ft.TextField(
        hint_text="Buscar jogador ou posição (ex: Brady, QB)...",
        prefix_icon=Icons.SEARCH, on_change=on_busca,
        border_color=Colors.WHITE24, color=Colors.WHITE,
        bgcolor=Colors.WHITE10, border_radius=12,
    )

    def on_toggle_modo(e):
        estado["comentarista"] = e.control.value
        modo_label.value = "Comentarista" if e.control.value else "Torcedor"
        page.update()

    modo_label = ft.Text("Torcedor", color=Colors.AMBER, weight=ft.FontWeight.BOLD)
    switch_modo = ft.Switch(value=False, on_change=on_toggle_modo,
                            active_color=Colors.INDIGO)

    topo = ft.Container(
        padding=ft.padding.only(16, 16, 16, 8),
        content=ft.Column([
            ft.Row([
                ft.Icon(Icons.SPORTS_FOOTBALL, color=Colors.AMBER, size=28),
                ft.Text("NFL Player Stats", size=22, weight=ft.FontWeight.BOLD,
                        color=Colors.WHITE, expand=True),
                ft.Row([ft.Text("Modo:", color=Colors.WHITE54, size=12),
                        modo_label, switch_modo], spacing=4),
            ]),
            ft.Row([
                ft.Text("Toque no avatar do jogador para ver os dados",
                        size=12, color=Colors.WHITE54, expand=True),
                ft.ElevatedButton(
                    "Ranking", icon=Icons.LEADERBOARD,
                    on_click=lambda e: abrir_ranking(),
                    bgcolor=Colors.INDIGO, color=Colors.WHITE),
            ]),
            busca,
        ], spacing=8),
    )

    # Carregamento inicial (mostra spinner enquanto lê os CSVs)
    carregando = ft.Column([
        ft.ProgressRing(color=Colors.AMBER),
        ft.Text("Carregando dados dos jogos...", color=Colors.WHITE70),
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
       alignment=ft.MainAxisAlignment.CENTER, expand=True)

    page.add(topo, carregando)
    page.update()

    # Lê os dados e troca o spinner pela grade
    jogadores = servico.jogadores_com_dados(limite=60)
    page.controls.remove(carregando)
    page.add(grade)
    render(jogadores)


if __name__ == "__main__":
    ft.app(target=main)
