# 📖 Instruções de Uso — BolaMatch

Guia passo a passo para **instalar, abrir e usar** o aplicativo BolaMatch.
Feito para qualquer pessoa conseguir rodar, mesmo sem experiência com Python.

---

## 👥 Participantes

Felipe Miguel Caetano Oliveira · Marcos Paulo Lima Soares ·
Gabrielle Gaya da Silva · Rennan Fernandes de Mesquita

---

## 1️⃣ Antes de começar (pré-requisitos)

Você precisa de:

1. **Python 3** instalado (o app foi testado no Python 3.14).
   - Para conferir, abra o **PowerShell** e digite:
     ```powershell
     py --version
     ```
   - Se aparecer algo como `Python 3.14.0`, está tudo certo.
   - Se não aparecer, instale pelo site oficial: https://www.python.org/downloads/

2. Os **arquivos de dados** (CSVs) na pasta:
   ```
   C:\Users\aluno\Downloads\data
   ```
   Devem existir ali: `games.csv`, `players.csv`, `plays.csv`,
   `pffScoutingData.csv` e a pasta `tracking`.

> 💡 Se os dados estiverem em outra pasta, veja a seção 6 (Dúvidas comuns).

---

## 2️⃣ Instalar o aplicativo (uma vez só)

Abra o **PowerShell** na pasta do projeto (a pasta `app`) e rode:

```powershell
py -m pip install -r requirements.txt
```

Isso instala o **Flet** (a tecnologia da interface). Precisa de internet
**apenas nesta etapa**. Depois de instalado, o app funciona **offline**.

---

## 3️⃣ Abrir o aplicativo

Ainda no PowerShell, dentro da pasta `app`, escolha uma das formas:

| Onde quer usar | Comando |
|----------------|---------|
| 💻 Janela no computador | `py -m flet run bolamatch.py` |
| 🌐 No navegador (web) | `py -m flet run --web bolamatch.py` |
| 📱 No celular | `py -m flet run --android bolamatch.py` |

> ⏳ **Na primeira vez** o app demora cerca de **40 segundos** para abrir,
> porque ele lê os arquivos de jogos uma única vez e guarda um atalho
> (`player_team_cache.json`). Nas próximas vezes abre rápido.

Para usar **no celular**: instale o aplicativo **"Flet"** na loja (Play Store /
App Store), rode o comando `--android`, e escaneie o **QR code** que aparece.
O celular e o computador precisam estar na **mesma rede Wi‑Fi**.

---

## 4️⃣ Usando o app — passo a passo

### Passo 1 — Login
- Digite um **e-mail** e uma **senha**.
- Toque em **ENTRAR** (ou em "Cadastre-se") para ir ao cadastro.

### Passo 2 — Cadastro e escolha do perfil
- Preencha **e-mail**, **senha** (mínimo 6 caracteres) e **confirmar senha**.
- Escolha o **tipo de perfil** tocando em um dos cartões:
  - 🙋 **Usuário (Torcedor)** — visão simples e rápida.
  - 🎙️ **Comentarista** — visão completa e técnica.
- Toque em **CRIAR MINHA CONTA**. Você entra na **HOME**.

### Passo 3 — HOME (tela principal)
- Aparece uma **grade de avatares** dos jogadores (cada cor é uma posição).
- Use a **🔎 busca** para achar um jogador pelo nome ou posição
  (ex.: `Brady`, `QB`).
- Toque no **botão 🏆 Ranking** para ver a classificação dos jogadores.
- Toque no ícone **⏻ (sair)** para voltar ao login.

### Passo 4 — Ver os dados de um jogador
Toque no **avatar** de um jogador. Abre um painel com abas:

| Aba | O que mostra |
|-----|--------------|
| **Lances** | Jogadas em que ele participou |
| **Jogos** | Jogos do mais recente ao mais antigo |
| **Minutagem** | Tempo em campo por jogo (mm:ss) |
| **Desempenho** | Nota de 0 a 100 |
| **Participação** | *(só Comentarista)* lances por jogo |
| **Posição** | Posição, altura, peso, faculdade |

### Passo 5 — Usar o Ranking
- Toque em **🏆 Ranking**.
- Escolha **Ordenar por** (minutagem, lances, sacks…).
- Filtre por **Posição** e por **Time**.
- Toque em um jogador da lista para ver os detalhes dele.

---

## 5️⃣ Diferença entre os perfis

```
🙋 TORCEDOR                       🎙️ COMENTARISTA
────────────────                 ─────────────────
• Linguagem simples              • Linguagem técnica
• 5 abas por jogador             • 6 abas (inclui Participação)
• Desempenho em frase            • Hits, hurries e sacks
• Ranking básico                 • Ranking completo + filtro de time
```

O perfil é escolhido no **cadastro**. Para trocar, saia (⏻) e cadastre-se
novamente com o outro perfil.

---

## 6️⃣ Dúvidas comuns (resolução de problemas)

**❓ Aparece "Python não foi encontrado".**
Use `py` em vez de `python`. Se ainda não funcionar, reinstale o Python
marcando a opção **"Add Python to PATH"**.

**❓ Erro "No module named 'flet'".**
Você pulou a instalação. Rode de novo:
`py -m pip install -r requirements.txt`

**❓ O app abre mas não aparece nenhum jogador.**
Os CSVs não foram encontrados. Confira se a pasta
`C:\Users\aluno\Downloads\data` existe com os arquivos.
Se os dados estiverem em outro lugar, aponte assim antes de rodar:
```powershell
$env:NFL_DATA_DIR = "D:\caminho\para\data"
py -m flet run bolamatch.py
```
E apague o `player_team_cache.json` para recriar o cache.

**❓ Quero testar se está tudo certo sem abrir a tela.**
```powershell
py testar.py             # testa os dados
py testar_bolamatch.py   # testa a interface
```
Deve aparecer "TESTES PASSARAM".

**❓ A pasta do app está no Temp e some.**
A pasta atual (`AppData\Local\Temp`) é temporária. Copie a pasta `app` para
um local permanente, como `Documentos`, para não perder o projeto.

---

## 7️⃣ Sobre os dados

Os dados são do **NFL Big Data Bowl**, temporada **2021 (semanas 1–8)**.
A base **não** contém temporadas anteriores, lesões nem suspensões — esses
campos não existem nos arquivos. Minutagem e participação são **estimativas**
a partir do número de jogadas, não valores oficiais.
