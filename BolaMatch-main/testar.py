"""
Teste geral do app (sem abrir a interface).

Valida a camada de dados de ponta a ponta: carga dos CSVs, cálculo de
lances/jogos/desempenho, minutagem, participação, ranking e os filtros
por posição e time.

Como rodar (PowerShell, dentro da pasta do projeto):
    py app\testar.py

Se tudo passar, aparece "TODOS OS TESTES PASSARAM" no final.
"""

import sys
from data_service import DataService


def check(nome, condicao, detalhe=""):
    status = "OK  " if condicao else "FALHOU"
    print(f"[{status}] {nome}" + (f"  -> {detalhe}" if detalhe else ""))
    return bool(condicao)


def main():
    print("Carregando dados (a 1a vez pode demorar ~40s pelo cache de times)...\n")
    s = DataService()
    s.load()

    ok = True

    # 1. Carga básica
    ok &= check("games.csv carregado", len(s.games) > 0, f"{len(s.games)} jogos")
    ok &= check("players.csv carregado", len(s.players) > 0,
                f"{len(s.players)} jogadores")
    ok &= check("plays.csv carregado", len(s.plays) > 0, f"{len(s.plays)} jogadas")

    # 2. Jogadores com dados
    jogadores = s.jogadores_com_dados(10)
    ok &= check("jogadores com lances", len(jogadores) > 0,
                f"{len(jogadores)} no topo")

    p = jogadores[0]
    # 3. Sub-dados do jogador
    ok &= check("jogador tem lances", p.total_lances > 0, f"{p.total_lances} lances")
    ok &= check("jogador tem jogos", len(p.jogos) > 0, f"{len(p.jogos)} jogos")
    ok &= check("desempenho entre 0-100", 0 <= p.desempenho_score <= 100,
                f"nota {p.desempenho_score}")

    # 4. Minutagem
    ok &= check("minutagem total > 0", p.minutos_totais > 0,
                f"{p.minutos_totais} min")
    mpj = p.minutagem_por_jogo()
    ok &= check("minutagem por jogo tem mm:ss", bool(mpj) and ":" in mpj[0]["mmss"],
                mpj[0]["mmss"] if mpj else "vazio")

    # 5. Participação
    part = p.participacao()
    ok &= check("participacao tem linha do tempo", len(part["linha"]) > 0,
                f"{len(part['linha'])} jogos")

    # 6. Time (vem do tracking)
    com_time = [x for x in s.players.values() if x.lances and x.team]
    ok &= check("jogadores com time definido", len(com_time) > 0,
                f"{len(com_time)} com time")
    times = s.times_disponiveis()
    ok &= check("lista de times", len(times) > 0, f"{len(times)} times")

    # 7. Ranking geral
    r = s.ranking("sacks", limite=5)
    ok &= check("ranking por sacks retorna resultados", len(r) > 0,
                f"lider: {r[0][1].name} ({r[0][2]} sacks)" if r else "vazio")

    # 8. Ranking com filtro de posição
    pos = s.posicoes_disponiveis()[0]
    rp = s.ranking("minutagem", limite=5, posicao=pos)
    ok &= check(f"ranking filtrado por posicao ({pos})",
                all(x[1].position.upper() == pos for x in rp),
                f"{len(rp)} jogadores")

    # 9. Ranking com filtro de time
    if times:
        tm = times[0]
        rt = s.ranking("minutagem", limite=5, time=tm)
        ok &= check(f"ranking filtrado por time ({tm})",
                    all(x[1].team.upper() == tm for x in rt),
                    f"{len(rt)} jogadores")

    # 10. Busca
    b = s.buscar("QB")
    ok &= check("busca por 'QB' retorna jogadores", len(b) > 0, f"{len(b)} achados")

    print()
    if ok:
        print("==============================")
        print("  TODOS OS TESTES PASSARAM")
        print("==============================")
        return 0
    else:
        print("!!! ALGUM TESTE FALHOU - veja as linhas [FALHOU] acima")
        return 1


if __name__ == "__main__":
    sys.exit(main())
