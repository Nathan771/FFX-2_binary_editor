# FFX-2 Binary Editor

> Ferramenta para extração e injeção de textos nos arquivos binários de **Final Fantasy X-2 (VERSÃO HD REMASTER)**, desenvolvida para o projeto de tradução PT-BR.

---

## 📋 Sobre

O **FFX-2 Binary Editor** é um editor com interface gráfica que permite:

- Extrair strings de diálogo de arquivos `.bin` para um `.txt` editável (**Dump**)
- Injetar o texto traduzido de volta no binário (**Insert**)
- Detectar automaticamente o formato dos ponteiros (simples ou PS2)
- Agrupar duplicatas automaticamente para simplificar a edição

Desenvolvido como parte do projeto de tradução não oficial de **Final Fantasy X-2** para o português brasileiro.

---

## ⚙️ Requisitos

- Python 3.8+
- Tkinter (já incluído na maioria das instalações Python)

---

## 🚀 Como usar

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/FFX-2_binary_editor.git
cd FFX-2_binary_editor
```

### 2. Configure o caminho da tabela

No início do arquivo `ffx2_editor.py`, ajuste o caminho para a sua tabela de caracteres:

```python
TABELA_PATH = r"C:\caminho\para\tabela_binarios_Ffx2.tbl"
```

### 3. Execute o script

```bash
python ffx2_editor.py
```

---

## 📖 Fluxo de trabalho

```
VBF Unpacker → .bin → [Dump] → .txt → Tradução → [Insert] → .bin traduzido → VBF Packer
```

1. Use o **VBF Unpacker** para extrair o `.bin` do arquivo `.vbf` do jogo
2. Abra o editor e clique em **"Selecionar .bin e Extrair"**
3. Edite o `.txt` gerado com a tradução
4. Clique em **"Selecionar .bin e .txt e Injetar"**
5. Use o **VBF Packer** para reempacotar o `.bin` traduzido

---

## 📁 Formato dos arquivos .bin

Os arquivos `.bin` de diálogo do FFX-2 possuem dois formatos de ponteiros:

### Formato Simples
Os ponteiros são offsets diretos dentro do arquivo.

```
[offset 0x00]  00 78 00 00  → ponteiro para 0x0078
[offset 0x04]  00 99 00 00  → ponteiro para 0x0099
...
[dados a partir do primeiro offset]
```

O número de ponteiros é calculado como: `primeiro_valor // 4`

### Formato PS2
Os ponteiros possuem uma base alta somada (geralmente `0x00800000`), referente ao mapeamento de memória do PS2.

```
[offset 0x00]  38 00 80 00  → base 0x800000 + offset 0x0038
[offset 0x04]  38 00 80 00  → mesmo ponteiro (duplicata)
...
```

O script detecta automaticamente qual formato está sendo usado e salva essa informação no arquivo `_grupos.txt` para uso no Insert.

### Estrutura das strings

Cada string termina com `0x00` e pode conter bytes de controle do engine:

| Byte | Função |
|------|--------|
| `03` | Fim de caixa de diálogo |
| `48` | Pausa / nova linha |
| `46` | Vírgula |
| `4F` | Interrogação |
| `3B` | Exclamação |
| `3A` | Espaço |

### Duplicatas

Cada string de diálogo aparece **duas vezes consecutivas** nos arquivos — isso é normal e esperado pelo engine do jogo. O editor agrupa as duplicatas automaticamente no Dump e as replica corretamente no Insert.

---

## 🔤 Tabela de Caracteres

O FFX-2 usa um encoding proprietário. Abaixo a tabela completa mapeada:

### Letras maiúsculas

| Hex | Char | Hex | Char | Hex | Char |
|-----|------|-----|------|-----|------|
| 50  | A    | 51  | B    | 52  | C    |
| 53  | D    | 54  | E    | 55  | F    |
| 56  | G    | 57  | H    | 58  | I    |
| 59  | J    | 5A  | K    | 5B  | L    |
| 5C  | M    | 5D  | N    | 5E  | O    |
| 5F  | P    | 60  | Q    | 61  | R    |
| 62  | S    | 63  | T    | 64  | U    |
| 65  | V    | 66  | W    | 67  | X    |
| 68  | Y    | 69  | Z    |     |      |

### Letras minúsculas

| Hex | Char | Hex | Char | Hex | Char |
|-----|------|-----|------|-----|------|
| 70  | a    | 71  | b    | 72  | c    |
| 73  | d    | 74  | e    | 75  | f    |
| 76  | g    | 77  | h    | 78  | i    |
| 79  | j    | 7A  | k    | 7B  | l    |
| 7C  | m    | 7D  | n    | 7E  | o    |
| 7F  | p    | 80  | q    | 81  | r    |
| 82  | s    | 83  | t    | 84  | u    |
| 85  | v    | 86  | w    | 87  | x    |
| 88  | y    | 89  | z    |     |      |

### Pontuação e especiais

| Hex | Char      |
|-----|-----------|
| 3A  | (espaço)  |
| 3B  | !         |
| 3F  | ?         |
| 41  | '         |

### Caracteres acentuados

Descobertos através da análise das versões em espanhol e francês do jogo:

| Hex | Char | Hex | Char |
|-----|------|-----|------|
| BB  | á    | BE  | ç    |
| BF  | è    | C0  | é    |
| C1  | ê    | C4  | í    |
| C7  | ñ    | C9  | ó    |
| CE  | ú    |     |      |

> ⚠️ **Nota:** Os caracteres `ã` e `õ` **não existem** na fonte do jogo em nenhuma versão localizada. Palavras que os contenham devem ser adaptadas na tradução.

---

## 📄 Formato do arquivo .tbl

A tabela de caracteres segue o formato padrão de ROM hacking:

```
50=A
51=B
...
3A= 
BB=á
BE=ç
```

---

## 📌 Observações

- O tamanho do `.bin` traduzido pode ser diferente do original — isso é esperado, pois os ponteiros são recalculados dinamicamente
- Bytes de controle no formato `[XX]` dentro do texto são preservados integralmente na injeção
- O arquivo `_grupos.txt` gerado pelo Dump é necessário para o Insert — não o delete

---

## 📜 Licença

Este projeto é de uso livre para fins educacionais e de preservação. Não distribui nem inclui nenhum arquivo protegido por direitos autorais da Square Enix.
