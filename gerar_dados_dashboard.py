#!/usr/bin/env python3
"""Gera dados_dashboard.js, dados/cidades/*.js e dados/secoes_resumo.csv para as 15 cidades auditadas."""
import csv
import json
import os
from collections import Counter, defaultdict

ZONAS_SALVADOR = {
    "0001": ("Centro / Barra / Graça", "Centro, Pelourinho, Barra, Campo Grande, Canela, Graça, Vitória"),
    "0002": ("Rio Vermelho / Ondina", "Rio Vermelho, Ondina, Federação, Amaralina, Engenho Velho da Federação"),
    "0003": ("Fazenda Grande / Pau Miúdo", "Fazenda Grande do Retiro, Pau Miúdo, Cidade Nova, IAPI, Santa Mônica, San Martin"),
    "0004": ("Subúrbio / Paripe / Ilhas", "Paripe, Periperi, Coutos, Fazenda Coutos, São Tomé de Paripe, Ilha de Maré"),
    "0005": ("Cabula / Mata Escura", "Cabula, Mata Escura, Barreiras, Engomadeira, Resgate, São Gonçalo do Retiro"),
    "0006": ("Brotas / Candeal", "Brotas, Acupe de Brotas, Candeal, Bonocô, Campinas de Brotas, Boa Vista de Brotas"),
    "0007": ("Nazaré / Comércio / Barris", "Nazaré, Comércio, Barbalho, Barris, Saúde, Santo Antônio, Tororó, Vila Laura"),
    "0008": ("Pirajá / Valéria", "Pirajá, Valéria, Marechal Rondon, Campinas de Pirajá, Palestina"),
    "0009": ("Itapagipe / Ribeira / Bonfim", "Ribeira, Bonfim, Uruguai, Massaranduba, Mares, Boa Viagem, Monte Serrat"),
    "0010": ("Boca do Rio / Imbuí / Piatã", "Boca do Rio, Imbuí, Stiep, Costa Azul, Patamares, Piatã, Bairro da Paz"),
    "0011": ("Pau da Lima / Águas Claras", "Pau da Lima, Castelo Branco, Águas Claras, Sete de Abril, Vila Canária, Dom Avelar"),
    "0012": ("Itapuã / São Cristóvão", "Itapuã, São Cristóvão, Stella Maris, Mussurunga, Jardim das Margaridas"),
    "0013": ("Pituba / Itaigara / Nordeste", "Pituba, Itaigara, Caminho das Árvores, Iguatemi, Nordeste de Amaralina, Santa Cruz"),
    "0014": ("Tancredo Neves / Sussuarana", "Tancredo Neves, Sussuarana, Arenoso, Novo Horizonte, São Marcos"),
    "0015": ("São Caetano / Lobato", "São Caetano, Capelinha, Boa Vista do Lobato, Lobato, Bom Juá"),
    "0016": ("Pernambués / Narandiba / CAB", "Pernambués, Narandiba, Saboeiro, Doron, Saramandaia, CAB, Paralela"),
    "0017": ("Plataforma / Itacaranha", "Plataforma, Rio Sena, Alto da Terezinha, Itacaranha, Escada, Praia Grande"),
    "0018": ("Liberdade / Calçada", "Liberdade, Curuzu, Caixa D'Água, Calçada, Caminho de Areia, Lapinha, Soledade"),
    "0019": ("Cajazeiras / Mussurunga", "Cajazeiras, Fazenda Grande I–IV, Boca da Mata, Mussurunga, Nova Brasília, Trobogy"),
}

ZONAS_SP = {
    "0001": ("Bela Vista", "Bela Vista, Liberdade, Sé, Consolação, República"),
    "0002": ("Perdizes", "Perdizes, Barra Funda, Água Branca, Sumaré, Pacaembu"),
    "0003": ("Santa Ifigênia", "Santa Ifigênia, Bom Retiro, Pari, Brás, Canindé"),
    "0004": ("Mooca", "Mooca, Belém, Água Rasa, Brás, Alto da Mooca, Cambuci"),
    "0005": ("Jardim Paulista", "Jardim Paulista, Cerqueira César, Jardins, Pinheiros, Itaim Bibi"),
    "0006": ("Vila Mariana", "Vila Mariana, Paraíso, Aclimação, Mirandópolis, Saúde"),
    "0020": ("Valo Velho", "Valo Velho, Capão Redondo (Sul), Jardim Ângela"),
    "0246": ("Santo Amaro", "Santo Amaro, Campo Belo, Brooklin, Chácara Santo Antônio, Vila Olímpia"),
    "0247": ("São Miguel Paulista", "São Miguel Paulista, Vila Jacuí, Vila Curuçá"),
    "0248": ("Itaquera", "Itaquera, Cidade Líder, José Bonifácio, Parque do Carmo"),
    "0249": ("Santana", "Santana, Mandaqui, Santa Teresinha, Água Fria, Carandiru"),
    "0250": ("Lapa", "Lapa, Vila Leopoldina, Alto da Lapa, Vila Romana, Jaguaré"),
    "0251": ("Pinheiros", "Pinheiros, Alto de Pinheiros, Vila Madalena, Butantã"),
    "0252": ("Penha de França", "Penha, Cangaíba, Vila Esperança, Artur Alvim"),
    "0253": ("Tatuapé", "Tatuapé, Carrão, Vila Formosa, Parque São Jorge, Anália Franco"),
    "0254": ("Vila Maria", "Vila Maria, Vila Guilherme, Parque Novo Mundo"),
    "0255": ("Casa Verde", "Casa Verde, Limão, Cachoeirinha, Imirim"),
    "0256": ("Tucuruvi", "Tucuruvi, Santana, Parada Inglesa, Vila Gustavo, Mandaqui"),
    "0257": ("Vila Prudente", "Vila Prudente, São Lucas, Vila Alpina, Mooca"),
    "0258": ("Indianópolis", "Moema, Indianópolis, Campo Belo, Planalto Paulista, Vila Nova Conceição"),
    "0259": ("Saúde", "Saúde, Cursino, Bosque da Saúde, Vila Gumercindo, Sacomã"),
    "0260": ("Ipiranga", "Ipiranga, Sacomã, Moinho Velho, Vila Monumento, Heliópolis"),
    "0280": ("Capela do Socorro", "Socorro, Cidade Dutra, Veleiros, Interlagos, Grajaú"),
    "0320": ("Jabaquara", "Jabaquara, Cidade Vargas, Vila Mascote, Americanópolis"),
    "0325": ("Pirituba", "Pirituba, São Domingos, Parque São Domingos, Jaraguá"),
    "0326": ("Ermelino Matarazzo", "Ermelino Matarazzo, Ponte Rasa, Parque Boturussu"),
    "0327": ("Nossa Senhora do Ó", "Freguesia do Ó, Brasilândia, Vila Albertina, Piqueri"),
    "0328": ("Campo Limpo", "Campo Limpo, Vila Andrade, Morumbi, Pirajussara"),
    "0346": ("Butantã", "Butantã, Morumbi, Vila Sônia, Ferreira, Caxingui"),
    "0347": ("Vila Matilde", "Vila Matilde, Cidade Patriarca, Artur Alvim, Vila Dalila"),
    "0348": ("Vila Formosa", "Vila Formosa, Aricanduva, Carrão, Sapopemba"),
    "0349": ("Jaçanã", "Jaçanã, Tremembé, Parque Edu Chaves, Furnas"),
    "0350": ("Sapopemba", "Sapopemba, Fazenda da Juta, Parque Bancário, Vila Ema"),
    "0351": ("Cidade Ademar", "Cidade Ademar, Pedreira, Cupecê, Americanópolis"),
    "0352": ("Itaim Paulista", "Itaim Paulista, Vila Curuçá, Jardim Camargo Novo"),
    "0353": ("Guaianases", "Guaianases, Lajeado, Cidade Tiradentes"),
    "0371": ("Grajaú", "Grajaú, Parque Cocaia, Cantinho do Céu, Varginha"),
    "0372": ("Piraporinha", "Jardim Ângela, M'Boi Mirim, Piraporinha, Jardim Nakamura"),
    "0373": ("Capão Redondo", "Capão Redondo, Jardim São Bento, Parque Fernanda"),
    "0374": ("Rio Pequeno", "Rio Pequeno, Raposo Tavares, Jaguaré, Educandário"),
    "0375": ("São Mateus", "São Mateus, Iguatemi, Cidade Satélite Santa Bárbara, São Rafael"),
    "0376": ("Brasilândia", "Brasilândia, Jardim Paulistano, Vila Teresinha, Morro Grande"),
    "0381": ("Parelheiros", "Parelheiros, Marsilac, Vargem Grande, Colônia (Extremo Sul)"),
    "0389": ("Perus", "Perus, Anhanguera, Morro Doce, Jardim Britânia"),
    "0390": ("Cangaíba", "Cangaíba, Engenheiro Goulart, Penha"),
    "0392": ("Ponte Rasa", "Ponte Rasa, Burgo Paulista, Ermelino Matarazzo"),
    "0397": ("Jardim Helena", "Jardim Helena, Vila Mara, São Miguel Paulista"),
    "0403": ("Jaraguá", "Jaraguá, Taipas, Cidade D'Abril, Vila Pirituba"),
    "0404": ("Cidade Tiradentes", "Cidade Tiradentes, Barro Branco, Prestes Maia"),
    "0405": ("Conj. José Bonifácio", "José Bonifácio, Itaquera, Conjunto Residencial José Bonifácio"),
    "0408": ("Jardim São Luís", "Jardim São Luís, Jardim Ibirapuera, Copacabana, Guarapiranga"),
    "0413": ("Cursino", "Cursino, Sacomã, Água Funda, Vila Moraes, Jardim Clímax"),
    "0417": ("Parque do Carmo", "Parque do Carmo, Fazenda Caguaçu, Jardim Nossa Senhora do Carmo"),
    "0418": ("Pedreira", "Pedreira, Cidade Ademar, Jardim Miriam, Alvarenga"),
    "0420": ("Vila Sabrina", "Vila Sabrina, Vila Medeiros, Jardim Japão"),
    "0421": ("Teotônio Vilela", "Conj. Teotônio Vilela, Sapopemba, Parque Santa Madalena"),
    "0422": ("Lauzane Paulista", "Lauzane Paulista, Mandaqui, Cachoeirinha, Pedra Branca"),
}

ZONAS_CUIABA = {
    "0001": ("Centro / Goiabeiras", "Centro, Goiabeiras, Quilombo, Araés, Duque de Caxias"),
    "0037": ("Coxipó / Tijucal", "Coxipó, Tijucal, Pedra 90, Osmar Cabral, São Gonçalo"),
    "0039": ("CPA / Morada da Serra", "CPA I–IV, Morada da Serra, Morada do Ouro, Jardim Vitória"),
    "0051": ("Cristo Rei / Porto", "Porto, Cidade Alta, Dom Aquino, Poção, Boa Esperança"),
    "0054": ("Bandeirantes / Alvorada", "Alvorada, Despraiado, Ribeirão do Lipa, Santa Isabel"),
    "0055": ("Parque Cuiabá / Sul", "Parque Cuiabá, Parque Ohara, Parque Atalaia, Coophema"),
}

CIDADES_CFG = [
    # id, nome, uf, mun, grupo, grid_cols, mapa_zonas, nota_status
    ("sp", "São Paulo", "sp", "71072", "prorrogada", 8, ZONAS_SP, ""),
    ("salvador", "Salvador", "ba", "38490", "prorrogada", 5, ZONAS_SALVADOR, ""),
    ("feira", "Feira de Santana", "ba", "35157", "prorrogada", 4, {}, "1.218 seções com BU apuradas (308 seções constam como 'Recebida' aguardando totalização no TSE)"),
    ("guarulhos", "Guarulhos", "sp", "64777", "prorrogada", 4, {}, ""),
    ("bh", "Belo Horizonte", "mg", "41238", "controle", 6, {}, ""),
    ("curitiba", "Curitiba", "pr", "75353", "controle", 4, {}, ""),
    ("portoalegre", "Porto Alegre", "rs", "88013", "controle", 4, {}, ""),
    ("sbc", "São Bernardo do Campo", "sp", "70750", "controle", 3, {}, ""),
    ("santoandre", "Santo André", "sp", "70572", "controle", 3, {}, ""),
    ("osasco", "Osasco", "sp", "67890", "controle", 3, {}, ""),
    ("cuiaba", "Cuiabá", "mt", "90670", "controle", 3, ZONAS_CUIABA, ""),
    ("joinville", "Joinville", "sc", "81795", "controle", 3, {}, ""),
    ("vitoria_conquista", "Vitória da Conquista", "ba", "39659", "controle", 3, {}, ""),
    ("blumenau", "Blumenau", "sc", "80470", "controle", 3, {}, ""),
    ("paranagua", "Paranaguá", "pr", "77453", "controle", 2, {}, ""),
]

FAIXAS_ORDEM = [
    "17:00–17:09",
    "17:10–17:19",
    "17:20–17:29",
    "17:30–17:59",
    "18:00–18:29",
    "18:30–18:59",
    "19:00–19:09",
    "19:10+",
]


def faixa_enc(enc):
    if not enc:
        return "Sem BU"
    hhmm = enc[:5]
    if hhmm < "17:00":
        return "<17:00"
    if hhmm < "17:10":
        return "17:00–17:09"
    if hhmm < "17:20":
        return "17:10–17:19"
    if hhmm < "17:30":
        return "17:20–17:29"
    if hhmm < "18:00":
        return "17:30–17:59"
    if hhmm < "18:30":
        return "18:00–18:29"
    if hhmm < "19:00":
        return "18:30–18:59"
    if hhmm < "19:10":
        return "19:00–19:09"
    return "19:10+"


def ler_oficial(path):
    if not os.path.exists(path):
        return None
    d = json.load(open(path, encoding="utf-8"))
    v = d.get("v", {})
    tv = int(v.get("tv", 0))
    vv = int(v.get("vv", 0))
    vb = int(v.get("vb", 0))
    vn = int(v.get("tvn") or v.get(" tvn") or 0)
    te = int(d.get("e", {}).get("te", 0))
    cands = []
    carg = d.get("carg", [{}])[0]
    for a in carg.get("agr", []):
        for p in a.get("par", []):
            sg = p.get("sg", "")
            for c in p.get("cand", []):
                pct_str = (c.get("pvapn") or c.get("pvap") or "0").replace(",", ".")
                cands.append({
                    "n": c.get("n", ""),
                    "nome": c.get("nmu", "").title(),
                    "sg": sg,
                    "v": int(c.get("vap", 0)),
                    "pct": float(pct_str),
                })
    cands.sort(key=lambda x: -x["v"])
    lula = next((c for c in cands if c["n"] == "13"), {"v": 0, "pct": 0.0})
    flavio = next((c for c in cands if c["n"] == "22"), {"v": 0, "pct": 0.0})
    outros = [
        [f"{c['nome']} ({c['sg']})", c["v"]]
        for c in cands
        if c["n"] not in ("13", "22")
    ]
    return {
        "aptos": te,
        "comp": tv,
        "validos": vv,
        "brancos": vb,
        "nulos": vn,
        "l": lula["v"],
        "lp": round(lula["pct"], 2),
        "f": flavio["v"],
        "fp": round(flavio["pct"], 2),
        "outros": outros,
    }


def agregar_grupo(secoes):
    bu = [s for s in secoes if "aptos" in s]
    aptos = sum(s["aptos"] for s in bu)
    comp = sum(s["comparecimento"] for s in bu)
    rdv = sum(s.get("rdv_votos", 0) for s in bu)
    v13 = sum(s["votos"].get("13", 0) for s in bu)
    v22 = sum(s["votos"].get("22", 0) for s in bu)
    vb = sum(s["votos"].get("branco", 0) for s in bu)
    vn = sum(s["votos"].get("nulo", 0) for s in bu)
    vp17 = sum(s.get("votos_pos17", 0) for s in bu)
    hp17 = sum(s.get("habilit_pos17", 0) for s in bu)
    v1t = sum(s.get("votos_1t", 0) for s in bu)
    vp17_1t = sum(s.get("votos_1t_pos17", 0) for s in bu)
    v2t_log = sum(s.get("votos_2t", 0) for s in bu)
    locais = len({(s["zona"], s.get("local")) for s in bu if s.get("local") is not None})
    sem_vp17 = sum(1 for s in bu if s.get("votos_pos17", 0) == 0)
    com_vp17 = sum(1 for s in bu if s.get("votos_pos17", 0) > 0)
    max_vp17 = max((s.get("votos_pos17", 0) for s in bu), default=0)

    hrs = Counter()
    enc_bins = Counter()
    for s in bu:
        for h, c in s.get("votos_hora", {}).items():
            hrs[int(h)] += c
        enc_bins[faixa_enc(s.get("encerramento"))] += 1

    v17_only = hrs.get(17, 0)
    v18_plus = hrs.get(18, 0) + hrs.get(19, 0)

    return {
        "n_secoes": len(bu),
        "n_locais": locais,
        "aptos": aptos,
        "comp": comp,
        "rdv": rdv,
        "v2t_log": v2t_log,
        "l": v13,
        "f": v22,
        "validos": v13 + v22,
        "brancos": vb,
        "nulos": vn,
        "votos_pos17": vp17,
        "votos_17h": v17_only,
        "votos_pos18": v18_plus,
        "habilit_pos17": hp17,
        "votos_1t": v1t,
        "votos_1t_pos17": vp17_1t,
        "sem_voto_pos17": sem_vp17,
        "com_voto_pos17": com_vp17,
        "max_votos_pos17": max_vp17,
        "votos_hora": {str(h): hrs.get(h, 0) for h in range(8, 20)},
        "enc_bins": {k: enc_bins.get(k, 0) for k in FAIXAS_ORDEM},
    }


def main():
    os.makedirs("dados/cidades", exist_ok=True)
    cidades_dict = {}
    csv_rows = []

    for cid_id, nome, uf, mun, grupo, cols_grid, mapa_zonas, nota_status in CIDADES_CFG:
        pasta = f"dados/{uf}_{mun}"
        sec_path = os.path.join(pasta, "secoes.json")
        if not os.path.exists(sec_path):
            print(f"PULANDO {cid_id}: {sec_path} não existe")
            continue

        d = json.load(open(sec_path, encoding="utf-8"))
        t1 = ler_oficial(os.path.join(pasta, "oficial_1t.json"))
        t2 = ler_oficial(os.path.join(pasta, "oficial_2t.json"))
        secoes_raw = d["secoes"]
        bu = [s for s in secoes_raw if "aptos" in s]
        pos18 = [s for s in bu if (s.get("encerramento") or "") >= "18:00"]
        ate18 = [s for s in bu if (s.get("encerramento") or "") < "18:00"]

        # Se não houver oficial_1t/2t por alguma razão, sintetizar do BU
        if not t2:
            agg_all = agregar_grupo(bu)
            t2 = {
                "aptos": agg_all["aptos"], "comp": agg_all["comp"],
                "validos": agg_all["validos"], "brancos": agg_all["brancos"], "nulos": agg_all["nulos"],
                "l": agg_all["l"], "lp": round(agg_all["l"]/agg_all["validos"]*100, 2) if agg_all["validos"] else 0,
                "f": agg_all["f"], "fp": round(agg_all["f"]/agg_all["validos"]*100, 2) if agg_all["validos"] else 0,
                "outros": [],
            }
        if not t1:
            t1 = t2.copy()

        por_zona = defaultdict(list)
        for s in bu:
            por_zona[s["zona"]].append(s)

        zonas_out = []
        for idx, z_cd in enumerate(sorted(por_zona.keys())):
            z_secs = por_zona[z_cd]
            z_pos18 = [s for s in z_secs if (s.get("encerramento") or "") >= "18:00"]
            z_ate18 = [s for s in z_secs if (s.get("encerramento") or "") < "18:00"]
            nm_curto, bairros = mapa_zonas.get(z_cd, (f"Zona {z_cd}", ""))
            zonas_out.append({
                "zona": z_cd,
                "nome": nm_curto,
                "bairros": bairros,
                "x": idx % cols_grid,
                "y": idx // cols_grid,
                "total": agregar_grupo(z_secs),
                "pos18": agregar_grupo(z_pos18),
                "ate18": agregar_grupo(z_ate18),
            })

        # Compactar seções para o arquivo individual da cidade
        secoes_compact = []
        for s in bu:
            vh = s.get("votos_hora", {})
            vh_arr = [vh.get(str(h), 0) for h in range(8, 20)]
            row = [
                s["zona"],
                s["secao"],
                s.get("local") or 0,
                s["aptos"],
                s["comparecimento"],
                s["votos"].get("13", 0),
                s["votos"].get("22", 0),
                s["votos"].get("branco", 0),
                s["votos"].get("nulo", 0),
                (s.get("abertura") or "")[:8],
                (s.get("encerramento") or "")[:8],
                (s.get("ultimo_voto") or "")[:8],
                (s.get("encerrar") or "")[:8],
                s.get("votos_pos17", 0),
                s.get("habilit_pos17", 0),
                s.get("votos_1t", 0),
                s.get("votos_1t_pos17", 0),
                vh.get("17", 0),
                vh.get("18", 0),
                vh.get("19", 0),
                vh_arr,
                s.get("rdv_votos", 0),
                s.get("votos_2t", 0),
            ]
            secoes_compact.append(row)
            csv_rows.append([
                uf.upper(), cid_id, s["zona"], s["secao"], s.get("local") or 0,
                s["aptos"], s["comparecimento"], s["votos"].get("13", 0), s["votos"].get("22", 0),
                s["votos"].get("branco", 0), s["votos"].get("nulo", 0),
                (s.get("encerramento") or "")[:8], (s.get("ultimo_voto") or "")[:8],
                s.get("votos_pos17", 0), vh.get("17", 0), vh.get("18", 0), vh.get("19", 0),
                s.get("votos_1t_pos17", 0)
            ])

        # Gravar arquivo específico da cidade para carregamento sob demanda
        cidade_js = f"window.DASH_SECOES = window.DASH_SECOES || {{}}; window.DASH_SECOES['{cid_id}'] = " + json.dumps(secoes_compact, ensure_ascii=False, separators=(",", ":")) + ";\n"
        cid_js_path = f"dados/cidades/{cid_id}.js"
        with open(cid_js_path, "w", encoding="utf-8") as f:
            f.write(cidade_js)

        cidades_dict[cid_id] = {
            "id": cid_id,
            "nome": nome,
            "uf": uf.upper(),
            "mun": mun,
            "grupo": grupo,
            "nota_status": nota_status,
            "offset_bsb_h": d.get("offset_bsb_h", 0),
            "cols_grid": cols_grid,
            "t1": t1,
            "t2": t2,
            "total": agregar_grupo(bu),
            "pos18": agregar_grupo(pos18),
            "ate18": agregar_grupo(ate18),
            "zonas": zonas_out,
            "n_secoes_total": len(bu),
        }
        print(f"OK {cid_id} ({nome}): {len(bu)} seções -> {cid_js_path} ({len(cidade_js)/1e6:.2f} MB)")

    out_obj = {
        "atualizado": "26/10/2026 · Auditoria consolidada BU + RDV + Log das 15 cidades",
        "faixas_enc": FAIXAS_ORDEM,
        "cidades": cidades_dict,
    }
    js_str = "window.DASH = " + json.dumps(out_obj, ensure_ascii=False, separators=(",", ":")) + ";\n"
    with open("dados_dashboard.js", "w", encoding="utf-8") as f:
        f.write(js_str)
    print(f"dados_dashboard.js gerado: {len(js_str) / 1e3:.1f} KB")

    # Gravar CSV consolidado
    csv_path = "dados/secoes_resumo.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "uf", "cidade", "zona", "secao", "local", "aptos", "comp",
            "v13", "v22", "branco", "nulo",
            "encerramento", "ultimo_voto",
            "votos_pos17", "v17h", "v18h", "v19h", "votos_1t_pos17"
        ])
        w.writerows(csv_rows)
    print(f"{csv_path} gerado: {os.path.getsize(csv_path) / 1e6:.2f} MB ({len(csv_rows)} seções)")


if __name__ == "__main__":
    main()
