"""
Camada de dados do app mobile.

Lê os CSVs do NFL Big Data Bowl (games, players, plays, pffScoutingData)
e monta, para cada jogador, os sub-dados exibidos ao clicar no avatar:
    - Lances        (jogadas em que o jogador participou)
    - Últimos jogos (jogos mais recentes do jogador)
    - Desempenho    (métricas agregadas de pressão/bloqueio da PFF)
    - Posição       (posição oficial + posições em que se alinhou)

Usa apenas a biblioteca padrão do Python (csv) para não exigir pandas.
"""

from __future__ import annotations

import csv
import glob
import json
import os
from collections import defaultdict
from dataclasses import dataclass, field


# Pasta onde estão os CSVs. Pode ser trocada por variável de ambiente.
DATA_DIR = os.environ.get("NFL_DATA_DIR", r"C:\Users\aluno\Downloads\data")

# Duração média de uma jogada com bola em jogo (snap -> fim), em segundos.
# Valor calibrado a partir do tracking real: 41,5 frames a 10 fps = 4,2 s.
SEG_POR_LANCE = 4.2


def _f(value: str) -> float:
    """Converte texto em número, tratando 'NA'/vazio como 0."""
    if value is None:
        return 0.0
    value = value.strip()
    if value == "" or value.upper() == "NA":
        return 0.0
    try:
        return float(value)
    except ValueError:
        return 0.0


@dataclass
class Player:
    nfl_id: str
    name: str
    position: str
    height: str
    weight: str
    college: str
    team: str = ""   # sigla do time (vem do tracking)

    # sub-dados
    lances: list = field(default_factory=list)        # jogadas
    jogos: list = field(default_factory=list)          # jogos (mais recentes primeiro)
    aligned_positions: dict = field(default_factory=dict)

    # totais de desempenho (defesa)
    hits: int = 0
    hurries: int = 0
    sacks: int = 0
    # totais de desempenho (bloqueio ofensivo)
    hits_allowed: int = 0
    hurries_allowed: int = 0
    sacks_allowed: int = 0
    beaten: int = 0

    @property
    def total_lances(self) -> int:
        return len(self.lances)

    @property
    def initials(self) -> str:
        parts = [p for p in self.name.split() if p]
        if not parts:
            return "?"
        if len(parts) == 1:
            return parts[0][:2].upper()
        return (parts[0][0] + parts[-1][0]).upper()

    @property
    def desempenho_score(self) -> int:
        """Nota simples 0-100 combinando ações positivas e negativas."""
        positivos = self.sacks * 4 + self.hits * 3 + self.hurries * 2
        negativos = self.sacks_allowed * 4 + self.hits_allowed * 3 + \
            self.hurries_allowed * 2 + self.beaten
        bruto = 50 + positivos * 2 - negativos * 2
        return max(0, min(100, bruto))

    # ------------------------------------------------------------------ #
    # Participação por jogo (aproximação de rodízio / possível ausência)
    # ------------------------------------------------------------------ #
    def participacao(self) -> dict:
        """
        Analisa quantos lances o jogador teve em cada jogo, na ordem
        cronológica (por semana), e sinaliza quedas bruscas.

        Não é dado oficial de lesão/substituição (esses não existem nos
        arquivos). É apenas uma estimativa a partir do volume de lances:
        uma queda forte pode indicar rodízio, saída no meio do jogo ou
        ausência. Serve como indício, não como confirmação.

        Retorna um dicionário com a linha do tempo e um resumo.
        """
        # ordem cronológica = por gameId crescente (cresce com o tempo)
        jogos = sorted(self.jogos, key=lambda j: j["gameId"])
        if not jogos:
            return {"linha": [], "media": 0, "pico": 0, "alertas": [], "resumo": "Sem jogos."}

        valores = [j["n_lances"] for j in jogos]
        pico = max(valores)
        media = round(sum(valores) / len(valores), 1)

        linha = []
        alertas = []
        anterior = None
        for jogo in jogos:
            n = jogo["n_lances"]
            # percentual em relação ao pico do próprio jogador
            pct_pico = round(100 * n / pico) if pico else 0

            queda = False
            nota = ""
            if pct_pico <= 40:
                queda = True
                nota = "Participação muito baixa"
            elif anterior is not None and anterior > 0 and n <= anterior * 0.5:
                queda = True
                nota = "Caiu para menos da metade do jogo anterior"

            if queda:
                alertas.append(
                    f"Semana {jogo['week']}: {n} lances "
                    f"({pct_pico}% do seu pico) - {nota}"
                )

            linha.append({
                "week": jogo["week"],
                "gameId": jogo["gameId"],
                "matchup": f"{jogo['visitor']} @ {jogo['home']}",
                "n_lances": n,
                "pct_pico": pct_pico,
                "queda": queda,
            })
            anterior = n

        if alertas:
            resumo = (f"Detectadas {len(alertas)} queda(s) de participação. "
                      f"Pode indicar rodízio ou ausência (não confirmado).")
        else:
            resumo = "Participação estável em todos os jogos."

        return {
            "linha": linha,
            "media": media,
            "pico": pico,
            "alertas": alertas,
            "resumo": resumo,
            "jogos_disputados": len(jogos),
        }

    # ------------------------------------------------------------------ #
    # Minutagem em campo (estimada a partir do nº de lances)
    # ------------------------------------------------------------------ #
    @property
    def segundos_totais(self) -> float:
        """Tempo total estimado de bola em jogo (snap->fim) em segundos."""
        return self.total_lances * SEG_POR_LANCE

    @property
    def minutos_totais(self) -> float:
        return round(self.segundos_totais / 60, 1)

    @property
    def minutos_por_jogo(self) -> float:
        n = len(self.jogos)
        if not n:
            return 0.0
        return round(self.minutos_totais / n, 1)

    def minutagem_por_jogo(self) -> list:
        """
        Minutagem estimada em cada jogo (do mais recente para o mais antigo).
        min:seg = n_lances * SEG_POR_LANCE. É tempo de bola em jogo, não o
        tempo total de relógio (os arquivos não trazem minutos oficiais).
        """
        out = []
        for jogo in self.jogos:  # já vem ordenado do mais recente
            seg = jogo["n_lances"] * SEG_POR_LANCE
            out.append({
                "week": jogo["week"],
                "date": jogo["date"],
                "matchup": f"{jogo['visitor']} @ {jogo['home']}",
                "n_lances": jogo["n_lances"],
                "segundos": round(seg),
                "mmss": f"{int(seg // 60)}:{int(seg % 60):02d}",
                "minutos": round(seg / 60, 1),
            })
        return out


class DataService:
    """Carrega os CSVs uma vez e serve consultas por jogador."""

    def __init__(self, data_dir: str = DATA_DIR):
        self.data_dir = data_dir
        self.players: dict[str, Player] = {}
        self.games: dict[str, dict] = {}
        self.plays: dict[tuple, dict] = {}
        self._loaded = False

    # ------------------------------------------------------------------ #
    # Carregamento
    # ------------------------------------------------------------------ #
    def _path(self, name: str) -> str:
        return os.path.join(self.data_dir, name)

    def load(self) -> None:
        if self._loaded:
            return
        self._load_games()
        self._load_players()
        self._load_plays()
        self._load_pff()
        self._sort_games()
        self._load_teams()
        self._loaded = True

    # ------------------------------------------------------------------ #
    # Time do jogador (vem dos arquivos de tracking; usa cache em JSON)
    # ------------------------------------------------------------------ #
    def _cache_path(self) -> str:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "player_team_cache.json")

    def _load_teams(self) -> None:
        """
        Mapeia nflId -> time (sigla) lendo a coluna `team` do tracking.

        Os arquivos de tracking são grandes (~800 MB somados), então na
        primeira vez lemos todos e gravamos um cache pequeno em JSON.
        Nas próximas execuções, só lemos o cache.
        """
        mapa = self._ler_cache_times()
        if mapa is None:
            mapa = self._construir_mapa_times()
            self._gravar_cache_times(mapa)

        for nfl_id, team in mapa.items():
            p = self.players.get(nfl_id)
            if p is not None:
                p.team = team

    def _ler_cache_times(self):
        caminho = self._cache_path()
        if not os.path.exists(caminho):
            return None
        try:
            with open(caminho, encoding="utf-8") as fh:
                return json.load(fh)
        except (OSError, json.JSONDecodeError):
            return None

    def _gravar_cache_times(self, mapa: dict) -> None:
        try:
            with open(self._cache_path(), "w", encoding="utf-8") as fh:
                json.dump(mapa, fh)
        except OSError:
            pass  # cache é opcional; se falhar, apenas relê na próxima vez

    def _construir_mapa_times(self) -> dict:
        """Lê a coluna `team` de cada arquivo de tracking (só as colunas úteis)."""
        mapa: dict[str, str] = {}
        padrao = os.path.join(self.data_dir, "tracking", "tracking_*.csv")
        for arquivo in glob.glob(padrao):
            try:
                with open(arquivo, newline="", encoding="utf-8") as fh:
                    leitor = csv.DictReader(fh)
                    for row in leitor:
                        # cada jogador aparece já no 1º frame de cada jogada;
                        # ler só frameId == "1" cobre todos e é bem mais rápido.
                        if (row.get("frameId") or "").strip() != "1":
                            continue
                        nid = (row.get("nflId") or "").strip()
                        team = (row.get("team") or "").strip()
                        if (nid and nid.upper() != "NA"
                                and team and team.lower() != "football"
                                and nid not in mapa):
                            mapa[nid] = team
            except OSError:
                continue
        return mapa

    def _load_games(self) -> None:
        with open(self._path("games.csv"), newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                self.games[row["gameId"]] = row

    def _load_players(self) -> None:
        with open(self._path("players.csv"), newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                self.players[row["nflId"]] = Player(
                    nfl_id=row["nflId"],
                    name=row.get("displayName", "").strip(),
                    position=row.get("officialPosition", "").strip(),
                    height=row.get("height", "").strip(),
                    weight=row.get("weight", "").strip(),
                    college=row.get("collegeName", "").strip(),
                )

    def _load_plays(self) -> None:
        with open(self._path("plays.csv"), newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                self.plays[(row["gameId"], row["playId"])] = row

    def _load_pff(self) -> None:
        """Lê o scouting e distribui as jogadas/estatísticas por jogador."""
        with open(self._path("pffScoutingData.csv"), newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                nfl_id = row.get("nflId", "").strip()
                player = self.players.get(nfl_id)
                if player is None:
                    continue

                game_id = row["gameId"]
                play_id = row["playId"]
                play = self.plays.get((game_id, play_id), {})

                # --- Lance ---
                player.lances.append({
                    "gameId": game_id,
                    "playId": play_id,
                    "role": row.get("pff_role", "").strip(),
                    "position": row.get("pff_positionLinedUp", "").strip(),
                    "desc": play.get("playDescription", "").strip(),
                    "coverage": play.get("pff_passCoverage", "").strip(),
                    "quarter": play.get("quarter", "").strip(),
                    "down": play.get("down", "").strip(),
                })

                # --- Posições alinhadas ---
                pos = row.get("pff_positionLinedUp", "").strip()
                if pos and pos.upper() != "NA":
                    player.aligned_positions[pos] = player.aligned_positions.get(pos, 0) + 1

                # --- Desempenho (defesa) ---
                player.hits += int(_f(row.get("pff_hit")))
                player.hurries += int(_f(row.get("pff_hurry")))
                player.sacks += int(_f(row.get("pff_sack")))
                # --- Desempenho (bloqueio ofensivo) ---
                player.hits_allowed += int(_f(row.get("pff_hitAllowed")))
                player.hurries_allowed += int(_f(row.get("pff_hurryAllowed")))
                player.sacks_allowed += int(_f(row.get("pff_sackAllowed")))
                player.beaten += int(_f(row.get("pff_beatenByDefender")))

    def _sort_games(self) -> None:
        """Monta a lista de jogos por jogador, ordenada do mais recente."""
        for player in self.players.values():
            game_ids = {lance["gameId"] for lance in player.lances}
            jogos = []
            for gid in game_ids:
                g = self.games.get(gid, {})
                jogos.append({
                    "gameId": gid,
                    "date": g.get("gameDate", ""),
                    "week": g.get("week", ""),
                    "home": g.get("homeTeamAbbr", ""),
                    "visitor": g.get("visitorTeamAbbr", ""),
                    "n_lances": sum(1 for l in player.lances if l["gameId"] == gid),
                })
            # gameId cresce com o tempo, então ordenar desc = mais recente primeiro
            jogos.sort(key=lambda j: j["gameId"], reverse=True)
            player.jogos = jogos

    # ------------------------------------------------------------------ #
    # Consultas usadas pela UI
    # ------------------------------------------------------------------ #
    def jogadores_com_dados(self, limite: int = 60) -> list[Player]:
        """Jogadores que aparecem em jogadas, ordenados por nº de lances."""
        self.load()
        com_lances = [p for p in self.players.values() if p.lances]
        com_lances.sort(key=lambda p: p.total_lances, reverse=True)
        return com_lances[:limite]

    def buscar(self, termo: str, limite: int = 60) -> list[Player]:
        termo = termo.strip().lower()
        base = self.jogadores_com_dados(limite=10_000)
        if not termo:
            return base[:limite]
        filtrados = [p for p in base if termo in p.name.lower()
                     or termo in p.position.lower()]
        return filtrados[:limite]

    # ------------------------------------------------------------------ #
    # Ranking de jogadores
    # ------------------------------------------------------------------ #
    # critérios disponíveis: chave -> (rótulo, função que extrai o valor)
    CRITERIOS_RANKING = {
        "minutagem": ("Minutagem (min)", lambda p: p.minutos_totais),
        "lances": ("Lances", lambda p: p.total_lances),
        "desempenho": ("Desempenho (nota)", lambda p: p.desempenho_score),
        "sacks": ("Sacks", lambda p: p.sacks),
        "hurries": ("Hurries", lambda p: p.hurries),
        "hits": ("Hits", lambda p: p.hits),
        "min_por_jogo": ("Min/jogo", lambda p: p.minutos_por_jogo),
    }

    def ranking(self, criterio: str = "minutagem", limite: int = 50,
                posicao: str | None = None,
                time: str | None = None) -> list[tuple[int, Player, float]]:
        """
        Retorna [(colocacao, Player, valor)] ordenado pelo critério escolhido.
        Usa apenas os dados dos arquivos (via os tópicos já calculados:
        minutagem, lances, desempenho, sacks, hurries, hits).
        Pode filtrar por posição e/ou por time.
        """
        self.load()
        rotulo, extrair = self.CRITERIOS_RANKING.get(
            criterio, self.CRITERIOS_RANKING["minutagem"])

        jogadores = [p for p in self.players.values() if p.lances]
        if posicao:
            posicao = posicao.strip().upper()
            jogadores = [p for p in jogadores if p.position.upper() == posicao]
        if time:
            time = time.strip().upper()
            jogadores = [p for p in jogadores if p.team.upper() == time]

        jogadores.sort(key=lambda p: (extrair(p), p.total_lances), reverse=True)

        resultado = []
        for i, p in enumerate(jogadores[:limite], start=1):
            resultado.append((i, p, extrair(p)))
        return resultado

    def rotulo_criterio(self, criterio: str) -> str:
        return self.CRITERIOS_RANKING.get(
            criterio, self.CRITERIOS_RANKING["minutagem"])[0]

    def posicoes_disponiveis(self) -> list[str]:
        """Posições oficiais existentes entre os jogadores com dados, ordenadas."""
        self.load()
        posicoes = {p.position.strip().upper()
                    for p in self.players.values()
                    if p.lances and p.position.strip()}
        return sorted(posicoes)

    def times_disponiveis(self) -> list[str]:
        """Times (siglas) existentes entre os jogadores com dados, ordenados."""
        self.load()
        times = {p.team.strip().upper()
                 for p in self.players.values()
                 if p.lances and p.team.strip()}
        return sorted(times)
