"""Categorias e séries do catálogo (a ordem aqui é a ordem na galeria).

Usada por build_templates.py (regenerar tudo, só para recomeçar do zero) e por add_templates.py (acrescentar uma remessa
nova ao templates.js sem apagar o que o usuário editou no app).
Uma série nova de uma remessa precisa aparecer aqui, na categoria certa.
"""
CATS = [
    ('anime', 'Animes e mangás', ['Naruto', 'One Piece', 'Attack on Titan', 'Dragon Ball', 'Demon Slayer', 'Hitman Reborn', 'Fullmetal Alchemist',
                                   'Code Geass', 'KonoSuba', 'Jujutsu Kaisen', 'Bleach', 'Cavaleiros do Zodíaco', 'Hunter x Hunter', 'Yu-Gi-Oh', 'Outros animes']),
    ('games', 'Jogos', ['Pokémon', 'Mario', 'Skyrim', 'Red Dead Redemption', "Assassin's Creed", 'Outros jogos']),
    ('heroes', 'Super-heróis', ['Super-heróis']),
    ('cinema', 'Filmes e séries', ['Harry Potter', 'Star Wars', 'Studio Ghibli', 'Chaves e Chapolin', 'O Mentalista', 'Outros filmes e séries']),
    ('toons', 'Desenhos e infantil', ['Disney', 'Hello Kitty', 'Minions', 'Bob Esponja', 'Avatar', 'Como Treinar o seu Dragão', 'Hora de Aventura', 'Phineas e Ferb', 'Looney Tunes', 'Turma da Mônica', 'Meninas Superpoderosas', 'Winx', 'Outros desenhos']),
    ('animals', 'Animais e gatos', ['Gatos', 'Animais']),
    ('symbols', 'Símbolos e objetos', ['Símbolos e objetos']),
    ('earrings', 'Brincos', ['Brincos']),
    ('claude', 'Criações do Claude', ['Bichinhos', 'Comidinhas', 'Formas e céu']),
    ('other', 'Outros', ['Outros']),
]
