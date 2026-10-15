<div align="center">

<img src="packaging/icon.png" alt="Ícone do Olympus" width="128">

# Olympus

**God of War: Chains of Olympus (PSP), recompilado para rodar nativamente no seu computador e celular.**

[![Status](https://img.shields.io/badge/status-alfa-orange)](docs/MISSING.md)
[![macOS](https://img.shields.io/badge/macOS-Apple%20Silicon-lightgrey?logo=apple)](#compilando)
[![Android](https://img.shields.io/badge/Android-10%2B%20arm64-3DDC84?logo=android&logoColor=white)](#compilando)
[![Licença](https://img.shields.io/badge/licen%C3%A7a-MIT-green)](LICENSE)

[English](README.md) · **Português (Brasil)**

</div>

---

O Olympus é irmão do [Sparta](https://github.com/arnaldolima1/gow-ghost-of-sparta-pc) (Ghost of Sparta): o mesmo motor, da Ready At Dawn, sobre o mesmo framework, o [PortableKit](https://github.com/arnaldolima1/PortableKit) (o branch `sparta` do fork). O código do jogo é recompilado antes para C++, e o PSP em volta dele (sistema, gráficos em Vulkan, som, controles, saves) é do PortableKit.

> [!IMPORTANT]
> Este repositório não contém nenhum dado de jogo. Você precisa da sua própria cópia: a versão europeia, **UCES-00842** (1.00). O programa instala o jogo a partir da sua imagem de disco.

## Situação

**Alfa.** [Releases](https://github.com/arnaldolima1/gow-chains-of-olympus-pc/releases) para macOS (Apple Silicon) e Android. Com o código do jogo recompilado, o jogo roda a 60 quadros por segundo e velocidade total num Apple M4; num Moto g84 (Snapdragon 695) também, na maior parte, com as lutas mais pesadas a 96–98% da velocidade. Só o começo do jogo foi jogado. START pula os vídeos. Veja [o que falta](docs/MISSING.md) e [o trabalho de desempenho](docs/PERFORMANCE.md).

## Compilando

Comece com `git clone --recursive https://github.com/arnaldolima1/gow-chains-of-olympus-pc.git`. Todo build tem os mesmos passos: compilar o programa, instalar o jogo a partir do seu `.iso`, recompilar o código do jogo (`generated/`) e compilar de novo com ele.

- **macOS** (Apple Silicon, ferramentas de linha de comando do Xcode):

  ```bash
  brew install cmake ninja ccache python sdl3 molten-vk vulkan-loader vulkan-headers glslang ffmpeg
  scripts/build.sh                                              # o programa, sem o código do jogo
  build/dev/bin/OlympusNative --install /caminho/para/UCES00842.iso --in-place
  scripts/generate.sh                                           # recompila o código do jogo para C++
  scripts/build.sh                                              # compila
  scripts/run.sh                                                # jogar
  ```

- **Android:** depois dos passos do macOS, com o Android SDK, o NDK e um JDK: `scripts/build_android.sh`, e `scripts/run_android.sh` para instalar num celular ligado por USB.
- **Windows:** [docs/WINDOWS.md](docs/WINDOWS.md) (ainda não testado).

Sem o código recompilado o programa ainda roda o jogo, no interpretador do PortableKit, umas vinte vezes mais devagar: é assim que um jogo novo começa.

## Créditos

- [PortableKit](https://github.com/TeamGDB/PortableKit), da TeamGDB: o recompilador e o sistema do PSP em volta do jogo.
- A tabela de chave do executável é a publicada para a tag dele, como o [Purun](https://github.com/TeamGDB/Purun) a traz.
- God of War é marca da Sony Interactive Entertainment. Este é um projeto não oficial, sem ligação com a Sony ou a Ready At Dawn.

## Licença

MIT: veja [LICENSE](LICENSE). Vale só para o código deste repositório, não para o jogo.
