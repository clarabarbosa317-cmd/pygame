# 🦖 DinoWars - Jogo Cooperativo de Plataforma

<div align="center">

**Um jogo de plataforma cooperativo onde dois dinossauros devem trabalhar juntos para escapar!**

🎮 2 Jogadores | 🎨 6 Níveis | 🎵 Áudio Dinâmico | ⏱️ Desafio contra o tempo

</div>

---

## 📖 Sobre o Jogo

**DinoWars** é um jogo de plataforma cooperativo local para 2 jogadores onde você controla dois dinossauros (vermelho e azul) que precisam trabalhar em equipe para superar obstáculos, evitar armadilhas mortais e alcançar os portais mágicos antes que o tempo acabe!

### 🌟 Características Principais

- ✅ **Cooperação obrigatória**: Ambos os jogadores devem chegar aos seus portais
- ✅ **Mecânica de cores**: Cada dinossauro só pode pisar em plataformas da sua cor
- ✅ **6 níveis desafiadores**: Da tutorial ao desafio final
- ✅ **Inimigos móveis**: Meteoros com comportamentos únicos nos níveis finais
- ✅ **Sistema de áudio imersivo**: Música ambiente dinâmica e efeitos sonoros
- ✅ **Física de plataforma**: Rampas, saltos e gravidade realista
- ✅ **Temporizador por fase**: Corrida contra o tempo com dificuldade crescente
- ✅ **Tutorial interativo**: Aprenda as mecânicas antes de jogar

---

## 🎮 Como Jogar

### Objetivo
Cada jogador deve levar seu dinossauro até o portal da sua cor antes que o tempo acabe. Trabalhem juntos para superar os obstáculos!

### Regras Importantes
- 🔴 **Dinossauro Vermelho**: Só pode pisar em plataformas **vermelhas** e **neutras**
- 🔵 **Dinossauro Azul**: Só pode pisar em plataformas **azuis** e **neutras**
- ⚠️ **Espinhos matam**: Colidir com espinhos causa respawn instantâneo
- ☄️ **Inimigos matam**: Tocar em meteoros causa respawn instantâneo (níveis 5-6)
- ✨ **Ambos devem chegar**: Os dois jogadores precisam entrar nos portais
- ⏰ **Cuidado com o tempo**: Cada nível tem um limite de tempo

---

## 🎹 Controles

### Jogador 1 (Dinossauro Vermelho 🔴)
- **A** - Mover para esquerda
- **D** - Mover para direita
- **W** - Pular

### Jogador 2 (Dinossauro Azul 🔵)
- **← (Seta Esquerda)** - Mover para esquerda
- **→ (Seta Direita)** - Mover para direita
- **↑ (Seta Cima)** - Pular

### Controles Gerais
- **ESC ou P** - Pausar o jogo
- **R** - Reiniciar o nível (durante pausa)
- **Q** - Voltar ao menu (durante pausa)

---

## 📦 Instalação e Execução

### Requisitos
- Python 3.7 ou superior
- Pygame 2.0+
- NumPy 1.20+

### Instalação

1. **Clone o repositório**:
```bash
git clone https://github.com/seu-usuario/pygame.git
cd pygame
```

2. **Instale as dependências**:
```bash
pip install pygame numpy
```

### Executar o Jogo

```bash
python src/jogo.py
```

ou

```bash
cd src
python jogo.py
```

---

## 🗺️ Níveis

| Nível | Nome | Tempo | Inimigos | Dificuldade |
|-------|------|-------|----------|-------------|
| 1 | **Primeiros Passos** | 45s | - | ⭐ Tutorial |
| 2 | **Plataformas Coloridas** | 60s | - | ⭐⭐ Fácil |
| 3 | **Campo Minado** | 75s | - | ⭐⭐⭐ Médio |
| 4 | **Saltos Precisos** | 80s | - | ⭐⭐⭐ Médio |
| 5 | **Corrida Contra o Tempo** | 70s | 5 ☄️ | ⭐⭐⭐⭐ Difícil |
| 6 | **Desafio Final** | 90s | 8 ☄️ | ⭐⭐⭐⭐⭐ Muito Difícil |

### 💡 Dicas
- 🤝 **Comunique-se**: Cooperação é essencial!
- 👀 **Planeje antes**: Observe o nível antes de agir
- ⚡ **Cuidado com o tempo**: Nível 5 é especialmente rápido
- 🔄 **Pratique**: Cada morte é uma oportunidade de aprender
- ☄️ **Observe os padrões**: Todos os inimigos têm movimentos previsíveis
- 💡 **Aviso visual**: Meteoros cadentes piscam antes de cair!

---

## 🎵 Sistema de Áudio

O jogo possui um sistema de áudio procedural completo:

### Efeitos Sonoros
- 🔊 **Pulo**: Som ascendente ao pular
- 🔊 **Pousar**: Som ao aterrissar
- 💀 **Morte**: Efeito dramático ao morrer
- 🎉 **Vitória**: Fanfarra ao completar nível
- 😢 **Derrota**: Som triste quando o tempo acaba

### Música Ambiente
A música muda dinamicamente baseada no nível:
- **Fases 1-2**: Música calma e relaxante (aprendizado)
- **Fases 3-4**: Música animada e energética (ação)
- **Fases 5-6**: Música tensa e urgente (desafio)

> 💡 **Nota**: Todos os sons são gerados proceduralmente usando NumPy - não há arquivos de áudio!

---

## 🎨 Mecânicas do Jogo

### Plataformas e Obstáculos
- **Normais** (cinza): Qualquer dinossauro pode usar
- **Vermelhas**: Apenas o dinossauro vermelho
- **Azuis**: Apenas o dinossauro azul
- **Rampas**: Permitem movimentos diagonais
- **Espinhos**: Matam instantaneamente
- **Meteoros**: Inimigos móveis que matam ao tocar (níveis 5-6)

### Física
- **Gravidade realista**: Os dinossauros caem naturalmente
- **Momentum**: Movimento suave e responsivo
- **Salto variável**: Altura baseada no tempo pressionado
- **Colisão precisa**: Sistema de hitbox pixel-perfect

### Portais
- 🔴 **Portal Vermelho**: Objetivo do jogador vermelho
- 🔵 **Portal Azul**: Objetivo do jogador azul
- ✨ **Animados**: Efeito visual atraente
- ⚡ **Simultâneos**: Ambos devem entrar para vencer

### Inimigos (Níveis 5-6)
Os níveis finais incluem inimigos móveis que aumentam o desafio:

#### ☄️ **Meteoro Patrulheiro (M)**
- **Comportamento**: Patrulha horizontal entre dois pontos
- **Perigo**: Movimento constante e previsível
- **Estratégia**: Observe o padrão e passe quando ele estiver longe
- **Onde**: Nível 5 (3x) e Nível 6 (4x)

#### 💥 **Meteoro Cadente (F)**
- **Comportamento**: Fica no teto e cai em intervalos regulares
- **Aviso**: Pisca 0.5 segundos antes de cair!
- **Estratégia**: Corra durante o aviso ou espere cair para passar
- **Onde**: Nível 5 (1x) e Nível 6 (2x)

#### 🦅 **Patrulha Vertical (V)**
- **Comportamento**: Voa para cima e para baixo
- **Perigo**: Bloqueia áreas específicas
- **Estratégia**: Timing perfeito de pulo
- **Onde**: Nível 5 (1x) e Nível 6 (1x)

> ⚠️ **Atenção**: Qualquer contato com inimigos causa morte instantânea e respawn!

---

## 🛠️ Estrutura do Projeto

```
pygame/
├── assets/
│   └── img/                    # Sprites e texturas
│       ├── dino_vermelho.png
│       ├── dino_azul.png
│       ├── tile_*.png
│       ├── portal_*.png
│       └── fase*.png
├── levels/                     # Arquivos dos níveis
│   ├── level1.txt
│   ├── level2.txt
│   └── ...
├── src/                        # Código fonte
│   ├── jogo.py                # Loop principal
│   ├── sprites.py             # Classes de sprites
│   ├── level.py               # Carregamento de níveis
│   ├── menu.py                # Menu principal
│   ├── tutorial.py            # Tela de tutorial
│   ├── assets.py              # Carregamento de assets
│   └── settings.py            # Configurações do jogo
└── README.md
```

---

## 🎯 Recursos Técnicos

### Gráficos
- **Sprites animados**: Animação fluida dos dinossauros
- **Tiles texturizados**: Variedade visual nos cenários
- **Backgrounds por fase**: Ambientação única para cada nível
- **Efeitos visuais**: Portais animados, parallax

### Audio
- **Geração procedural**: Sons criados matematicamente
- **Música adaptativa**: Muda conforme o nível
- **Mixagem inteligente**: Canais separados para música e efeitos
- **Controle de volume**: Sistema ajustável

### Gameplay
- **Física de plataforma**: Gravidade, momentum, colisões
- **Sistema de spawn**: Respawn instantâneo ao morrer
- **Temporizador dinâmico**: Cores mudam conforme urgência
- **Menu de pausa**: Sistema completo com opções

---

## 👥 Créditos

### Desenvolvedores
- **Clara Barbosa**
- **João Pedro Zaltron**
- **Maria Clara Dragone**

### Tecnologias Utilizadas
- **Python 3** - Linguagem de programação
- **Pygame** - Framework de jogos
- **NumPy** - Geração de áudio procedural

### Ferramentas
- **Visual Studio Code** - IDE
- **Git** - Controle de versão

---

## 📝 Changelog

### Versão Atual
- ✅ 6 níveis completos
- ✅ Sistema de inimigos móveis (3 tipos)
- ✅ Sistema de áudio completo
- ✅ Tutorial interativo
- ✅ Menu principal com opções
- ✅ Sistema de cores e plataformas
- ✅ Temporizador por fase
- ✅ Menu de pausa
- ✅ Backgrounds por fase

---

## 🤝 Como Contribuir

Contribuições são bem-vindas! Sinta-se à vontade para:

1. 🐛 Reportar bugs
2. 💡 Sugerir novas funcionalidades
3. 🎨 Adicionar novos assets
4. 🗺️ Criar novos níveis
5. 📖 Melhorar a documentação

---

## 📜 Licença

Este projeto foi desenvolvido como parte de um projeto acadêmico.

---

## 🎮 Divirta-se!

<div align="center">

**Prepare-se para o desafio cooperativo mais emocionante com dinossauros!**

🦖🦖

</div>
