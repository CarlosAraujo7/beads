# Bead Studio — instruções para agentes

Editor local de moldes para contas de fusão (hama/Pindou), em português do Brasil. O dono do projeto é um hobbista que está começando com contas e **manda imagens em pastas `remessa N`**; o trabalho recorrente é **converter essas imagens em templates** (moldes) e colocá-los no catálogo do app. Este arquivo descreve o projeto e, principalmente, **o processo exato** usado até aqui (remessas 1–12, 386 templates + 70 do levantamento "Outros" + 32 versões de 1 placa; o catálogo do usuário varia, porque ele exclui e ajusta).

Responda ao usuário sempre em **pt-BR**. Ele é direto e confere a qualidade olhando as imagens: nunca diga que algo está bom sem ter renderizado e olhado.

---

## 1. O que existe na pasta

| Caminho | O que é |
|---|---|
| `index.html` | O app inteiro (HTML+CSS+JS puro, sem build; abre com duplo clique). ~135 KB. |
| `templates.js` | **Arquivo gerado** com o catálogo. Nunca edite à mão: regenere com `tools/build_templates.py`. |
| `remessa 1` … `remessa 12` | Imagens que o usuário enviou (entrada). Não apague nem renomeie. |
| `tools/` | Todo o pipeline de conversão (Python) + os dados-fonte em `tools/data/*.json`. |
| `tools/out/` | Saída descartável (prévias PNG, temporários). Criada automaticamente; pode apagar. |
| `tools/backups/` | Cópias de segurança automáticas do `templates.js` (feitas pelo app ao gravar e pelos scripts antes de sobrescrever; guarda as últimas 30). |

Ferramentas avulsas em `tools/` (todas com a explicação no cabeçalho do arquivo):
- `layoutsim.py` (compara desenhos de forma tolerante; ≥ 0,85 ≈ mesmo desenho, mas confira olhando) e `triage.py N` (folha de triagem: imagem | conversão fiel | molde parecido do catálogo; serve para saber o que **não** está no catálogo), `dupcheck.py` (cópias por conteúdo);
- `shrink.py` + `make_1placa.py` (versão reduzida "<nome> (1 placa)" dos moldes > 50×50; ver §10);
- `r_outros.py` + `photo7.py` + `data/outros_pool.json` (levantamento "Outros": converte tudo que faltava no catálogo das remessas 1–12; `photo7` = fotos de peças prontas com paleta explícita; ver §7.4 e §10).

Dependências: Python 3.12 com `numpy`, `Pillow`, `opencv-python` (`cv2`); `node` só para `node --check templates.js`.

Os scripts de `tools/` resolvem os caminhos **relativos à própria pasta** (a raiz do projeto é a pasta acima de `tools/`), então rodam de qualquer diretório.

## 2. Fatos do hardware (não mudam)

- Kit do usuário: **Pindou nº 1, 24 cores**, contas de 2,6 mm; placa transparente de ~**50×50** pinos. A placa é uma configuração do app.
- Paleta (código Pindou → letra usada nos templates → hex). **Só estas 24 letras existem**; `.` = vazio.

| letra | cód | hex | letra | cód | hex | letra | cód | hex |
|---|---|---|---|---|---|---|---|---|
| k | H7 | #2E2E32 (preto) | w | H2 | #FFFFFF | i | H1 | #E4E7EA |
| d | H5 | #5F6065 | m | H4 | #8A8D93 | l | H3 | #B5B8BE |
| r | F5 | #BD3A4B (vermelho) | p | E4 | #EA9BB8 (rosa) | q | E2 | #F1C4D1 |
| o | A7 | #EC8546 (laranja) | a | A6 | #E9A23B (âmbar) | y | A4 | #EBC22F (amarelo) |
| s | G1 | #E4C7B5 (bege/pele) | t | G5 | #D99479 (salmão/marrom claro) | n | G7 | #8F5E50 (marrom) |
| b | C8 | #6B98D3 (azul) | c | C5 | #55BEDB (ciano) | e | C3 | #C3E5F3 (azul claro) |
| u | D7 | #75609A (roxo) | v | D6 | #A89BC6 (lavanda) | x | D9 | #C8C4E4 (lilás) |
| g | B3 | #7FC79C (menta) | f | B5 | #5FA66E (verde) | h | B8 | #3F8761 (verde escuro) |

A paleta **não tem**: azul-marinho, bege-creme, verde-limão, turquesa, marrom-escuro. Toda conversão é um compromisso (veja §6.3). As definições estão em `tools/img2tpl.py` (`PAL`, `LETTER`).

## 3. Formato de `templates.js`

```js
window.TPL_LEGEND = {"k":"H7", ...};
window.TEMPLATES = [
{id:"gon-freecss",cat:"hunter-x-hunter",group:"Hunter x Hunter",name:"Gon Freecss",rows:[
"....kk....",
"..kkyykk..",
]},
...
];
```

- `rows`: todas as linhas com o mesmo comprimento; cada caractere é uma letra da paleta ou `.`.
- **Um molde tem só NOME e CATEGORIA** (desde 2026-10-25 o app não tem mais "série"/chips). `cat` = id da categoria; `group` continua existindo no arquivo só por compatibilidade e é sempre **o nome de exibição da categoria** (o app grava assim; `add_templates.py` também). Nunca use `group` como subgrupo. **Organização atual: cada categoria é uma FRANQUIA** (Naruto, One Piece, Dragon Ball, Pokémon, Marvel, Lilo & Stitch…, ~80 categorias); o que não foi identificado fica em **"Outros"** (`other`) para o usuário ajustar. Exceção intencional: `earrings` = "Brincos" (uso, não franquia). As categorias genéricas do padrão (`anime`, `games`, `heroes`, `cinema`, `toons`, `animals`, `symbols`, `claude`) continuam no código (`TPL_CATS`) mas ficam **escondidas** (`hidden` em `TPL_CATS_CFG`).
- A lista de franquias, a ordem e o mapeamento nome→franquia estão em `tools/franchises.py` (`CATEGORIES`, `GROUP_MAP`, `NAME_MAP`); a aplicação única foi `tools/reorganize.py` (com `--dry`). As categorias criadas ficam em `TPL_CATS_CFG.custom` (ids em slug, ex.: `one-piece`, `lilo-stitch`).
- `id` é gerado do nome (slug sem acentos); repetido ganha `-2`, `-3`…
- **O "série" do `rN_exfinal.py` (2º item de cada tupla) é só a franquia de origem**; `add_templates.py` a resolve assim: nome igual ao de uma categoria existente (inclusive as que o usuário criou/renomeou) → `GROUP_MAP` de `franchises.py` → categoria mais usada por aquela série no catálogo → **franquia nova = categoria nova**: o script cria a categoria sozinho (id em slug, ícone `cStar` ou o de `franchises.py`). Nomes genéricos (`GENERIC_GROUPS` em `franchises.py`: "Outros animes", "Animais"…) vão para "Outros". `tools/cats.py` (`CATS`) é só do build legado.
- Depois que o usuário usa **Moldes → Gerenciar → Gravar no catálogo** (ou depois de rodar `add_templates.py`), o arquivo ganha também: `window.TPL_CATS_CFG` (organização das categorias: `order`, `names`, `icons`, `custom`, `hidden`), `window.TPL_BAKED` (carimbo; **marca o arquivo como "fonte da verdade"**) e `window.TPL_REMOVED` (nomes que o usuário excluiu, para `add_templates.py` não trazê-los de volta). **A partir daí o `templates.js` é o banco de dados do catálogo**: não o regenere pelo `build_templates.py` (ele se recusa; veja §5).
- O app guarda no navegador do usuário (localStorage): `beadstudio.v1` (autosave), `beadstudio.mine` (templates próprios: `{id,name,w,h,grid[,cat]}`), `beadstudio.edits` (ajustes de **desenho** sobre templates do catálogo: id → {name,w,h,grid}), `beadstudio.deleted` (ids do catálogo que ele excluiu → categoria "Excluídos"), `beadstudio.meta` (**nome / categoria** que ele escolheu para templates do catálogo: id → {name,cat}; a entrada some se ele voltar ao original) e `beadstudio.cats` (organização das categorias: `{order,names,icons,custom:[{id,name,icon}],hidden,alpha}`) e `beadstudio.tplview` (`"blocks"`|`"list"`: como a galeria mostra as categorias). O **Menu** do editor exporta/importa `meus-templates-bead-studio.json` (v2) com tudo isso. Se o usuário mandar esse arquivo, o que ele fez no app ainda **não** está em `templates.js` (veja §9).

### Interface (`index.html`) — onde mexer
- **Duas telas, sempre abre na inicial** (a pedido do usuário, 2026-10-25): `body[data-view="home"|"edit"]`, trocado por `setView(v)`; `goHome()`/`popstate` usam `history` (`#editar`), então o "voltar" do navegador volta ao início. A **tela inicial** (`#home`, `renderHome()`) tem saudação, busca (`#homeSearch`; resultados ali mesmo, Enter abre a galeria), cartão "Continuar de onde parou" (só se o projeto salvo tem contas; `artCrop()` para a miniatura), 4 ações (Escolher um molde / Desenhar do zero / Imagem → contas / Abrir projeto), "Novidades no catálogo" (os **últimos 12 de `window.TEMPLATES`**, ou seja, o que o `add_templates.py` acrescentou por último) e as categorias com mais moldes. O desenho em andamento continua no autosave (`beadstudio.v1`) e **não** abre sozinho. `openTpl()` pergunta antes de substituir um desenho solto/alterado/com progresso de montagem (`okToReplace()`). `fitZoom()` não faz nada com o editor escondido (`fitPending`) e roda ao abrir o editor.
- **Botão Voltar (ir olhando moldes e voltando)**: ao abrir um molde por clique numa lista, `openTpl()` guarda de onde veio em `navBack` (`captureNav`): da **galeria** (`tplCat`, `tplQuery`, `tplView`, rolagem de `#tplMain` e `#tplSide`, rolagem de dentro do bloco `.cblock .cthumbs` e se a galeria estava por cima da tela inicial ou do editor, `galleryUnder`) ou da **tela inicial** (rolagem de `#home`, das novidades `#homeNewRow` e a busca `homeQ`). No editor aparece `#btnBack` ("Voltar aos moldes" / "Voltar à busca" / "Voltar"; só a seta no celular). `goBack()` → `pendingRestore` → `applyRestore()` (chamado ao fim de `setView('home')` e direto quando a galeria estava por cima do editor) devolve tudo e **destaca o molde visto** (`.flash`, `flashItem`). O "voltar" do navegador faz o mesmo (`popstate`). `navBack` é zerado por Início, por `setGrid` (novo desenho, imagem, abrir projeto) e depois de usado. Não troque a ordem em `openTpl`: capturar antes de `okToReplace()`/`dialog.close()` e só gravar `navBack` depois de `setGrid`.
- **Editor enxuto**: barra de ferramentas só com ícones à esquerda (`.rail`, `#tools`; atalhos B E G I L R O **S** M), opções da ferramenta só quando fazem sentido (`#optBrush`, `#optFill`, `#optMirror`, `#optSelect` na `.viewbar`, ligadas em `setTool`), paleta numa faixa embaixo (`.dock`, `#palette`; mesma ordem da tabela impressa; 12+12 cores, ou 24 numa linha quando cabe — `@container dock`), menu **Exibir** (grade, códigos, contas/pixels), botão `#btnPanel` esconde o painel direito (`beadstudio.panel`). Painel direito: aba **Contas** (3 números + lista por cor; o campo "tenho" só aparece com "Conferir meu estoque", `S.showStock`) e aba **Ajustes** (seções recolhíveis `<details class="acc">`). Menu **Menu** (`#fileMenu`): escolher molde, novo desenho, imagem → contas, salvar, exportar, ajustar cores, gravar no catálogo, exportar/importar moldes. Todos os `.menu` abrem/fecham pelo mesmo código (`menus`/`closeMenus`; `data-stay` mantém aberto).
- **Selecionar contas** (botão **Selecionar** na barra de cima, nos modos Criar e Montar; atalho S; Ctrl+A tudo; Esc limpa): **igual ao pincel — botão ESQUERDO seleciona, botão DIREITO tira da seleção, sem teclas** (o usuário disse que Alt+clique não funcionou; **não use Shift/Alt/Ctrl para nada na seleção**). Formatos (`S.selShape`, lembrado em `beadstudio.selshape`): **Pincel** (padrão: passar sobre as contas; `selStamp` + `bres`), **Linha** (clique = linha inteira, arrastar = só o trecho; o desvio vertical do mouse é ignorado), **Coluna** e **Área** (retângulo; `selRect`). Clicar nos **números da régua** (`rulerAt`) pega a linha/coluna inteira em qualquer modo (arrastar pelos números pega várias; o canto pega tudo; botão direito tira). Na **Montar** o botão liga `S.selOn` (desligado, o clique marca a conta como colocada) e o resumo diz "N já colocadas, M faltam". A seleção é uma máscara `S.sel` (com `S.selW/selH`; `selMask()` só vale se o tamanho da placa não mudou), desenhada em `draw()` e resumida em `#selChip` (`renderSel`/`selStats`/`selWhere`): quantas contas, onde ("Linha 12 inteira", "Linhas 4 a 6 inteiras"…) e a contagem por cor. Some ao trocar de molde/girar/espelhar. **A ajuda da ferramenta fica só na linha de baixo (`#hint`, `updHint()`). Não ponha texto nem botões a mais na barra de cima: se ela quebrar em 2 linhas a tela de desenho "pula" e o clique cai na linha errada** (por isso a barra tem container query que esconde a barrinha de zoom em larguras menores e o pincel de seleção tem sempre 1 conta de largura).
- **Aparência**: claro, escuro ou automático (`beadstudio.theme` = `light`|`dark`|ausente). `<html data-theme>` é sempre o valor resolvido (script no `<head>` aplica antes da primeira pintura); `applyTheme(pref)` atualiza botões e `readTheme()` (cores do canvas). As cores são variáveis em `:root` e `:root[data-theme="dark"]` — **não use cores fixas** nos componentes novos. O seletor fica nos botões `.themebtn` (início e editor; no celular dentro do Menu).
- **Textos**: no app o catálogo se chama **“moldes”** (não “templates”); o código e o arquivo `templates.js`/`meus-templates-bead-studio.json` continuam com “templates”.
- Galeria (agora **em tela cheia**, `<dialog id="dlgTemplates">` com cabeçalho Voltar · busca `#tplSearch` · Blocos/Lista · menu **Gerenciar** com Criar molde, Selecionar vários, Organizar categorias e Gravar no catálogo (bolinha = há alterações não gravadas); abrir por `openGallery({cat,query})`): `decodeTemplates()` junta catálogo + `edits` + `meta` + `mine` + `deleted` e devolve objetos `{id,name,cat,group,reqCat,...}` (`group` = nome da categoria efetiva); `renderTemplates()` desenha a galeria em **dois modos alternáveis** (botões `#tplViewSeg`, lembrado em `beadstudio.tplview`): **Blocos** (padrão: `renderBoard()`, um bloco `.cblock[data-cat]` por categoria com miniaturas `tplMini()`; clicar no nome do bloco abre aquela categoria em Lista; categorias nativas vazias não aparecem, as criadas pelo usuário aparecem com "Arraste moldes para cá") e **Lista** (barra lateral `#tplSide` + seções `.tsec[data-cat]` com cartões `tplCard()`); modo "Selecionar" (`tplSelMode`, `tplSel`, barra `#tplBar`); `openEditTpl(ids)` (renomear/mover um ou vários) e `applyPlacement(ids,{name,cat})` (grava em `meta` ou no registro de `mine`; se voltar ao nome/categoria originais, apaga a entrada de `meta`).
- **Arrastar e soltar**: cartões, miniaturas e (em modo Selecionar) a seleção inteira são `draggable`; soltar sobre qualquer elemento com `data-cat` (botão da barra lateral, bloco ou seção; "Todos" e "Excluídos" não valem) chama `moveToCat(ids,cat)`. Funções `tplDragStart`/`tplDragEnd` (os nomes `startDrag`/`endDrag` já existem no editor do canvas — não reutilize). Não funciona em tela de toque (HTML5 DnD): lá continuam o ✎ e Selecionar → Mover.
- Config local de categorias (`beadstudio.cats`) leva o carimbo `base` = `TPL_BAKED` do catálogo em que foi feita. Se o catálogo foi regravado/reorganizado depois (carimbo diferente), `loadCatCfg()` usa a organização do catálogo e mantém só as categorias que o usuário criou (`mergeStaleCfg`); `reconcileCats()` faz isso ao abrir e avisa com um toast. Mudança local de um template para categoria que não existe mais/está escondida é ignorada (vale a do catálogo). Sem isso, a config local antiga sobrescrevia a nova inteira.
- Categorias: `TPL_CATS` (padrão, no código) + `catList()` (aplica nomes/ícones/ordem/removidas/criadas de `beadstudio.cats`). **Ordem: alfabética A–Z por padrão** (`cfg.alpha`, ausente = ligado; collator pt-BR, sem acento/caixa; "Outros" sempre por último; vale na galeria, nos seletores e em Organizar categorias); a caixa "Ordem alfabética" do diálogo desliga e libera a ordem manual (`cfg.order`, setas ↑↓; ao desligar, `order` parte da ordem A–Z atual). `alpha` vai no `TPL_CATS_CFG` do `templates.js` (o Python preserva o dict inteiro). O item **Organizar categorias** do menu Gerenciar da galeria abre o diálogo (na visão em Blocos não há barra lateral); `openCats()`/`renderCats()` (diálogo "Organizar categorias"). Categoria removida do padrão só é escondida (`hidden`) e seus templates caem em "Outros" (`other`, que não pode ser removida); categoria criada pelo usuário tem id `c_…` e, ao ser removida, move os templates para "Outros" de vez.
- Ícones de categoria: chaves `c…` em `ICONS`; novas chaves entram também em `CAT_ICONS` para aparecerem no seletor.
- Layout do editor: grade `barra de ferramentas | tela | painel` ≥ 1181 px (painel mais estreito até 861 px); abaixo disso a página empilha (barra de cima, **canvas**, ferramentas na horizontal, paleta, painel); abaixo de 561 px a barra de cima fica em 2 linhas, o tema vai para o Menu e a galeria vira 2 colunas. Na **Montar** a barra de ferramentas, a paleta e as opções somem (só tela + painel de montagem).
- Cópia do `index.html` anterior a esta interface: `tools/backups/index-antes-da-nova-interface.html` (o app só apaga `templates-*.js` dessa pasta, então ele fica).

## 4. Regras que o usuário já deixou claras (leia antes de qualquer coisa)

1. **Padrões que já vêm em grade para hama beads → cópia EXATA.** Contorno preto, ruído e peças soltas ficam. Só saem: fundo liso e o que não é desenho (legenda de cores, marca d'água, réguas/numeração, molduras, título). Foi uma correção explícita ("pode pegar eles exatamente iguais ao que estou mandando").
2. **Nunca destruir detalhe interno** (olhos, braços, boca, estampas) ao "limpar". As rodadas de remoção automática de contorno/simetria/ligação de peças foram rejeitadas. **Não rode `polish`, `symmetrize`, `connect_components` nem `strip_*` em templates novos.** Eles só existem no pipeline antigo (remessas 1–4).
3. Quando o usuário diz "voltar como estava", restaure **byte a byte** as linhas anteriores. A versão que ele aprova é a que vale; não "melhore" sem pedir.
4. **Fotos de peças prontas não ficam exatas.** Converta pela grade de contas (§7.4) e diga ao usuário que é aproximado. Se o fundo/iluminação impedir um resultado reconhecível, **pule e avise** (foi o caso da foto do Natsu e do Eevee em placa transparente).
5. **Nunca baixe imagens da internet**; só as que o usuário colocou nas pastas `remessa N`.
6. Nomes de template: únicos no catálogo (o build ignora com `AVISO` um nome repetido) e descritivos. Quando não souber quem é o personagem, use um nome neutro (ex.: "Chibi de capacete de gato") e **liste os chutes** no relatório final. Se já existir um com o mesmo nome, use sufixo como "(padrão)", "(versão 2)", "(chibi)".
7. Mantenha texto de UI em pt-BR; valores de cor da paleta são ajustáveis pelo usuário no app ("Ajustar cores…").

## 5. Como o catálogo é montado

> **Fluxo atual (use este):** o `templates.js` é editado pelo usuário no app (Gravar no catálogo) e **acrescentado** por `python tools/add_templates.py tools/data/finalN.json` (cópia de segurança automática; respeita nomes, categorias e exclusões que o usuário já gravou). O `build_templates.py` abaixo **regenera tudo do zero** e só serve para recomeçar o catálogo: se o `templates.js` tiver `window.TPL_BAKED` ele **para** com uma mensagem, e só roda com `--force` (apagando o trabalho do usuário, com cópia em `tools/backups/`). Os `data/final*.json` continuam sendo o histórico das conversões.

### Regenerar do zero (`tools/build_templates.py`) — legado

`python tools/build_templates.py` **regenera `templates.js` inteiro**, em ordem:

1. `data/final1..6.json` (remessas 1–4, já com correções) → `fixes.json`/`fixes2.json` (trocas, renomeações, remoções) → `polish` (só pipeline antigo) → `fixes3.json` (redesenhos à mão e remoções a pedido do usuário) → simetria (lista fixa) → bloco `EXACT` (devolve versões que o usuário mandou voltar "como estavam").
2. Depois, um bloco por remessa nova: `final7.json` (remessa 5), `final8.json` (6), `final9.json` (7), `final10.json` (8), `final11.json` (9), `final12.json` (10). **Esses entram sem nenhum tratamento** e só se o nome ainda não existir.
3. `REGROUP`/`RENAME_GROUP` (reagrupa por nome exato) → ordena por `CATS` → escreve `templates.js`.

Correspondência: a remessa **N ≥ 5 vira `data/final{N+2}.json`** (a próxima, remessa 13, será `final15.json`). O build legado só conhece até `final12.json` (remessa 10); as remessas 11 em diante entram **só** por `add_templates.py`.

Reprodutibilidade (verificada ao criar este arquivo): rodar o build a partir de `tools/` reproduz `templates.js` **byte a byte**, e rodar `r5_exfinal.py … r10_exfinal.py` reproduz exatamente `final7…final12.json`. Antes de mexer, faça cópia de `templates.js`; depois do build compare (§8, passo 8).

Observações:
- `fixes3.json → remove` apaga **por nome** (só nas etapas antigas; os blocos `final7+` entram depois e não são afetados).
- As remessas 1–4 foram geradas por dezenas de scripts ad hoc (leitura de células, fotos, redesenhos à mão) que **não estão em `tools/`**; o resultado delas está congelado em `data/final1..6.json` + `fixes*.json`. Não tente regenerá-las.
- Não rode `tools/r5_final.py` nem `tools/r5_build.py` achando que atualizam o catálogo: são a 1ª passada (com limpeza) da remessa 5, substituída pela versão exata; as saídas deles vão para `tools/out/` e não entram no build. A remessa 5 oficial é `r5_exfinal.py` → `data/final7.json`.

## 6. Biblioteca de conversão (`tools/r6.py`, usa `r5.py`, `grid2.py`, `fitgrid.py`…)

Todos os scripts baseados em `r6` leem a pasta da remessa pela variável de ambiente **`REMNUM`** (Bash: `REMNUM=9 python …`; PowerShell: `$env:REMNUM='9'; python …`). O **índice** de uma imagem é a posição na lista **ordenada por nome de arquivo** da pasta (`glob` ordenado) — é o número que `src_sheet.py` mostra.

### 6.1 Conversão exata de padrões com grade: `r6.exact6(idx, …)`

Passos internos: carrega a imagem (compõe RGBA sobre branco) → **detecta a grade** (`grid2.detect`: espectro das bordas, passo fracionário, sub-pixel, inclui células parciais) → **amostra** cada célula (mediana do centro; ou cor dominante com `mode=True`) → remove o **fundo** (inundação a partir da borda) → **funde ruído de JPEG** (`snap`: cores a ≤ `dist` viram a mais comum do grupo, senão uma mesma cor lisa vira letras diferentes) → mapeia cada célula para uma letra (`mapc`) → aplica `drop`/`clear` → `trim` → `post`.

Parâmetros (todos opcionais):

| parâmetro | uso |
|---|---|
| `crop_img=(x0,y0,x1,y1)` | recorte **em pixels, antes** da detecção da grade (para tirar título/legenda/réguas de um gráfico) |
| `crop=(y0,y1,x0,x1)` | recorte **em células, depois** da amostragem (para tirar moldura, régua numerada, rodapé) |
| `clear=[(y0,y1,x0,x1),…]` | esvazia regiões (coordenadas de célula, depois de `crop`, antes do trim): marcas d'água, legendas pequenas |
| `px=22.0` ou `px=dict(px=,py=,ox=,oy=,W=,H=)` | força o passo da grade. Use quando a detecção travar no **meio** do passo (células com pontinhos/números) ou quando as células são **não quadradas** (use o dict) |
| `mode=True` | cor dominante da célula (ignora números/códigos desenhados dentro das células) |
| `tol=26`, `ref=(r,g,b)` | fundo = cor do canto (mediana dos 4 cantos), tolerância; `ref` força a cor |
| `thr=N` | fundo = "claro ligado à borda" (min(R,G,B) > N) |
| `achro=N` | fundo xadrez/cinza-claro **sem cor** (max−min ≤ 10 e min > N), ligado à borda — fundos "transparentes" de editores |
| `grad=14` | fundo em **degradê**: a inundação passa de célula em célula enquanto a cor muda menos que 14 |
| `darkbg=N` | fundo escuro (max(R,G,B) < N) |
| `bgs=[(ref,tol),…]` | mais fundos de cores diferentes (inundação adicional) |
| `allbg=True` | células com a cor do fundo que ficaram **fechadas dentro do desenho** (ex.: furo de um Ankh) também ficam vazias |
| `dist=16` | raio do `snap` (use ~24 quando uma marca d'água suja as cores) |
| `colmap=[((r,g,b),tol,'letra'),…]` | força uma letra para uma cor específica (override por imagem) |
| `drop='xy'` | letras que viram vazio depois do mapeamento |
| `post=fn(rows)` | pós-processamento (ex.: `largest` mantém só a maior peça) |

Outras funções: `sprite6(idx)` (PNG 1 pixel = 1 conta com alfa), `ring_render(idx, …)` (renders de contas redondas sobre pegboard escuro: conta preta × furo vazio pelo brilho do anel), `photo6(idx, p0, spread, bgfn, mapper, colmap, keepbg, check='arquivo.png', …)` (foto de peça pronta; §7.4), `flood_bg`/`flood_fn`/`snap`/`load_cells` (blocos usados pelas anteriores).

### 6.2 Fundos — qual opção usar

- Fundo de uma cor só (verde, rosa, cinza, bege…): padrão (cor do canto).
- Moldura/borda em volta (a cor do canto é a da moldura): `crop` para tirar a moldura e só então o padrão acha o fundo interno.
- Fundos aninhados (Inuyasha: lilás > cinza > branco): `crop` até o branco interno.
- **Cor do canto ambígua** (uma linha de moldura escura embaixo e fundo colorido em cima → a mediana dos 4 cantos sai errada e o fundo não é removido, como na garota de cabelo azul da remessa 10): recorte a linha da moldura com `crop` ou force `ref=(r,g,b)`.
- Fundo com **listras/trama** mais escura que o fundo (pegboard cinza): aumente `tol` (≈48) — o contorno preto do desenho evita vazamento — e/ou `post=r5.largest` para sobrar só a peça principal.
- Xadrez branco/cinza: `achro`. Degradê: `grad`. Imagem com vários painéis empilhados: `crop_img`/`crop` por painel, ou converter inteira e separar por linhas vazias (função `blocks()` em `r9_exfinal.py`).
- **Branco dentro do desenho que encosta no fundo branco não é distinguível**: armadura branca sem contorno fechado vira buraco. É inerente à fonte; não "conserte".

### 6.3 Cor: `r6.mapc(rgb)` (a regra atual, na ordem)

1. cinza puro (saturação < 0,08) → só entre `w i l m d k` por Lab (RGB-mais-próximo transformava cinza claro em lilás `x`);
2. claro com um pouco de cor (v ≥ 0,70 e s < 0,45: pele, lavanda, verde claro) → vizinho mais próximo em **Lab** na paleta inteira (bege em vez de rosa);
3. dourado vivo e claro (s ≥ 0,45, v ≥ 0,80, matiz 28–50°) → só `a y o`;
4. verde-água vivo (matiz 140–200°, v ≥ 0,85) → candidatos até 30° de matiz;
5. azul acinzentado (matiz 200–235°, s ≥ 0,35, v ≥ 0,45) → `b` (não roxo);
6. malva/roxo apagado (matiz 250–330°, s 0,20–0,45, v < 0,70) → `u v x`;
7. resto → `r5.hue_letter`: RGB mais próximo, **mas cores muito saturadas só podem virar paleta do mesmo matiz** (senão vermelho puro vira laranja e azul vira roxo); verde-limão cai em verde, não em amarelo.

Lições de cor: sempre `snap` antes de mapear; Lab sozinho põe vermelho vivo em laranja; RGB sozinho põe cinza claro em lilás; **vermelho puro muito saturado (ex.: 244,40,15) vira laranja `o`** (o Lab acha o laranja mais perto que o `F5`): use `colmap=[((244,40,15),30,'r')]` na imagem (o `mapc` não foi alterado de propósito, para manter `final8…final12.json` reprodutíveis); marrom/tan fica ambíguo (G5 `t` vs âmbar `a` — foi decidido caso a caso: lobo da remessa 6 em `a`, Pou em `t`); azul-marinho vira `u` ou `b`; turquesa vira `g`/`h` (decidido à mão no Shiryu). Ao fazer uma escolha subjetiva de cor, **diga qual foi** no relatório e que dá para ajustar no editor.

Lições da remessa 11: (a) **marca d'água translúcida** clareia algumas células e o `snap` as funde com o branco (pele creme virava branco): use `dist` pequeno (3) e `colmap` com tolerância 4 nos tons creme; (b) pele creme (255,239,223 / 252,243,236) cai em `w` pela regra do cinza: mande para `s` com `colmap`; (c) **marrom escuro/oliva** (79,58,23) caía em `t` (salmão, mais claro e rosado): mande para `n`; pele **oliva** (148,131,79) não tem par na paleta e o âmbar fica laranja demais, então foi tudo para `n` (G7); (d) vários tons do gráfico (os vermelhos F15/F7/F19; o amarelo-oliva do cabelo do gráfico 3) viram a mesma letra: quando o sombreado importa, use `colmap` para mandar o tom escuro a outra letra (no gráfico 3 o oliva escuro foi para `a`); (e) o `clear=` usa coordenadas **antes do trim** (o índice da linha muda), então para apagar uma assinatura de painel é mais seguro limpar as células depois da conversão; (f) painéis com vários personagens: `cblocks` por colunas vazias e `rsplit` por linha vazia.

Lições da remessa 12: (a) **o preview (`render_flat`) desenha xadrez para "vazio", então um fundo xadrez cinza/branco que NÃO foi removido parece transparente**: depois de converter, varra as bordas de cada molde procurando letras alternadas tipo `ililil` (a Anya chibi veio com o xadrez de um editor; o conserto foi `crop` da moldura cinza + `achro=190`); (b) em `exact6`, **`clear` é inclusivo** (`y0<=y<=y1`) e usa coordenadas da grade **antes do trim**; (c) para **não** remover o fundo (desenho em negativo, fundo preto que é parte do desenho) passe `ref=(0,255,0), tol=1`; (d) régua numerada ao redor do gráfico impede a remoção do fundo branco: recorte com `crop=(1,H+1,1,W+1)`; fundo colorido sem inundação: `ref=(r,g,b), tol=40, allbg=True` (o `allbg` esvazia o miolo de letras como o "O" do OK); (e) captura do Photoshop com fundo xadrez cinza: `crop_img` sem a régua + `achro=100`; (f) pixel art em **ponto-cruz** (textura de fio): `mode=True` e `ref` do fundo com `tol` ~45; marrom-oliva escuro caía em laranja (mande para `k`/`n`); (g) amarelo-limão (234,238,127) cai em verde-menta: force `y` com `colmap`; (h) marca d'água e assinatura fora do desenho: `post=r5.largest` quando o desenho é uma peça só (veja se as tentáculos/partes soltas do desenho não somem); (i) o **ruído de borda** da imagem pode virar uma linha de contas soltas na última linha (`post=lambda r: r[:-1]`).

## 7. Casos especiais

7.1 **Gráficos numerados/com legenda** (Mimikyu, Yami Yugi, Gojo roxo): cortar para a grade (`crop_img`), forçar o passo (`px`; dict se as células forem não quadradas), `mode=True`. A legenda de cores da própria imagem ajuda a conferir as cores.

7.2 **Sprites 1 pixel = 1 conta** (PNG pequeno com alfa): `sprite6`.

7.3 **Renders de contas redondas sobre pegboard preto** (Cavaleiro de Ouro): `ring_render` — conta preta sólida (anel escuro) vira `k`; furo vazio (anel cinza) vira vazio.

7.4 **Fotos de peças prontas** (aproximado!): `photo6` ajusta ângulo/passo/deslocamento da grade de contas (`fitgrid.fit`) dentro da imagem e amostra o **anel** de cada conta (o centro tem o furo). **Confirme o passo antes de confiar**: em foto sobre placa o passo detectado costuma ser o **dobro ou a metade** do real (pinos × contas). Use `check='x.png'` para gerar a imagem com a grade desenhada e olhe; estime o passo por autocorrelação ou medindo contas num recorte ampliado. Fundo: função `bgfn(cor)` (parede clara, madeira, placa transparente…) + inundação a partir da borda; em placa transparente/mesa escura isso é pouco confiável — uma alternativa é uma **lista branca de matizes** do desenho (`keepbg=True`, tudo que não é desenho vira vazio, como no Mimikyu (foto)). Limpe cinzas/sombras residuais com um mapa de letras (`post`). Se não ficar reconhecível, não inclua.

7.4b **Fotos: método que funcionou (`tools/photo7.py`, usado em `r_outros.py`)**: (1) estime o passo com autocorrelação do gradiente (`scratchpad`-style: período dominante em x e y numa caixa só com o desenho) e dê `bbox=(x0,y0,x1,y1)` **só em volta da peça** (a placa transparente tem pinos de mesmo passo e engana o ajuste); (2) rode `photo7.py REM IDX P0 SPREAD bbox K` para ver o passo achado e os K grupos de cor; grave a imagem da grade (`check=`) e **olhe se as linhas caem entre as contas** — fase errada = conversão cheia de contas trocadas; (3) escolha o fundo: `bg=fn(rgb)` (ou `fn(rgb,y,x)` para regras por posição) com inundação a partir da borda, `flood=False` quando o desenho nunca tem a cor do fundo e o fundo aparece em ilhas (entre braços/pernas), ou lista branca `keep=`; (4) dê uma **paleta explícita** `pal=[((r,g,b),'letra'),…]` com os centros dos grupos (resultado reprodutível e você decide marrom×salmão, lavanda×roxo…). **Fotos sobre placa transparente com contas brancas, com perspectiva ou desfocadas** (violão, Stormtrooper, Cyndaquil, Excalibur, 3 personagens do Bob Esponja, asas, menina de cabelo branco) **não ficaram reconhecíveis**: não entraram.
7.4c **Gráfico/captura pequeno e borrado (JPEG de 8 px por célula, ex.: folha das 9 Eeveelutions, remessa 5 img 7): a fase da grade decide tudo.** Ajuste `px`, `ox`, `oy` pela imagem inteira (busca fina de 0,005 px: um erro de 0,05 px por célula já desloca 1 célula em ~20) e confira desenhando as linhas por cima do recorte ampliado; com a fase certa o ruído some. Fundo cinza da grade: `ref=` com `tol` pequeno (14) para não comer o corpo cinza-escuro do Umbreon; manchas cinza que sobram (cruzamentos da grade) saem com `replace('d','.')` em cada sprite, `drop_specks` e `fill_holes` (buracos cercados). O corte 3×3 fixo é mais seguro que `groups()` quando há pontinhos soltos ligando os sprites.

7.5 **Imagem que é cópia de outra remessa**: compare o MD5 dos arquivos (o resumo do §8 passo 1 faz isso); não duplique.

## 8. Passo a passo para uma remessa nova (N)

1. **Listar e classificar.** Conferir quantas imagens, tamanhos e **duplicatas por MD5** contra as remessas anteriores (a mesma arte em outro arquivo passa pelo MD5: depois de converter rode `python tools/dupcheck.py tools/data/finalN.json` — ~0,99 = mesma arte, não inclua). Gerar folhas de contato numeradas e olhar:
   `python tools/src_sheet.py N 0 24` → `tools/out/src_N_0.png` (24 por folha; repita `24 48`…). O número mostrado em cada miniatura é o **índice**. Classifique cada uma: padrão com grade / sprite / render / foto de peça pronta / painel múltiplo / duplicata.
2. **Primeira passada automática** de todos os padrões: `REMNUM=N python tools/r6_try.py tag 0 1 2 …` → `tools/out/r6_try_tag.png` (título = `índice colunasxlinhas pN`, onde `pN` = nº de peças soltas). Olhe a imagem.
3. **Diagnosticar cada problema** (moldura, régua, legenda, fundo que não saiu, passo errado, marca d'água):
   - `REMNUM=N python tools/r6_dump.py idx [rows="(a,b)"] [cols="(a,b)"] [px=…] [crop_img="(x0,y0,x1,y1)"] [mode=True]` imprime a grade de letras **com índices de linha/coluna**, para escolher `crop`/`clear`;
   - `REMNUM=N python tools/colors.py idx [crop_img=…] [px=…]` lista as cores mais comuns e a letra que cada uma vira (para decidir `colmap`);
   - **gráficos numerados com legenda** (a detecção acha metade do passo por causa dos códigos nas células): `python tools/gridlines.py "remessa N/arq" x0 y0 x1 y1` numa faixa de células vazias dá a posição das linhas da grade → monte `px=dict(px,py,ox,oy,W,H)` + `mode=True` (veja `G3`, `G7`, `G13` em `r11_exfinal.py`);
   - para olhar o original ampliado, recorte/redimensione com Pillow e abra a PNG.
4. **Escrever `tools/rN_exfinal.py`** copiando `tools/r12_exfinal.py` (a mais recente, com imagens de várias origens; a `r11_exfinal.py` tem os painéis divididos e tem exemplos de `cblocks`, painel dividido em personagens (`slam()`), `colmap`, `clear`, gráficos numerados com passo forçado e `post`): ajuste `os.environ['REMNUM']`, a lista `CFG = [(nome, série, lambda: E(idx, …)), …]` e o arquivo de saída `data/final{N+2}.json`. A **série é o nome da franquia** (ex.: `'Naruto'`, `'Pokémon'`, `'Winx'`); use o nome que já existe quando houver (veja `franchises.py`); só use uma série genérica (`'Outros animes'`…) para o que não for identificado. Rodar: `python tools/rN_exfinal.py` (aceita nomes parciais como filtro) → grava o JSON e as prévias `tools/out/rN_x_*.png`. **Olhe as prévias**, uma a uma, comparando com a fonte, e itere.
5. **Nomear.** O 2º item da tupla ("série") = franquia/categoria; franquia nova cria categoria nova sozinha (se quiser ícone/nome/ordem específicos, acrescente em `tools/franchises.py` → `CATEGORIES`/`GROUP_MAP` antes de rodar). O que você não identificar vai com um nome genérico ("Outros animes", "Outros jogos"…) e cai em "Outros". Nomes únicos (§4.6).
6. **Integrar no catálogo.** `python tools/add_templates.py tools/data/final{N+2}.json --dry` mostra o que entraria (nomes repetidos e excluídos pelo usuário são pulados, nome genérico vai para "Outros"); sem `--dry` ele grava o `templates.js` (cópia de segurança automática em `tools/backups/`). Franquia nova: a categoria é criada pelo script (veja o passo 5). Não rode `build_templates.py` (veja §5). A saída deve mostrar `acrescentados: <n>` igual ao número de templates da remessa, `pulados: 0` (ou só os que você espera).
7. **Cache do navegador:** o `templates.js` é carregado por um pequeno script no `index.html` que usa `var b='AAAAMMDDx'` como versão; aumente esse valor (ex.: `20261025d` → `20261025e`) sempre que o `templates.js` mudar **fora do app** (add_templates, build). Quando o app grava o arquivo ele mesmo, o carimbo local é atualizado sozinho.
8. **Verificar.**
   - `node --check templates.js`;
   - os templates antigos continuam idênticos (compare por id contra o backup: mesmas linhas/nome/categoria) e os novos têm linhas do mesmo comprimento;
   - **teste no navegador:** crie temporariamente `.claude/launch.json` com `{"version":"0.0.1","configurations":[{"name":"beads","runtimeExecutable":"python","runtimeArgs":["-m","http.server","8765"],"port":8765}]}`, abra `http://localhost:8765`, confira `window.TEMPLATES.length`, busque um template novo na galeria (`#tplSearch`), abra-o e leia `S.w/S.h`; sem erros no console. Ao terminar: `localStorage.clear()` nessa origem, pare o servidor e **apague a pasta `.claude`**.
9. **Registrar**: acrescente a remessa na tabela do §10 deste arquivo e atualize a memória do agente, se houver.
10. **Relatório ao usuário (pt-BR):** quantos entraram e o total; o que entrou por categoria; o que foi pulado e por quê; **nomes que foram chute**; compromissos de cor; avisar para recarregar com Ctrl+F5.

## 9. Ajustes, nomes, categorias e exclusões que o usuário faz no app

O usuário edita desenhos, renomeia, move entre categorias, cria/remove categorias e exclui templates na própria galeria. Isso fica guardado no navegador dele (localStorage) até ele clicar em **Moldes → Gerenciar → Gravar no catálogo** (também em Menu → Gravar no catálogo). O botão mostra quantas alterações estão pendentes.

- **Chrome/Edge:** o app usa a File System Access API: na primeira vez o navegador pede a **pasta do projeto** (a que tem `index.html` e `templates.js`); a pasta fica lembrada (IndexedDB). O app copia o `templates.js` atual para `tools/backups/templates-AAAAMMDD-HHMMSS.js`, grava o novo, confere lendo de volta e limpa do navegador o que foi gravado. Se não conseguir copiar o backup, **não grava**.
- **Outros navegadores:** o app baixa o `templates.js` novo e pede para o usuário trocar o arquivo da pasta; depois ele clica em "Já troquei o arquivo".
- O que é gravado: templates do catálogo com nome/categoria (e `group` = nome da categoria) e desenhos ajustados já aplicados (ids preservados), os templates "meus" viram templates normais (id novo a partir do nome), excluídos saem do arquivo e seus nomes vão para `TPL_REMOVED`, e a organização de categorias vai para `TPL_CATS_CFG`. Dá para recomeçar de um backup copiando-o de volta para `templates.js`.
- O código está em `index.html` (`buildBaked`, `catalogueText`, `getProjDir`, `writeCatalogue`, `applyBaked`, `openBake`) e o formato é lido/escrito igualmente por `tools/tplfile.py` (verificado: o arquivo gravado pelo app é lido pelo Python e reproduzido igual).
- O botão exportar/importar (`meus-templates-bead-studio.json`, v2: `edits`, `placed`, `cats`, `deleted`, `mine`) continua existindo para levar o que está só no navegador para **outro** navegador. Se o usuário mandar esse JSON em vez de gravar pelo app, aplique-o importando no app (Menu → Importar moldes e ajustes…) e usando "Gravar no catálogo", em vez de mexer no `templates.js` à mão.
- **Página aberta com catálogo velho (acidente de 2026-10-26):** o app grava `window.TEMPLATES` como estava quando a página abriu; se o usuário clicar em "Gravar no catálogo" numa página aberta ANTES de você acrescentar uma remessa, os moldes novos somem do arquivo (os 34 da remessa 12 sumiram assim; a cópia de antes está em `tools/backups/`). **Trava no app:** `writeCatalogue` lê o arquivo do disco e, se ele tiver ids que a página não carregou (`tplLoadedIds`), **não grava** e mostra "Recarregue a página (Ctrl+F5)" (`STALE`). Mesmo assim, **depois de cada remessa** (1) aumente `var b` no `index.html` (também ao recuperar/regravar o arquivo por fora), (2) diga ao usuário para **recarregar com Ctrl+F5** e (3) **confira nas próximas conversas se o `templates.js` ainda tem os moldes** (compare os ids com o backup mais recente de `tools/backups/`) antes de supor que a remessa está lá. Para recuperar: `python tools/add_templates.py tools/data/finalN.json` (acrescenta só o que falta; `--readd` recoloca também o que o usuário excluiu — use só quando ele pedir).
- Nunca sobrescreva o `templates.js` com o `build_templates.py` sem avisar: apagaria o trabalho do usuário. Pergunte antes de remover algo do catálogo.

## 10. Registro das remessas

| Remessa | Imagens | Entraram | Total | Fonte dos dados | Observações |
|---|---|---|---|---|---|
| 1–4 | ~146 | 145 (depois 135, após exclusões e redesenhos pedidos) | 135 | `data/final1..6.json`, `fixes*.json` | pipeline antigo (com polimento); congelado |
| 5 | 45 | 40 | 175 | `final7.json` (`r5_exfinal.py`) | convertida **exata** depois da correção do usuário; fotos por grade de contas; pulados: Eevee em pegboard, folha de Eeveelutions, foto do Bob Esponja, foto do Togepi, foto do Grogu |
| 6 | 48 | 47 | 222 | `final8.json` (`r6_exfinal.py`) | pulada: duplicata do Homem de Ferro; foto do Natsu não reproduzível; foto do Mimikyu entrou aproximada |
| 7 | 40 | 42 | 264 | `final9.json` (`r7_exfinal.py`) | 3 faces das Meninas Superpoderosas separadas de 1 imagem; Okarun (render com marca d'água); Visão (foto aproximada) |
| 8 | 24 | 24 | 288 | `final10.json` (`r8_exfinal.py`) | gráficos numerados; Lelouch gatinho 91×142 |
| 9 | 7 | 9 | 297 | `final11.json` (`r9_exfinal.py`) | pilha Charmander/Charmeleon/Charizard separada em 3 |
| 10 | 29 | 30 | 327 | `final12.json` (`r10_exfinal.py`) | puladas 2 duplicatas por MD5 (máscara Hollow da remessa 2 e `togepi.png` da remessa 5); Judy/Nick separados por colunas vazias; 2 painéis de galinhas e 2 de carros separados por `crop`; gráficos com régua/legenda recortados |
| 11 | 17 | 24 | 351 | `final13.json` (`r11_exfinal.py`) | puladas 3: 2 duplicatas por MD5 (Reborn da remessa 3 e Sasuke chibi da remessa 7) e o Naruto de corpo inteiro (mesma arte de "Naruto (corpo inteiro)", 99% das contas iguais); 3 gráficos numerados (passo forçado), painel de **Slam Dunk** dividido em 5 personagens + bola (assinatura "ADAPT BY ZMOMO" apagada), painel do **Soul Eater** dividido em 4 chibis + lua + emblema, 3 Sakuras (marcas d'água removidas); categoria nova "Slam Dunk" |
| 12 | 35 | 35 | 386 | `final14.json` (`r12_exfinal.py`) | puladas 2 duplicatas por MD5, mas o **Reborn foi refeito** a pedido do usuário (ele tinha excluído a versão antiga; entra com `--readd`, `crop_img=(19,18,379,378), px=8.0`) e a Mona Lisa só entrou depois, no levantamento "Outros"; `dupcheck.py` não achou cópias por conteúdo. 7 alienígenas do Ben 10, Saitama 80×100 (One Punch Man), 2 Anyas (uma em **negativo**, com o fundo preto mantido porque a roupa é do mesmo preto), 2 Levis de limpeza (contorno e ponto-cruz), 2 "malhas" de retratos fotográficos de pessoas (nomes neutros), capturas de editor com régua/moldura recortadas; 5 categorias novas (One Punch Man, Spy x Family, The Last of Us, Resident Evil, Scott Pilgrim). **Acidente:** a remessa foi apagada do arquivo quando o usuário gravou pelo app com a página aberta antes dela (ver §9); recuperada com `add_templates.py final14.json --readd` |
| Outros | 12 pastas | 70 (+1 de 1 placa) | 451 | `final_outros.json` (`r_outros.py`) | **levantamento pedido pelo usuário (2026-10-26)**: "passar por todas as pastas, ver o que não está no catálogo e fazer todas que forem possíveis, na categoria Outros, fielmente". Triagem com `triage.py 1..4` (+ conferência lado a lado com `layoutsim`). Entraram em **Outros** (série `'Outros'`, `add_templates.py --readd` porque 37 nomes estavam em `TPL_REMOVED`): 20 conversões exatas que já existiam de remessas 5–12 e que o usuário tinha excluído ou que nunca entraram (`data/outros_pool.json`), gráficos que faltavam (remessas 1–4, 12: Pintinho, Smiley do Red John, Dragonair, Luffy, Batman, Flash, gato siamês, menino pescador, Kakashi, Naruto, Kazuma v2, Mona Lisa, Asas da Liberdade em gráfico, 8 insígnias de Kanto, Pikachu na Poké Ball), as **9 Eeveelutions** (folha 84×80 recortada em 3×3) e 17 **fotos de peças prontas** aproximadas (Ulquiorra de corpo inteiro, Capitão América, Gavião Arqueiro/Capitão do quarteto, Pantera Cor-de-Rosa, Perry, Stitch na mão, Yami Yugi de contas grandes, Natsu, 2 chaveiros, Caveira de Luffy, 2 Togepis, Bob Esponja, monstrinho marrom…). **Pulados por já estarem no catálogo** (conferido lado a lado): Cowboy RDR, chibi de jaqueta azul e faixa verde, Asas em foto (já há a versão em gráfico), Seiya em foto (mesma arte do gráfico), Goku em foto (parece a peça pronta do "Goku (chibi pixel)"; não conferido contas a contas), Grogu e fotos de foice e martelo / maneki neko (mesma arte). **Fotos que NÃO ficaram reconhecíveis e não entraram** (placa transparente com contas brancas, perspectiva, desfoque): violão, Stormtrooper, Cyndaquil, Excalibur, 3 personagens do Bob Esponja, asas de anjo com bolinha marrom, menina de cabelo branco, Renji em foto, cobra, criatura de chapéu de palha, Quebra-cabeça do Milênio, pato de borracha, Eevee em render gigante (r5 #33) — ver §7.4b. |

**Reorganização por franquia (2026-10-25, a pedido do usuário):** o usuário já tinha usado "Gravar no catálogo" (297 templates: excluiu 31 da remessa 10 e anteriores, ajustou desenhos e criou "Percy Jackson (chibi)"), então a reorganização foi feita **sobre o `templates.js` dele** por `tools/reorganize.py` (backup em `tools/backups/`; nenhum nome ou desenho mudou). Resultado: 82 categorias (80 franquias + Brincos + Outros); 50 templates ficaram em "Outros" (animais, formas, "Chibi de …", criações do Claude…) para o usuário ajustar. Franquias identificadas pelo nome (e que o usuário pode corrigir): Rem (Re:Zero), Asta (Black Clover), Okarun (Dan Da Dan), Rimuru (Tensura), Koro-sensei, Kaneki, Frieren, Kaiju nº 8, Soul Eater, Lavi/Allen (D.Gray-man), Vash (Trigun), Deku/Todoroki (My Hero Academia), Natsu/Fairy Tail, Marvel (Groot, Wanda, Homem-Aranha, Deadpool, Homem de Ferro, Hulk, Wolverine, Visão) e DC (Lanterna Verde, Batman, Superman), Lilo & Stitch (todos os Stitch/Angel), Zootopia, Carros, Ratatouille, Ursinho Pooh, Peter Pan (Sininho), Egito Antigo e Religião (temas).

Séries criadas ao longo do caminho (antes da reorganização): Dragon Ball, Studio Ghibli, Turma da Mônica, Cavaleiros do Zodíaco, Hunter x Hunter, Meninas Superpoderosas, Winx, Yu-Gi-Oh.

## 11. Armadilhas do ambiente (Windows)

- Ao escrever scripts Python que contenham **caminhos Windows com `\`**, use a ferramenta de escrita de arquivo (Write), não `python - <<EOF` no Bash: a ferramenta colapsa `\\` e quebra literais/regex (`\U` vira erro de unicode). Se precisar de `\` num heredoc, construa com `chr(92)`. Idem para `sed -i` em linhas com `\`.
- O diretório de trabalho do shell volta para a raiz do projeto a cada chamada; use caminhos absolutos ou `cd` dentro do mesmo comando.
- Capturas de tela do navegador embutido podem estourar o tempo com o painel oculto; use `javascript_exec`/`get_page_text` para inspecionar.
- `REMNUM` precisa estar definida em **cada** comando que usa `r6`, `r6_try`, `r6_dump`, `colors` ou os `rN_exfinal` (o `src_sheet` recebe a remessa como argumento; os `rN_exfinal` já definem a sua).
- O build e todos os scripts escrevem prévias em `tools/out/`; nunca deixe PNGs soltos na raiz do projeto.
