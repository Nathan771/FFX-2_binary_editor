# FFX-2 Binary Editor

> 🇧🇷 **Português** | 🇺🇸 [English below](#english-version)

---

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?logo=windows)
![Status](https://img.shields.io/badge/Status-Em%20andamento-yellow)
![License](https://img.shields.io/badge/License-Educacional-green)

**Ferramenta de engenharia reversa para extração e injeção de texto em arquivos binários de Final Fantasy X-2 (HD Remaster)**

</div>

---

## 📸 Demonstração

![CrystalTile2 + Remaster](https://raw.githubusercontent.com/Nathan771/FFX-2_binary_editor/screenshot.png)

> *Esquerda: análise do binário no CrystalTile2. Direita: diálogo traduzido rodando o jogo.*

---

## 📋 Sobre o Projeto

O **FFX-2 Binary Editor** é uma ferramenta com interface gráfica (Tkinter) desenvolvida do zero para o projeto de **tradução não oficial de Final Fantasy X-2 para o Português Brasileiro**.

O projeto envolveu engenharia reversa dos arquivos `.bin` compactados dentro de containers `.vbf` — analisando estruturas de ponteiros, mapeando tabelas de caracteres proprietárias e desenvolvendo um pipeline completo de extração, tradução e reinjeção de texto.

### 🔧 Funcionalidades

- **Dump** — extrai strings de diálogo de arquivos `.bin` para um `.txt` editável
- **Insert** — injeta o texto traduzido de volta no binário com recálculo dinâmico de ponteiros
- **Verificar** — compara dump original vs traduzido vs binário gerado, detectando erros
- Detecção automática do formato de ponteiros (`simples`, `ps2`, `flag3`)
- Agrupamento automático de duplicatas
- Suporte a bytes de controle do engine do jogo

---

## 🧠 Habilidades Técnicas Demonstradas

> Esta seção destaca as competências de engenharia reversa aplicadas no projeto.

| Área | Aplicação |
|------|-----------|
| **Engenharia Reversa** | Análise de estrutura binária dos arquivos `.bin` e `.vbf` sem documentação disponível |
| **Análise de Binários** | Inspeção com CrystalTile2 e Ghidra para mapeamento de ponteiros e encoding |
| **Manipulação de Ponteiros** | Suporte a 3 formatos distintos com recálculo dinâmico pós-injeção |
| **Encoding Proprietário** | Mapeamento completo da tabela de caracteres do engine do FFX-2 |
| **Desenvolvimento Python** | Editor com GUI Tkinter, manipulação de bytes, I/O binário e JSON |
| **Shell Script** | Automação de conversão em lote de arquivos `.phyre` via linha de comando |
| **Análise de Formato** | Identificação e implementação dos formatos `simples`, `ps2` e `flag3` |

---

## ⚙️ Requisitos

- Python 3.8+
- Tkinter (já incluído na maioria das instalações Python)

---

## 🚀 Como Usar

### 1. Clone o repositório

```bash
git clone https://github.com/Nathan771/FFX-2_binary_editor.git
cd FFX-2_binary_editor
```

### 2. Configure o caminho da tabela de caracteres

No início do arquivo `ffx2_editor.py`, ajuste o caminho:

```python
TABELA_PATH = r"C:\caminho\para\tabela_binarios_Ffx2.tbl"
```

### 3. Execute

```bash
python ffx2_editor.py
```

---

## 📖 Fluxo de Trabalho

```
VBF Unpack → .bin → [Dump] → .txt → Tradução → [Insert] → .bin traduzido → VBF Pack → PCSX2
```

| Etapa | Descrição |
|-------|-----------|
| **VBF Unpack** | Extrai os `.bin` do container `.vbf` do jogo |
| **Dump** | Extrai as strings para um `.txt` editável |
| **Tradução** | Edição manual do `.txt` gerado |
| **Insert** | Injeta o texto traduzido de volta no `.bin` |
| **VBF Pack** | Reempacota o `.bin` no container `.vbf` |
| **Teste** | Valida o resultado no emulador PCSX2 |

---

## 📁 Formatos de Ponteiro Suportados

O editor detecta automaticamente o formato com base nos valores dos ponteiros:

### Formato `simples`
Offsets de 32 bits diretos, sem base.
```
[0x00]  78 00 00 00  → ponteiro para offset 0x0078
[0x04]  99 00 00 00  → ponteiro para offset 0x0099
```

### Formato `ps2`
Ponteiros com base alta somada (ex: `0x00800000`), referente ao mapeamento de memória do PS2.
```
[0x00]  38 00 80 00  → base 0x800000 + offset 0x0038
```

### Formato `flag3`
Byte alto = flag/tipo de contexto (preservado). 3 bytes baixos = offset real.
```
[0x00]  05 00 12 00  → flag=0x05, offset=0x001200
[0x04]  0C 00 15 00  → flag=0x0C, offset=0x001500
```
Detectado quando há múltiplas flags únicas no arquivo. As flags são salvas em JSON no `_grupos.txt` e reconstruídas no Insert como `(flag << 24) | offset`.

---

## 🔤 Tabela de Caracteres

O FFX-2 usa encoding proprietário. Mapeamento completo:

### Maiúsculas
| Hex | Char | Hex | Char | Hex | Char | Hex | Char |
|-----|------|-----|------|-----|------|-----|------|
| 50 | A | 51 | B | 52 | C | 53 | D |
| 54 | E | 55 | F | 56 | G | 57 | H |
| 58 | I | 59 | J | 5A | K | 5B | L |
| 5C | M | 5D | N | 5E | O | 5F | P |
| 60 | Q | 61 | R | 62 | S | 63 | T |
| 64 | U | 65 | V | 66 | W | 67 | X |
| 68 | Y | 69 | Z |    |   |    |   |

### Minúsculas
| Hex | Char | Hex | Char | Hex | Char | Hex | Char |
|-----|------|-----|------|-----|------|-----|------|
| 70 | a | 71 | b | 72 | c | 73 | d |
| 74 | e | 75 | f | 76 | g | 77 | h |
| 78 | i | 79 | j | 7A | k | 7B | l |
| 7C | m | 7D | n | 7E | o | 7F | p |
| 80 | q | 81 | r | 82 | s | 83 | t |
| 84 | u | 85 | v | 86 | w | 87 | x |
| 88 | y | 89 | z |    |   |    |   |

### Acentuados (PT-BR)
| Hex | Char | Hex | Char | Hex | Char |
|-----|------|-----|------|-----|------|
| BB | á | BE | ç | BF | è |
| C0 | é | C1 | ê | C4 | í |
| C9 | ó | CE | ú |    |   |

> ⚠️ Os caracteres `ã` e `õ` **não existem** na fonte do jogo. Palavras que os contenham são adaptadas na tradução.

### Bytes de Controle do Engine
| Byte | Função |
|------|--------|
| `03` | Separador de linha/opção |
| `46` | Continuação de linha |
| `48` | Fim de caixa de diálogo |
| `4F` | Interrogação |
| `3B` | Exclamação |
| `3A` | Espaço |

---

## 📌 Observações Técnicas

- O tamanho do `.bin` traduzido pode diferir do original — os ponteiros são recalculados dinamicamente
- Bytes de controle no formato `[XX]` são preservados integralmente na injeção
- O arquivo `_grupos.txt` gerado pelo Dump é necessário para o Insert — não o delete
- Strings duplicadas aparecem 2× em cada arquivo — comportamento normal e esperado pelo engine

---

## 📜 Licença

Uso livre para fins educacionais e de preservação. Não distribui nem inclui arquivos protegidos por direitos autorais da Square Enix.

---

---

# English Version

> 🇺🇸 **English** | 🇧🇷 [Português acima](#ffx-2-binary-editor)

---

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?logo=windows)
![Status](https://img.shields.io/badge/Status-In%20Progress-yellow)
![License](https://img.shields.io/badge/License-Educational-green)

**Reverse engineering tool for text extraction and injection in Final Fantasy X-2 (HD Remaster) binary files**

</div>

---

## 📋 About

The **FFX-2 Binary Editor** is a GUI-based tool (Tkinter) built from scratch for an **unofficial Portuguese (PT-BR) translation project of Final Fantasy X-2**.

The project involved reverse engineering `.bin` files packed inside `.vbf` containers — analyzing pointer structures, mapping proprietary character tables, and developing a complete pipeline for text extraction, translation, and re-injection.

### 🔧 Features

- **Dump** — extracts dialogue strings from `.bin` files into an editable `.txt`
- **Insert** — injects translated text back into the binary with dynamic pointer recalculation
- **Verify** — compares original dump vs translated vs generated binary, detecting errors
- Automatic pointer format detection (`simple`, `ps2`, `flag3`)
- Automatic duplicate grouping
- Engine control byte support

---

## 🧠 Technical Skills Demonstrated

| Area | Application |
|------|-------------|
| **Reverse Engineering** | Binary structure analysis of `.bin` and `.vbf` files without available documentation |
| **Binary Analysis** | Inspection with CrystalTile2 and Ghidra for pointer mapping and encoding |
| **Pointer Manipulation** | Support for 3 distinct formats with dynamic post-injection recalculation |
| **Proprietary Encoding** | Full mapping of the FFX-2 engine character table |
| **Python Development** | Tkinter GUI editor, byte manipulation, binary I/O and JSON handling |
| **Shell Scripting** | Batch automation for `.phyre` file conversion via command line |
| **Format Analysis** | Identification and implementation of `simple`, `ps2` and `flag3` formats |

---

## ⚙️ Requirements

- Python 3.8+
- Tkinter (included in most Python installations)

---

## 🚀 Usage

### 1. Clone the repository

```bash
git clone https://github.com/Nathan771/FFX-2_binary_editor.git
cd FFX-2_binary_editor
```

### 2. Set the character table path

At the top of `ffx2_editor.py`, adjust the path:

```python
TABELA_PATH = r"C:\path\to\tabela_binarios_Ffx2.tbl"
```

### 3. Run

```bash
python ffx2_editor.py
```

---

## 📖 Workflow

```
VBF Unpack → .bin → [Dump] → .txt → Translation → [Insert] → translated .bin → VBF Pack → PCSX2
```

---

## 📁 Supported Pointer Formats

| Format | Description |
|--------|-------------|
| `simple` | Direct 32-bit offsets, no base |
| `ps2` | Pointers with high base added (e.g. `0x00800000`) |
| `flag3` | High byte = context flag (preserved), low 3 bytes = real offset |

The `flag3` format is detected when multiple unique flags are found. Flags are saved as JSON in `_grupos.txt` and reconstructed on Insert as `(flag << 24) | offset`.

---

## 📜 License

Free to use for educational and preservation purposes. Does not distribute or include any files protected by Square Enix copyright.