const fs = require('fs');
const path = require('path');
const { chromium } = require('/usr/lib/chatgpt/resources/cua_node/lib/node_modules/playwright-core');

global.window = global;
require('./dados_dashboard.js');
const D = window.DASH;

const fmt = n => Math.round(n || 0).toLocaleString('pt-BR');
const pc = (n, d = 2) => Number(n).toFixed(d).replace('.', ',');

const outDir45 = path.join(__dirname, 'instagram');
const outDir916 = path.join(__dirname, 'instagram', '1080x1920');
fs.mkdirSync(outDir45, { recursive: true });
fs.mkdirSync(outDir916, { recursive: true });

const GITHUB_ICON = `<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" style="vertical-align:-3px;margin-right:6px"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>`;

function baseTemplate(slideNum, titleKicker, innerHtml, height = 1350) {
  const isTall = height >= 1800;
  return `<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..900&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap">
<style>
:root {
  --bg: #f6f1e7;
  --paper: #fbf8f1;
  --ink: #161514;
  --muted: #5c564e;
  --line: #d8cfc0;
  --soft: #ede5d5;
  --accent: #8b4513;
  --accent-soft: #f3e5d7;
  --lula: #c41e24;
  --flavio: #183a6e;
  --part: #15803d;
  --part-soft: #dcfce7;
  --calc: #6d28d9;
  --display: 'Archivo', system-ui, sans-serif;
  --serif: 'Source Serif 4', Georgia, serif;
  --mono: 'JetBrains Mono', monospace;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  width: 1080px;
  height: ${height}px;
  background: var(--bg);
  color: var(--ink);
  font-family: var(--serif);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  overflow: hidden;
  -webkit-font-smoothing: antialiased;
}
.top-strip {
  background: var(--ink);
  color: #f6f1e7;
  padding: ${isTall ? '22px 44px' : '16px 40px'};
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-family: var(--mono);
  font-size: 15px;
  letter-spacing: .06em;
  text-transform: uppercase;
  border-bottom: 4px solid var(--accent);
}
.top-strip .brand {
  font-weight: 800;
  color: #f59e0b;
  display: flex;
  align-items: center;
  gap: 10px;
}
.top-strip .brand-dot {
  width: 10px; height: 10px; border-radius: 50%; background: #22c55e; display: inline-block;
}
.top-strip .credit-top {
  color: #fbf8f1;
  font-weight: 700;
  background: rgba(255,255,255,0.12);
  padding: 5px 14px;
  border-radius: 6px;
}
.top-strip .pg {
  font-weight: 800;
  color: #f6f1e7;
  background: var(--accent);
  padding: 4px 14px;
  border-radius: 99px;
}
.content {
  flex: 1;
  padding: ${isTall ? '36px 44px' : '22px 40px'};
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: ${isTall ? '22px' : '14px'};
}
.kicker {
  font-family: var(--mono);
  font-size: 14px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .1em;
  color: var(--accent);
  margin-bottom: 4px;
}
h1 {
  font-family: var(--display);
  font-weight: 900;
  font-variation-settings: "wdth" 88;
  font-size: ${isTall ? '54px' : '46px'};
  line-height: 1.03;
  letter-spacing: -.02em;
  color: var(--ink);
}
h2 {
  font-family: var(--display);
  font-weight: 900;
  font-variation-settings: "wdth" 88;
  font-size: ${isTall ? '44px' : '38px'};
  line-height: 1.06;
  letter-spacing: -.015em;
  color: var(--ink);
}
.lead {
  font-size: ${isTall ? '21px' : '18.5px'};
  line-height: 1.38;
  color: #2c2926;
  margin-top: 6px;
}
.lead code, .mono {
  font-family: var(--mono);
  font-size: 0.9em;
  background: var(--soft);
  padding: 1px 6px;
  border-radius: 4px;
}
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}
.kpi {
  background: var(--paper);
  border: 1.5px solid var(--line);
  border-top: 5px solid var(--c, var(--accent));
  border-radius: 10px;
  padding: ${isTall ? '18px 16px' : '13px 14px'};
}
.kpi .lbl {
  font-family: var(--mono);
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .05em;
  color: var(--muted);
}
.kpi .val {
  font-family: var(--display);
  font-weight: 900;
  font-variation-settings: "wdth" 82;
  font-size: ${isTall ? '40px' : '34px'};
  line-height: 1.05;
  color: var(--c, var(--ink));
  margin: 4px 0;
}
.kpi .sub {
  font-family: var(--mono);
  font-size: 12px;
  color: var(--muted);
  line-height: 1.25;
}
.facts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: ${isTall ? '18px' : '12px'};
}
.fact-card {
  background: var(--paper);
  border: 1.5px solid var(--line);
  border-radius: 10px;
  padding: ${isTall ? '22px 22px' : '15px 18px'};
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.fact-card .num-badge {
  font-family: var(--mono);
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: .06em;
  color: var(--accent);
}
.fact-card h3 {
  font-family: var(--display);
  font-weight: 800;
  font-size: ${isTall ? '23px' : '19.5px'};
  line-height: 1.15;
  color: var(--ink);
}
.fact-card p {
  font-size: ${isTall ? '17.5px' : '15.2px'};
  line-height: 1.38;
  color: #36322e;
}
.verdict-banner {
  background: #eaf5ec;
  border: 2px solid #86efac;
  border-left: 8px solid var(--part);
  border-radius: 10px;
  padding: ${isTall ? '18px 22px' : '13px 18px'};
}
.verdict-banner .v-text {
  font-size: ${isTall ? '19px' : '16.2px'};
  line-height: 1.36;
  color: #112617;
}
.city-tbl {
  width: 100%;
  border-collapse: collapse;
  font-family: var(--mono);
  font-size: ${isTall ? '13.5px' : '12.5px'};
  text-align: right;
}
.city-tbl th {
  padding: ${isTall ? '11px 8px' : '8px 8px'};
  background: var(--ink);
  color: #f6f1e7;
  font-family: var(--display);
  font-size: 11.5px;
  text-transform: uppercase;
  letter-spacing: .04em;
}
.city-tbl td {
  padding: ${isTall ? '9.5px 8px' : '6px 8px'};
  border-bottom: 1px solid var(--line);
}
.city-tbl th:first-child, .city-tbl td:first-child {
  text-align: left;
  padding-left: 12px;
}
.city-tbl th:last-child, .city-tbl td:last-child {
  padding-right: 12px;
}
.footer-bar {
  background: var(--paper);
  border-top: 2px solid var(--line);
  padding: ${isTall ? '18px 44px' : '13px 40px'};
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  font-family: var(--mono);
  font-size: 13px;
  color: var(--muted);
  white-space: nowrap;
}
.footer-bar .gh-pill {
  background: var(--ink);
  color: #fbf8f1;
  padding: 6px 14px;
  border-radius: 8px;
  font-weight: 700;
  font-size: 13.5px;
  display: inline-flex;
  align-items: center;
}
.footer-bar .swipe {
  font-weight: 800;
  color: var(--accent);
  text-transform: uppercase;
  letter-spacing: .04em;
}
</style>
</head>
<body>
  <div class="top-strip">
    <div class="brand"><span class="brand-dot"></span> AUDITORIA DE URNAS · 2º TURNO 2026</div>
    <div class="credit-top">${GITHUB_ICON}github.com/mmarsz</div>
    <div class="pg">${slideNum} / 4</div>
  </div>
  <div class="content">
    ${innerHtml}
  </div>
  <div class="footer-bar">
    <div class="gh-pill">${GITHUB_ICON}github.com/mmarsz · mmarsz.github.io/urna-2t</div>
    <div>TSE Oficial (BU + RDV + Log ASN.1) · 57.744 seções</div>
    <div class="swipe">${slideNum < 4 ? 'Arraste para o lado →' : 'Dashboard & CSV no GitHub ✓'}</div>
  </div>
</body>
</html>`;
}

function makeSlide1(height) {
  const html = `
    <div>
      <div class="kicker">AUDITORIA INDEPENDENTE · 15 CIDADES · 16,38 MILHÕES DE VOTOS</div>
      <h1>Será que a prorrogação até as 19h foi injusta?</h1>
      <p class="lead">
        Após a vitória de Lula no 2º turno, a campanha de Flávio Bolsonaro anunciou que pedirá a anulação do pleito alegando que a ampliação do horário teria desequilibrado a disputa. Decodificamos urna por urna os <b>Boletins de Urna (<code>bu.dat</code>)</b>, <b>Registros Digitais do Voto (<code>rdv.dat</code>)</b> e <b>Logs de segundo (<code>logd.dat</code>)</b> do TSE.
      </p>
    </div>

    <div class="kpi-grid">
      <div class="kpi" style="--c:var(--ink)">
        <div class="lbl">Seções Auditadas</div>
        <div class="val">57.744</div>
        <div class="sub">15 cidades (4 prorrogadas + 11 controle)</div>
      </div>
      <div class="kpi" style="--c:var(--part)">
        <div class="lbl">Abertas ≥ 18h</div>
        <div class="val">2.494</div>
        <div class="sub">Só 4,32% do total (95,7% fecharam antes)</div>
      </div>
      <div class="kpi" style="--c:var(--accent)">
        <div class="lbl">Votos após 18h</div>
        <div class="val">865</div>
        <div class="sub">0,005% de 16,38 milhões de votos</div>
      </div>
      <div class="kpi" style="--c:var(--calc)">
        <div class="lbl">Fatia Pós-18h</div>
        <div class="val">≤ 0,015%</div>
        <div class="sub">0,0083% em SP · 0,0146% em Salvador</div>
      </div>
    </div>

    <div class="facts-grid">
      <div class="fact-card">
        <div class="num-badge">FATO 01 · FONTE: AGÊNCIA BRASIL</div>
        <h3>Os dois lados pediram prorrogação até 19h</h3>
        <p>A coligação de Lula pediu prorrogação por falhas graves de ônibus. <b>A própria campanha de Flávio Bolsonaro também protocolou pedido de votação até as 19h</b> alegando fortes chuvas em SC, PR e interior de SP.</p>
      </div>
      <div class="fact-card">
        <div class="num-badge">FATO 02 · DECISÃO ÀS 17H20</div>
        <h3>Mais de 80% das urnas já estavam encerradas</h3>
        <p>Quando a decisão do Min. Cristiano Zanin (STF) chegou aos TREs, <b>mais de 80% das seções já haviam fechado às 17h</b> e emitido o Boletim de Urna. Só continuaram abertas as seções que ainda não haviam encerrado.</p>
      </div>
      <div class="fact-card">
        <div class="num-badge">FATO 03 · 4 DE 15 CIDADES</div>
        <h3>Só 4 cidades tiveram urnas abertas ≥ 18h</h3>
        <p>Das 15 cidades auditadas, apenas <b>São Paulo (1.661), Salvador (755), Feira de Santana (61) e Guarulhos (17)</b> tiveram seções abertas ≥18h. Em Curitiba, Joinville, Blumenau, POA e BH, <b>100% fecharam antes das 18h</b>.</p>
      </div>
      <div class="fact-card">
        <div class="num-badge">FATO 04 · URNAS VAZIAS</div>
        <h3>865 votos pós-18h e 44% das urnas sem eleitor</h3>
        <p>Somando todas as cidades, entraram apenas <b>865 votos após as 18h</b> (606 em SP, 240 em Salvador, 13 em Feira e 6 em Guarulhos). Em <b>44% das urnas prorrogadas</b>, nenhum eleitor apareceu depois das 17h.</p>
      </div>
    </div>

    <div class="verdict-banner">
      <div class="v-text">
        <b>Conclusão da Auditoria:</b> Os votos pós-18h equivalem a <b>0,0083% do comparecimento em SP</b> e <b>0,0146% em Salvador</b>. O RDV não traz horário (sigilo do voto), logo não indica em quem votaram — mas, mesmo no limite matemático extremo, o resultado permanece inalterado.
      </div>
    </div>
  `;
  return baseTemplate(1, 'CAPA', html, height);
}

function makeSlide2(height) {
  const isTall = height >= 1800;
  const sp = D.cidades.sp;
  const ssa = D.cidades.salvador;

  const hrs = ['8','9','10','11','12','13','14','15','16','17','18','19'];
  const spMax = Math.max(...hrs.map(h => sp.total.votos_hora[h] || 0));
  const ssaMax = Math.max(...hrs.map(h => ssa.total.votos_hora[h] || 0));

  const spNorm = sp.total.comp - sp.total.votos_pos17;
  const ssaNorm = ssa.total.comp - ssa.total.votos_pos17;

  function hourBars(vh, maxV) {
    return `<div style="display:grid;grid-template-columns:repeat(12,1fr);gap:6px;align-items:end;height:${isTall ? '130px' : '90px'};padding-top:18px;margin-top:4px;border-bottom:2px solid var(--line)">
      ${hrs.map(h => {
        const v = vh[h] || 0;
        const pct = maxV ? Math.max((v / maxV) * 100, v > 0 ? 4 : 1) : 1;
        const is17 = h === '17';
        const is18 = Number(h) >= 18;
        const col = is18 ? 'var(--part)' : (is17 ? '#d97706' : 'var(--flavio)');
        const vStr = v >= 10000 ? Math.round(v/1000) + 'k' : fmt(v);
        return `<div style="display:flex;flex-direction:column;align-items:center;height:100%;justify-content:flex-end">
          <div style="font-family:var(--mono);font-size:10.5px;font-weight:700;color:${is18 ? 'var(--part)' : 'var(--ink)'};margin-bottom:3px">${vStr}</div>
          <div style="width:100%;height:${pct}%;background:${col};border-radius:4px 4px 0 0"></div>
        </div>`;
      }).join('')}
    </div>
    <div style="display:grid;grid-template-columns:repeat(12,1fr);gap:6px;padding-top:4px;font-family:var(--mono);font-size:11px;text-align:center;color:var(--muted);font-weight:700">
      ${hrs.map(h => `<span style="${Number(h)>=18 ? 'color:var(--part);font-weight:800' : ''}">${h}h</span>`).join('')}
    </div>`;
  }

  const html = `
    <div>
      <div class="kicker">RAIO-X POR HORÁRIO · LOGS DE SEGUNDO (LOGD.DAT + LOGS ANINHADOS)</div>
      <h2>São Paulo &amp; Salvador: 99,99% votaram antes das 18h</h2>
      <p class="lead">
        Todo voto grava um carimbo de segundo no log da urna (inclusive em urnas substituídas). Veja a distribuição horária dos <b>8,75 milhões de votos</b> de São Paulo e Salvador e a comparação com a fila pós-17h do 1º turno:
      </p>
    </div>

    <!-- Card São Paulo -->
    <div style="background:var(--paper);border:1.5px solid var(--line);border-radius:12px;padding:${isTall ? '20px 22px' : '14px 18px'};display:flex;flex-direction:column;gap:8px">
      <div style="display:flex;justify-content:space-between;align-items:baseline;border-bottom:1px solid var(--line);padding-bottom:6px">
        <div>
          <span style="font-family:var(--display);font-weight:900;font-size:${isTall ? '28px' : '24px'}">São Paulo (SP)</span>
          <span style="font-family:var(--mono);font-size:13px;color:var(--muted);margin-left:8px">${fmt(sp.total.n_secoes)} seções · ${fmt(sp.total.comp)} votos</span>
        </div>
        <div style="font-family:var(--mono);font-size:13px;font-weight:800;color:var(--part);background:var(--part-soft);padding:3px 10px;border-radius:99px">
          1.661 seções abertas ≥18h (6,2%) → 606 votos pós-18h (0,008%)
        </div>
      </div>

      ${hourBars(sp.total.votos_hora, spMax)}

      <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:4px;font-family:var(--mono);font-size:12.5px">
        <div style="background:var(--soft);padding:8px 10px;border-radius:6px">
          <div style="color:var(--muted);font-size:11px">HORÁRIO NORMAL (8h–16h)</div>
          <b style="font-size:14.5px">${fmt(spNorm)} (${pc(spNorm/sp.total.comp*100, 3)}%)</b>
        </div>
        <div style="background:var(--soft);padding:8px 10px;border-radius:6px">
          <div style="color:var(--muted);font-size:11px">FILA NORMAL 17h (2ºT vs 1ºT)</div>
          <b style="font-size:14.5px">${fmt(sp.total.votos_17h)}</b> <span style="color:var(--muted)">(1ºT: ${fmt(sp.total.votos_1t_pos17)})</span>
        </div>
        <div style="background:var(--part-soft);padding:8px 10px;border-radius:6px;border:1px solid #86efac">
          <div style="color:var(--part);font-size:11px;font-weight:700">PRORROGAÇÃO (18h–19h)</div>
          <b style="font-size:14.5px;color:var(--part)">${fmt(sp.total.votos_pos18)} votos</b> <span style="color:var(--part)">(0,36/urna)</span>
        </div>
        <div style="background:var(--soft);padding:8px 10px;border-radius:6px">
          <div style="color:var(--muted);font-size:11px">PLACAR ABERTAS ≥18h vs DEMAIS</div>
          <b style="color:var(--lula)">L 57,4%</b> <span style="color:var(--muted)">(vs 55,4% demais)</span>
        </div>
      </div>
    </div>

    <!-- Card Salvador -->
    <div style="background:var(--paper);border:1.5px solid var(--line);border-radius:12px;padding:${isTall ? '20px 22px' : '14px 18px'};display:flex;flex-direction:column;gap:8px">
      <div style="display:flex;justify-content:space-between;align-items:baseline;border-bottom:1px solid var(--line);padding-bottom:6px">
        <div>
          <span style="font-family:var(--display);font-weight:900;font-size:${isTall ? '28px' : '24px'}">Salvador (BA)</span>
          <span style="font-family:var(--mono);font-size:13px;color:var(--muted);margin-left:8px">${fmt(ssa.total.n_secoes)} seções · ${fmt(ssa.total.comp)} votos</span>
        </div>
        <div style="font-family:var(--mono);font-size:13px;font-weight:800;color:var(--part);background:var(--part-soft);padding:3px 10px;border-radius:99px">
          755 seções abertas ≥18h (14,7%) → 240 votos pós-18h (0,016%)
        </div>
      </div>

      ${hourBars(ssa.total.votos_hora, ssaMax)}

      <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:4px;font-family:var(--mono);font-size:12.5px">
        <div style="background:var(--soft);padding:8px 10px;border-radius:6px">
          <div style="color:var(--muted);font-size:11px">HORÁRIO NORMAL (8h–16h)</div>
          <b style="font-size:14.5px">${fmt(ssaNorm)} (${pc(ssaNorm/ssa.total.comp*100, 3)}%)</b>
        </div>
        <div style="background:var(--soft);padding:8px 10px;border-radius:6px">
          <div style="color:var(--muted);font-size:11px">FILA NORMAL 17h (2ºT vs 1ºT)</div>
          <b style="font-size:14.5px">${fmt(ssa.total.votos_17h)}</b> <span style="color:var(--muted)">(1ºT: ${fmt(ssa.total.votos_1t_pos17)}!)</span>
        </div>
        <div style="background:var(--part-soft);padding:8px 10px;border-radius:6px;border:1px solid #86efac">
          <div style="color:var(--part);font-size:11px;font-weight:700">PRORROGAÇÃO (18h–19h)</div>
          <b style="font-size:14.5px;color:var(--part)">${fmt(ssa.total.votos_pos18)} votos</b> <span style="color:var(--part)">(0,32/urna)</span>
        </div>
        <div style="background:var(--soft);padding:8px 10px;border-radius:6px">
          <div style="color:var(--muted);font-size:11px">PLACAR ABERTAS ≥18h vs DEMAIS</div>
          <b style="color:var(--lula)">L 74,4%</b> <span style="color:var(--muted)">(vs 73,0% demais)</span>
        </div>
      </div>
    </div>

    <div class="verdict-banner">
      <div class="v-text">
        <b>Comparativo 1º Turno × 2º Turno:</b> No 1º turno (6 cargos na urna), <b>98.973 eleitores</b> votaram após as 17h em SP e Salvador por causa das filas. No 2º turno (1 cargo), foram apenas <b>6.260</b> (sendo 5.414 na fila normal das 17h e apenas 846 na prorrogação pós-18h) — uma queda de <b>93,7%</b>.
      </div>
    </div>
  `;
  return baseTemplate(2, 'FLUXO HORÁRIO', html, height);
}

function makeSlide3(height) {
  const isTall = height >= 1800;
  const cids = Object.values(D.cidades);

  const rowsHtml = cids.map(c => {
    const isProrrog = c.pos18.n_secoes > 0;
    const lPct = c.total.validos ? (c.total.l / c.total.validos * 100) : 0;
    const fPct = 100 - lPct;
    const compPct = c.total.aptos ? (c.total.comp / c.total.aptos * 100) : 0;
    const badge = isProrrog
      ? `<span style="background:var(--part-soft);color:var(--part);border:1px solid #86efac;padding:2px 7px;border-radius:99px;font-size:10.5px;font-weight:800">PRORROGADA</span>`
      : `<span style="background:var(--soft);color:var(--muted);padding:2px 7px;border-radius:99px;font-size:10.5px;font-weight:700">CONTROLE</span>`;

    return `<tr style="background:${isProrrog ? '#f3faf5' : 'var(--paper)'}">
      <td style="font-family:var(--display);font-weight:800;font-size:${isTall ? '15.5px' : '14px'}">
        ${c.nome} <span style="color:var(--muted);font-weight:600;font-size:12px">(${c.uf})</span>
      </td>
      <td style="text-align:center">${badge}</td>
      <td>${fmt(c.total.n_secoes)}</td>
      <td style="font-weight:800;color:${isProrrog ? 'var(--part)' : 'var(--muted)'}">${isProrrog ? fmt(c.pos18.n_secoes) : '0'}</td>
      <td style="font-weight:800;color:${isProrrog ? 'var(--part)' : 'var(--muted)'};background:${isProrrog ? '#e3f7e8' : 'transparent'}">${isProrrog ? fmt(c.total.votos_pos18) : '0'}</td>
      <td>${fmt(c.total.votos_17h)}</td>
      <td style="color:var(--muted)">${fmt(c.total.votos_1t_pos17)}</td>
      <td style="width:190px">
        <div style="display:flex;justify-content:space-between;font-size:11.5px;font-weight:700;margin-bottom:2px">
          <span style="color:var(--lula)">L ${pc(lPct,1)}%</span>
          <span style="color:var(--flavio)">F ${pc(fPct,1)}%</span>
        </div>
        <div style="display:flex;height:6px;border-radius:99px;overflow:hidden;background:var(--soft)">
          <div style="width:${lPct}%;background:var(--lula)"></div>
          <div style="width:${fPct}%;background:var(--flavio)"></div>
        </div>
      </td>
      <td>${pc(compPct, 1)}%</td>
    </tr>`;
  }).join('');

  const html = `
    <div>
      <div class="kicker">QUADRO CONSOLIDADO · 57.744 SEÇÕES AUDITADAS</div>
      <h2>As 15 Cidades Auditadas: Prorrogadas vs. Controle</h2>
      <p class="lead">
        Separamos a <b>fila normal das 17h</b> (17:00–17:59, presente em toda eleição) dos <b>votos reais após as 18h</b>. Nas 11 cidades de controle — inclusive as que citaram chuva no Sul — nenhuma seção ficou aberta até as 18h:
      </p>
    </div>

    <div style="border:1.5px solid var(--line);border-radius:10px;overflow:hidden;background:var(--paper)">
      <table class="city-tbl">
        <thead>
          <tr>
            <th>Município</th>
            <th style="text-align:center">Grupo</th>
            <th>Seções</th>
            <th style="color:#86efac">Abertas ≥18h</th>
            <th style="color:#86efac">Votos ≥18h</th>
            <th>Fila 17h (2ºT)</th>
            <th>Fila 17h (1ºT)</th>
            <th style="text-align:center">Placar 2º Turno</th>
            <th>Comp.</th>
          </tr>
        </thead>
        <tbody>
          ${rowsHtml}
        </tbody>
        <tfoot>
          <tr style="background:var(--soft);font-weight:800;font-size:${isTall ? '14px' : '13px'}">
            <td style="font-family:var(--display)">TOTAL (15 CIDADES)</td>
            <td style="text-align:center">4 / 11</td>
            <td>57.744</td>
            <td style="color:var(--part)">2.494 (4,3%)</td>
            <td style="color:var(--part);background:#dcfce7">865</td>
            <td>7.114</td>
            <td>214.795</td>
            <td style="text-align:center">L 53,6% × 46,4% F</td>
            <td>80,8%</td>
          </tr>
        </tfoot>
      </table>
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
      <div style="background:var(--paper);border:1.5px solid var(--line);border-left:6px solid var(--flavio);border-radius:8px;padding:${isTall ? '14px 16px' : '10px 14px'}">
        <div style="font-family:var(--mono);font-size:11px;font-weight:800;color:var(--flavio);text-transform:uppercase">Cidades do Sul (Chuvas) · 0 Urnas ≥18h</div>
        <p style="font-size:${isTall ? '15.5px' : '13.8px'};line-height:1.35;margin-top:3px">
          Em <b>Curitiba, Joinville, Blumenau, Paranaguá e Porto Alegre</b>, 100% das 9.443 urnas já estavam encerradas antes das 17h30. Os votos entre 17:00 e 17:19 foram fila normal de encerramento.
        </p>
      </div>
      <div style="background:var(--paper);border:1.5px solid var(--line);border-left:6px solid var(--accent);border-radius:8px;padding:${isTall ? '14px 16px' : '10px 14px'}">
        <div style="font-family:var(--mono);font-size:11px;font-weight:800;color:var(--accent);text-transform:uppercase">O Contraexemplo de Belo Horizonte</div>
        <p style="font-size:${isTall ? '15.5px' : '13.8px'};line-height:1.35;margin-top:3px">
          BH teve disputa acirradíssima vencida por Flávio (<b>50,80% × 49,20% Lula</b>) e <b>nenhuma seção aberta ≥18h</b>, registrando 327 votos na fila normal das 17h (contra 35.141 no 1º turno).
        </p>
      </div>
    </div>
  `;
  return baseTemplate(3, 'TABELA 15 CIDADES', html, height);
}

function makeSlide4(height) {
  const isTall = height >= 1800;
  const html = `
    <div>
      <div class="kicker">PROVA MATEMÁTICA, SIGILO DO RDV &amp; FONTES OFICIAIS</div>
      <h2>Por que é impossível a prorrogação ter mudado o resultado</h2>
      <p class="lead">
        Além da baixíssima procura (865 eleitores pós-18h em 57.744 seções), testamos cenários matemáticos extremos e documentamos toda a cadeia criptográfica dos arquivos do TSE:
      </p>
    </div>

    <!-- Simulação Matemática -->
    <div style="background:var(--paper);border:1.5px solid var(--line);border-top:5px solid var(--calc);border-radius:10px;padding:${isTall ? '20px 22px' : '14px 18px'}">
      <div style="font-family:var(--mono);font-size:12px;font-weight:800;color:var(--calc);text-transform:uppercase;letter-spacing:.05em;margin-bottom:8px">
        LIMITE MATEMÁTICO SUPERIOR · PROPORÇÃO DOS VOTOS PÓS-18H (O RDV NÃO TRAZ HORÁRIO POR SIGILO)
      </div>
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;font-family:var(--mono)">
        <div style="background:var(--soft);padding:12px;border-radius:8px">
          <div style="font-size:11px;color:var(--muted)">SÃO PAULO (MARGEM: 766.431)</div>
          <div style="font-family:var(--display);font-size:26px;font-weight:900;color:var(--ink);margin:2px 0">606 votos ≥18h</div>
          <div style="font-size:11.5px;color:var(--part);font-weight:700">= 0,0083% do comparecimento</div>
          <div style="font-size:11px;color:var(--muted);margin-top:2px">0,079% da margem municipal</div>
        </div>
        <div style="background:var(--soft);padding:12px;border-radius:8px">
          <div style="font-size:11px;color:var(--muted)">SALVADOR (MARGEM: 732.320)</div>
          <div style="font-family:var(--display);font-size:26px;font-weight:900;color:var(--ink);margin:2px 0">240 votos ≥18h</div>
          <div style="font-size:11.5px;color:var(--part);font-weight:700">= 0,0146% do comparecimento</div>
          <div style="font-size:11px;color:var(--muted);margin-top:2px">0,033% da margem municipal</div>
        </div>
        <div style="background:var(--soft);padding:12px;border-radius:8px">
          <div style="font-size:11px;color:var(--muted)">FEIRA + GUARULHOS</div>
          <div style="font-family:var(--display);font-size:26px;font-weight:900;color:var(--ink);margin:2px 0">19 votos ≥18h</div>
          <div style="font-size:11.5px;color:var(--part);font-weight:700">13 em Feira · 6 em Guarulhos</div>
          <div style="font-size:11px;color:var(--muted);margin-top:2px">≤ 0,004% do comparecimento</div>
        </div>
      </div>
    </div>

    <!-- Metodologia & Sigilo do Voto -->
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
      <div style="background:var(--paper);border:1.5px solid var(--line);border-radius:10px;padding:${isTall ? '18px 20px' : '13px 16px'}">
        <div style="font-family:var(--mono);font-size:11.5px;font-weight:800;color:var(--accent);text-transform:uppercase;margin-bottom:6px">
          ARQUIVOS BRUTOS AUDITADOS (ASN.1 BER)
        </div>
        <ul style="font-size:${isTall ? '15px' : '13.5px'};line-height:1.4;padding-left:18px;display:grid;gap:4px">
          <li><b><code>bu.dat</code>:</b> Votos por candidato, comparecimento e hora exata de encerramento.</li>
          <li><b><code>rdv.dat</code>:</b> Cédulas digitais embaralhadas. <b>100% das 57.744 seções batem RDV = BU.</b></li>
          <li><b><code>log.jez</code>:</b> <b>57.743/57.744 seções (99,998%)</b> batem Log = BU (apenas a seção 0395/0298 de Guarulhos, 268 votos e fechada às 17:03, veio sem <code>log.jez</code>).</li>
        </ul>
      </div>
      <div style="background:var(--paper);border:1.5px solid var(--line);border-radius:10px;padding:${isTall ? '18px 20px' : '13px 16px'}">
        <div style="font-family:var(--mono);font-size:11.5px;font-weight:800;color:var(--flavio);text-transform:uppercase;margin-bottom:6px">
          LIMITES METODOLÓGICOS &amp; SIGILO DO VOTO
        </div>
        <ul style="font-size:${isTall ? '15px' : '13.5px'};line-height:1.4;padding-left:18px;display:grid;gap:4px">
          <li><b>Sigilo no RDV:</b> Por projeto constitucional da urna, o <code>rdv.dat</code> não grava hora — não indica em quem votaram os eleitores pós-18h.</li>
          <li>Mede-se a <b>quantidade de votos por hora pelo Log</b> e o <b>placar agregado pelo BU</b> das seções.</li>
          <li>Em Feira de Santana, 1.218 seções tinham BU publicado na coleta (308 estavam como "Recebida").</li>
        </ul>
      </div>
    </div>

    <!-- Fontes Jornalísticas -->
    <div style="background:var(--paper);border:1.5px solid var(--line);border-radius:10px;padding:${isTall ? '16px 20px' : '12px 16px'}">
      <div style="font-family:var(--mono);font-size:11.5px;font-weight:800;color:var(--muted);text-transform:uppercase;margin-bottom:6px">
        FONTES JORNALÍSTICAS DOCUMENTADAS (AGÊNCIA BRASIL / EBC · 25/10/2026)
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px 16px;font-family:var(--mono);font-size:11.5px;color:var(--ink)">
        <div>• <i>"Campanha de Flávio pede votação até 19h por chuvas em alguns estados"</i></div>
        <div>• <i>"Em SP, 80% das urnas estavam encerradas quando votação foi prorrogada"</i></div>
        <div>• <i>"Lula pede prorrogação de votação em cidades com falhas no transporte"</i></div>
        <div>• <i>"Prorrogação da votação teve baixa procura e frustração de eleitores"</i></div>
      </div>
    </div>

    <!-- Call to Action GitHub -->
    <div style="background:var(--ink);color:#fbf8f1;border-radius:12px;padding:${isTall ? '22px 28px' : '16px 24px'};display:flex;align-items:center;justify-content:space-between">
      <div>
        <div style="font-family:var(--mono);font-size:12px;color:#f59e0b;font-weight:800;text-transform:uppercase;letter-spacing:.08em">
          AUDITORIA ABERTA · REPRODUZA VOCÊ MESMO
        </div>
        <div style="font-family:var(--display);font-size:${isTall ? '26px' : '22px'};font-weight:900;margin-top:2px">
          Dashboard Interativo, Scripts Python, ASN.1 e CSV das 57.744 seções
        </div>
      </div>
      <div style="background:#f59e0b;color:#161514;font-family:var(--mono);font-weight:900;font-size:17px;padding:11px 18px;border-radius:8px;white-space:nowrap">
        github.com/mmarsz
      </div>
    </div>
  `;
  return baseTemplate(4, 'IMPACTO E METODOLOGIA', html, height);
}

(async () => {
  const browser = await chromium.launch({
    executablePath: '/home/mmarsz/.cache/ms-playwright/chromium-1248/chrome-linux64/chrome',
    args: ['--no-sandbox', '--disable-gpu']
  });

  const configs = [
    { height: 1350, dir: outDir45, label: '1080x1350 (4:5 Feed)' },
    { height: 1920, dir: outDir916, label: '1080x1920 (9:16 Stories/Full)' }
  ];

  for (const cfg of configs) {
    const page = await browser.newPage({
      viewport: { width: 1080, height: cfg.height },
      deviceScaleFactor: 1
    });

    const slides = [
      { name: '01_capa_fatos.png', html: makeSlide1(cfg.height) },
      { name: '02_sp_salvador_fluxo.png', html: makeSlide2(cfg.height) },
      { name: '03_tabela_15_cidades.png', html: makeSlide3(cfg.height) },
      { name: '04_impacto_metodologia_fontes.png', html: makeSlide4(cfg.height) }
    ];

    for (const s of slides) {
      await page.setContent(s.html, { waitUntil: 'networkidle' });
      await page.evaluate(() => document.fonts.ready);
      const outPath = path.join(cfg.dir, s.name);
      await page.screenshot({ path: outPath, type: 'png' });
      console.log(`[${cfg.label}] Generated:`, outPath);
    }
    await page.close();
  }

  await browser.close();
})();
