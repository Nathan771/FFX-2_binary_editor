import struct
import os
import tkinter as tk
from tkinter import filedialog, messagebox

# ─────────────────────────────────────────────
#  CAMINHO FIXO DA TABELA
# ─────────────────────────────────────────────
TABELA_PATH = r"C:\Users\natha\Documents\FFX2_PROJETO\tabela_binarios_Ffx2.tbl"

# ─────────────────────────────────────────────
#  CARREGAR TABELA  (BYTE -> CHAR  e  CHAR -> BYTE)
# ─────────────────────────────────────────────
def carregar_tabela(path):
    byte_to_char = {}
    char_to_byte = {}

    with open(path, 'r', encoding='utf-8') as f:
        for linha in f:
            linha = linha.strip()
            if '=' not in linha:
                continue
            partes = linha.split('=', 1)
            hex_str = partes[0].strip()
            char    = partes[1]
            try:
                valor = int(hex_str, 16)
            except ValueError:
                continue
            byte_to_char[valor] = char
            if char and char not in char_to_byte:
                char_to_byte[char] = valor

    # Hardcoded para garantir prioridade
    byte_to_char[0x3A] = ' '
    char_to_byte[' '] = 0x3A
    byte_to_char[0x3F] = '?'
    char_to_byte['?'] = 0x3F

    return byte_to_char, char_to_byte

# ─────────────────────────────────────────────
#  DETECTAR PONTEIROS AUTOMATICAMENTE
#  Suporta dois formatos:
#  - 'simples': ponteiros são offsets diretos (ex: 0x0038)
#  - 'ps2':     ponteiros têm base alta (ex: 0x00800038)
# ─────────────────────────────────────────────
def detectar_ponteiros(dados):
    if len(dados) < 8:
        return 'simples', None, []

    primeiro = struct.unpack_from('<I', dados, 0)[0]

    # Tentar formato PS2 (base alta)
    base_candidata = primeiro & 0xFF800000
    if base_candidata != 0:
        offset_real = primeiro - base_candidata
        if 0 < offset_real < len(dados):
            # Confirmar lendo mais ponteiros
            ponteiros_reais = []
            for i in range(len(dados) // 4):
                val = struct.unpack_from('<I', dados, i * 4)[0]
                if (val & 0xFF800000) == base_candidata:
                    off = val - base_candidata
                    if 0 <= off < len(dados):
                        ponteiros_reais.append(off)
                    else:
                        break
                else:
                    break
            if ponteiros_reais:
                return 'ps2', base_candidata, ponteiros_reais

    # Formato simples
    n = primeiro // 4
    n = min(n, len(dados) // 4)
    ponteiros_reais = []
    for i in range(n):
        if i * 4 + 4 > len(dados):
            break
        val = struct.unpack_from('<I', dados, i * 4)[0]
        # Aceita ponteiro se estiver dentro do arquivo (incluindo 0 que pode ser string vazia)
        if 0 <= val < len(dados):
            ponteiros_reais.append(val)
        else:
            # Não quebra — apenas ignora ponteiros inválidos
            ponteiros_reais.append(0)

    return 'simples', None, ponteiros_reais

# ─────────────────────────────────────────────
#  DECODIFICAR UMA STRING A PARTIR DE UM OFFSET
# ─────────────────────────────────────────────
def decodificar_string(dados, offset, byte_to_char):
    resultado = ''
    pos = offset
    while pos < len(dados):
        b = dados[pos]
        if b == 0x00:
            break
        if b in byte_to_char:
            resultado += byte_to_char[b]
        else:
            resultado += f'[{b:02X}]'
        pos += 1
    return resultado

# ─────────────────────────────────────────────
#  DUMP  (binário → txt)
# ─────────────────────────────────────────────
def dump(bin_path, tabela_path):
    byte_to_char, _ = carregar_tabela(tabela_path)

    with open(bin_path, 'rb') as f:
        dados = f.read()

    formato, base, ponteiros_reais = detectar_ponteiros(dados)
    n = len(ponteiros_reais)

    strings = [decodificar_string(dados, ptr, byte_to_char) for ptr in ponteiros_reais]

    # Detectar grupos de duplicatas consecutivas
    representantes = []
    grupo_map = {}

    i = 0
    while i < len(strings):
        rep_idx = i
        representantes.append((rep_idx, strings[i]))
        grupo_map[i] = rep_idx
        j = i + 1
        while j < len(strings) and strings[j] == strings[i]:
            grupo_map[j] = rep_idx
            j += 1
        i = j

    # Salvar .txt
    txt_path = os.path.splitext(bin_path)[0] + '_dump.txt'
    with open(txt_path, 'w', encoding='utf-8') as f:
        for rep_idx, texto in representantes:
            f.write(f'[{rep_idx:04d}]{texto}\n')

    # Salvar mapeamento de grupos (inclui formato e base)
    map_path = os.path.splitext(bin_path)[0] + '_grupos.txt'
    with open(map_path, 'w', encoding='utf-8') as f:
        f.write(f'formato={formato}\n')
        f.write(f'base={base if base is not None else 0}\n')
        for idx, rep in grupo_map.items():
            f.write(f'{idx}={rep}\n')

    return txt_path, len(representantes), n, formato

# ─────────────────────────────────────────────
#  CODIFICAR UMA STRING PARA BYTES
# ─────────────────────────────────────────────
def codificar_string(texto, char_to_byte):
    encoded = bytearray()
    j = 0
    while j < len(texto):
        if texto[j] == '[' and j + 3 < len(texto) and texto[j+3] == ']':
            hex_val = texto[j+1:j+3]
            try:
                encoded.append(int(hex_val, 16))
                j += 4
                continue
            except ValueError:
                pass
        matched = False
        for length in (2, 1):
            sub = texto[j:j+length]
            if sub in char_to_byte:
                encoded.append(char_to_byte[sub])
                j += length
                matched = True
                break
        if not matched:
            encoded.append(0x3A)  # fallback: espaço
            j += 1
    encoded.append(0x00)
    return bytes(encoded)

# ─────────────────────────────────────────────
#  INSERT  (txt → binário reconstruído)
# ─────────────────────────────────────────────
def insert(bin_path, txt_path, tabela_path):
    _, char_to_byte = carregar_tabela(tabela_path)

    with open(bin_path, 'rb') as f:
        dados_originais = f.read()

    formato, base, ponteiros_reais = detectar_ponteiros(dados_originais)
    n_ponteiros = len(ponteiros_reais)

    # Carregar mapeamento de grupos
    map_path = os.path.splitext(bin_path)[0] + '_grupos.txt'
    grupo_map = {}
    formato_salvo = formato
    base_salva = base

    if os.path.exists(map_path):
        with open(map_path, 'r', encoding='utf-8') as f:
            for linha in f:
                linha = linha.strip()
                if linha.startswith('formato='):
                    formato_salvo = linha.split('=', 1)[1]
                elif linha.startswith('base='):
                    b = int(linha.split('=', 1)[1])
                    base_salva = b if b != 0 else None
                elif '=' in linha:
                    a, b = linha.split('=', 1)
                    grupo_map[int(a)] = int(b)
    else:
        grupo_map = {i: i for i in range(n_ponteiros)}

    # Ler txt editado
    with open(txt_path, 'r', encoding='utf-8') as f:
        linhas = f.read().splitlines()

    textos_rep = {}
    for linha in linhas:
        if not linha.startswith('['):
            continue
        fecha = linha.index(']')
        idx_str = linha[1:fecha]
        try:
            idx = int(idx_str)
        except ValueError:
            continue  # ignora tags como [0A] que não são índices
        texto = linha[fecha+1:]
        textos_rep[idx] = texto

    # Expandir: cada índice recebe o texto do seu representante
    strings_codificadas = []
    for i in range(n_ponteiros):
        rep = grupo_map.get(i, i)
        texto = textos_rep.get(rep, '')
        strings_codificadas.append(codificar_string(texto, char_to_byte))

    # Recalcular ponteiros com o formato correto
    inicio_dados = n_ponteiros * 4
    novos_ponteiros = []
    offset_atual = inicio_dados

    for s in strings_codificadas:
        if formato_salvo == 'ps2' and base_salva is not None:
            novos_ponteiros.append(offset_atual + base_salva)
        else:
            novos_ponteiros.append(offset_atual)
        offset_atual += len(s)

    # Construir novo binário
    novo_bin = bytearray()
    for ptr in novos_ponteiros:
        novo_bin += struct.pack('<I', ptr)
    for s in strings_codificadas:
        novo_bin += s

    out_path = os.path.splitext(bin_path)[0] + '_traduzido.bin'
    with open(out_path, 'wb') as f:
        f.write(novo_bin)

    return out_path

# ─────────────────────────────────────────────
#  VERIFICAR  (binário traduzido vs dump)
# ─────────────────────────────────────────────
def verificar(bin_orig_path, bin_trad_path, dump_path, tabela_path):
    byte_to_char, _ = carregar_tabela(tabela_path)

    def extrair_strings(path):
        with open(path, 'rb') as f:
            dados = f.read()
        formato, base, ponteiros = detectar_ponteiros(dados)
        visto = set()
        resultado = {}
        for i, ptr in enumerate(ponteiros):
            if ptr not in visto:
                visto.add(ptr)
                resultado[i] = decodificar_string(dados, ptr, byte_to_char)
        return resultado, len(ponteiros)

    orig_strings, orig_n = extrair_strings(bin_orig_path)
    trad_strings, trad_n = extrair_strings(bin_trad_path)

    # Ler índices do dump
    dump_indices = set()
    with open(dump_path, 'r', encoding='utf-8') as f:
        for linha in f:
            if linha.startswith('['):
                try:
                    dump_indices.add(int(linha[1:5]))
                except ValueError:
                    pass

    relatorio = []
    alertas = 0

    # 1. Contagem de ponteiros
    relatorio.append(f"Strings únicas — Original: {len(orig_strings)}  |  Traduzido: {len(trad_strings)}")
    relatorio.append(f"Total ponteiros — Original: {orig_n}  |  Traduzido: {trad_n}")

    if orig_n != trad_n:
        relatorio.append("⚠️  ATENÇÃO: número de ponteiros diferente!")
        alertas += 1
    else:
        relatorio.append(f"✅  Ponteiros: contagem correta ({orig_n})")

    # 2. Strings fora do dump
    faltando = [i for i in orig_strings if i not in dump_indices]
    nao_vazias = [(i, orig_strings[i]) for i in faltando if orig_strings[i].strip()]
    if nao_vazias:
        relatorio.append(f"\n⚠️  {len(nao_vazias)} string(s) com conteúdo fora do dump:")
        for i, t in nao_vazias:
            relatorio.append(f"   [{i:04d}] {t[:60]}")
        alertas += 1
    else:
        relatorio.append("✅  Todas as strings com conteúdo estão no dump")

    # 3. Strings em inglês no traduzido
    import re
    # Palavras/formas exclusivamente inglesas — baixo risco de falso positivo
    palavras_en_fortes = [
        "you've", "you're", "you'll", "you'd", "i've", "i'm", "i'll",
        "don't", "didn't", "doesn't", "won't", "can't", "isn't", "wasn't",
        "haven't", "hadn't", "there's", "that's", "it's", "let's",
        " the ", " their ", " them ", " they ", " your ", " yourself ",
        " you ", "you!", " and ", " but ", " with ", " from ", " what ",
        " this ", " that ", " will ", " shall ", " our ", " we ", " us ",
        " she ", " her ", " him ", " his ", " very ", " just ", " only ",
        " even ", " some ", " more ", " much ", " many ", " here ",
        " there ", " when ", " where ", " like ", " know ", " think ",
        " make ", " been ", " have ", " had ", " has ",
    ]
    # Termos do jogo que podem conter palavras inglesas — ignorar
    termos_jogo = [
        'gullwings', 'cactuar', 'celsius', 'bikanel', 'spira', 'blitzball',
        'machina', 'hover', 'oasis', 'sphere', 'yuna', 'rikku', 'paine',
        'marnela', 'nhadala', 'gippal', 'nooj', 'baralai', 'crimson',
        'assembly', 'coin', 'rank', 'sandbox', 'attack', 'defense',
        'special', 'scrap', 'metal', 'save', 'offline', 'done', 'zoom',
    ]
    suspeitas = []
    for i, t in trad_strings.items():
        tl = t.lower()
        # Remove tags [XX] para não confundir a busca
        tl_limpo = re.sub(r'\[[0-9a-f]{2}\]', ' ', tl)
        # Se for predominantemente termo do jogo, só marca se tiver forma verbal inglesa clara
        eh_termo_jogo = any(trm in tl_limpo for trm in termos_jogo)
        formas_verbais = ["you've","you're","you'll","don't","didn't","doesn't",
                          "won't","can't","isn't","wasn't","haven't","it's","let's"]
        if eh_termo_jogo:
            if any(p in tl_limpo for p in formas_verbais):
                suspeitas.append((i, t))
        else:
            if any(p in tl_limpo for p in palavras_en_fortes):
                suspeitas.append((i, t))
    if suspeitas:
        relatorio.append(f"\n⚠️  {len(suspeitas)} possível(is) string(s) em inglês:")
        for i, t in suspeitas[:10]:
            relatorio.append(f"   [{i:04d}] {t[:60]}")
        if len(suspeitas) > 10:
            relatorio.append(f"   ... e mais {len(suspeitas)-10}")
        alertas += 1
    else:
        relatorio.append("✅  Nenhuma string em inglês detectada")

    # Resumo
    relatorio.append(f"\n{'='*44}")
    if alertas == 0:
        relatorio.append("✅  TUDO CERTO! Arquivo pronto para uso.")
    else:
        relatorio.append(f"⚠️  {alertas} alerta(s) encontrado(s). Revise antes de usar.")

    return "\n".join(relatorio)


# ─────────────────────────────────────────────
#  INTERFACE GRÁFICA
# ─────────────────────────────────────────────
def main():
    root = tk.Tk()
    root.title("FFX-2 Editor de Texto")
    root.geometry("480x480")
    root.resizable(False, False)
    root.configure(bg="#1e1e2e")

    cor_bg  = "#1e1e2e"
    cor_btn = "#89b4fa"
    cor_txt = "#cdd6f4"
    cor_sub = "#a6e3a1"

    tk.Label(root, text="FFX-2 Editor de Texto", font=("Helvetica", 16, "bold"),
             bg=cor_bg, fg=cor_txt).pack(pady=18)

    tk.Label(root, text=f"Tabela: {TABELA_PATH}", font=("Helvetica", 7),
             bg=cor_bg, fg="#585b70", wraplength=460).pack()

    # ── DUMP ──
    frame_dump = tk.LabelFrame(root, text=" 1. Extrair texto (Dump) ", bg=cor_bg,
                               fg=cor_sub, font=("Helvetica", 10, "bold"), padx=10, pady=8)
    frame_dump.pack(fill="x", padx=20, pady=14)

    def btn_dump():
        bin_path = filedialog.askopenfilename(title="Selecione o arquivo .bin",
                                              filetypes=[("Binários", "*.bin"), ("Todos", "*.*")])
        if not bin_path:
            return
        try:
            txt_path, n_unicas, n_total, fmt = dump(bin_path, TABELA_PATH)
            messagebox.showinfo("Dump concluído!",
                f"Formato detectado: {fmt}\n"
                f"{n_unicas} frases únicas extraídas ({n_total} total com duplicatas).\n\n"
                f"Edite o arquivo e depois use 'Injetar':\n{txt_path}")
        except Exception as e:
            messagebox.showerror("Erro no Dump", str(e))

    tk.Button(frame_dump, text="Selecionar .bin e Extrair", bg=cor_btn, fg="#1e1e2e",
              font=("Helvetica", 10, "bold"), relief="flat", padx=12, pady=6,
              command=btn_dump).pack()

    # ── INSERT ──
    frame_ins = tk.LabelFrame(root, text=" 2. Injetar tradução (Insert) ", bg=cor_bg,
                              fg=cor_sub, font=("Helvetica", 10, "bold"), padx=10, pady=8)
    frame_ins.pack(fill="x", padx=20, pady=4)

    def btn_insert():
        bin_path = filedialog.askopenfilename(title="Selecione o .bin ORIGINAL",
                                              filetypes=[("Binários", "*.bin"), ("Todos", "*.*")])
        if not bin_path:
            return
        txt_path = filedialog.askopenfilename(title="Selecione o .txt EDITADO",
                                              filetypes=[("Texto", "*.txt"), ("Todos", "*.*")])
        if not txt_path:
            return
        try:
            out_path = insert(bin_path, txt_path, TABELA_PATH)
            messagebox.showinfo("Insert concluído!",
                f"Binário traduzido salvo em:\n{out_path}\n\nAgora é só usar o VBF Pack!")
        except Exception as e:
            messagebox.showerror("Erro no Insert", str(e))

    tk.Button(frame_ins, text="Selecionar .bin e .txt e Injetar", bg=cor_btn, fg="#1e1e2e",
              font=("Helvetica", 10, "bold"), relief="flat", padx=12, pady=6,
              command=btn_insert).pack()

    # ── VERIFICAR ──
    frame_ver = tk.LabelFrame(root, text=" 3. Verificar tradução ", bg=cor_bg,
                              fg=cor_sub, font=("Helvetica", 10, "bold"), padx=10, pady=8)
    frame_ver.pack(fill="x", padx=20, pady=14)

    def btn_verificar():
        bin_orig = filedialog.askopenfilename(title="Selecione o .bin ORIGINAL",
                                             filetypes=[("Binários", "*.bin"), ("Todos", "*.*")])
        if not bin_orig:
            return
        bin_trad = filedialog.askopenfilename(title="Selecione o .bin TRADUZIDO",
                                             filetypes=[("Binários", "*.bin"), ("Todos", "*.*")])
        if not bin_trad:
            return
        dump_path = filedialog.askopenfilename(title="Selecione o .txt do DUMP",
                                              filetypes=[("Texto", "*.txt"), ("Todos", "*.*")])
        if not dump_path:
            return
        try:
            relatorio = verificar(bin_orig, bin_trad, dump_path, TABELA_PATH)
            # Janela de resultado
            win = tk.Toplevel(root)
            win.title("Relatório de Verificação")
            win.configure(bg="#1e1e2e")
            win.geometry("560x400")
            txt = tk.Text(win, bg="#181825", fg="#cdd6f4", font=("Courier", 9),
                          wrap="word", padx=10, pady=10)
            txt.pack(fill="both", expand=True, padx=10, pady=10)
            txt.insert("1.0", relatorio)
            txt.config(state="disabled")
            # Colorir linhas de alerta/ok
            txt.config(state="normal")
            for tag, cor in [("ok", "#a6e3a1"), ("warn", "#f38ba8")]:
                txt.tag_config(tag, foreground=cor)
            for i, linha in enumerate(relatorio.splitlines(), start=1):
                if "✅" in linha:
                    txt.tag_add("ok", f"{i}.0", f"{i}.end")
                elif "⚠️" in linha:
                    txt.tag_add("warn", f"{i}.0", f"{i}.end")
            txt.config(state="disabled")
        except Exception as e:
            messagebox.showerror("Erro na Verificação", str(e))

    tk.Button(frame_ver, text="Selecionar .bin original, traduzido e .txt", bg="#cba6f7", fg="#1e1e2e",
              font=("Helvetica", 10, "bold"), relief="flat", padx=12, pady=6,
              command=btn_verificar).pack()

    root.mainloop()

if __name__ == "__main__":
    main()