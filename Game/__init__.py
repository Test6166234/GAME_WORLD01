# <!DOCTYPE html>
# <html lang="ru">
# <head>
# <meta charset="UTF-8">
# <meta name="viewport" content="width=device-width, initial-scale=1.0">
# <title>НЕ ТАНК 2026: TOTAL ANNIHILATION</title>
# <style>
# :root { --neon: #00f2ff; --danger: #ff004c; --gold: #ffee00; --bg: #010103; }
# body { margin:0; background: var(--bg); color:#fff; font-family:'Exo 2', sans-serif; overflow:hidden; display:flex; align-items:center; justify-content:center; min-height:100vh; }
# #game-container { position:relative; border:2px solid var(--neon); box-shadow:0 0 50px rgba(0,242,255,0.25); background: #050508; }
# canvas { display:block; }
# #ui-top { position:absolute; top:-55px; width:100%; display:flex; justify-content:space-between; color:var(--neon); font-family: monospace; font-size:1.5rem; text-shadow:0 0 10px var(--neon); }
# .overlay { display:none; position:absolute; top:0; left:0; width:100%; height:100%; background: rgba(0,0,0,0.96); flex-direction:column; justify-content:center; align-items:center; z-index:100; text-align:center; }
# #countdown-display { font-size: 9rem; color: var(--neon); text-shadow: 0 0 40px var(--neon); font-weight: bold; }
# .cyber-btn { padding:15px 35px; border:2px solid var(--neon); background:transparent; color:#fff; cursor:pointer; text-transform:uppercase; margin:10px; font-weight:bold; transition:0.3s; width:280px; letter-spacing: 2px; }
# .cyber-btn:hover { background: var(--neon); color:#000; box-shadow:0 0 25px var(--neon); }
# #super-bar-container { position:absolute; bottom:12px; left:10%; width:80%; height:16px; background:#111; border:1px solid #444; }
# #super-bar { height:100%; width:0%; background: linear-gradient(90deg, #660000, var(--danger), var(--gold)); box-shadow: 0 0 20px var(--danger); transition: 0.1s; }
# .skill-card { border:1px solid var(--gold); padding:18px; margin:10px; width:340px; cursor:pointer; background: rgba(255,238,0,0.03); transition: 0.3s; text-align: left; }
# .skill-card:hover { background: var(--gold); color:#000; transform: translateY(-5px); }
# </style>
# </head>
# <body>
#
# <div id="game-container">
#     <div id="ui-top">
#         <div>SCORE: <span id="ne_tank_score">0</span></div>
#         <div id="wave-tag">WAVE: 1</div>
#     </div>
#
#     <div id="start-timer" class="overlay" style="display: flex;"><div id="countdown-display">3</div></div>
#
#     <div id="level-up" class="overlay">
#         <h1 style="color: var(--gold); letter-spacing: 5px;">WAR-FORGE UPGRADE</h1>
#         <div id="skills-list"></div>
#         <button class="cyber-btn" onclick="location.href='/dashboard'">BACK TO MENU</button>
#     </div>
#
#     <div id="game-over" class="overlay">
#         <h1 style="color: var(--danger); font-size: 3rem;">CORE BREACHED</h1>
#         <h2 id="final-score">SCORE: 0</h2>
#         <button class="cyber-btn" onclick="location.reload()">RE-INITIALIZE</button>
#         <button class="cyber-btn" onclick="location.href='/dashboard'">BACK TO MENU</button>
#     </div>
#
#     <canvas id="neTankGame" width="400" height="600"></canvas>
#     <div id="super-bar-container"><div id="super-bar"></div></div>
# </div>
#
# <script>
# const canvas = document.getElementById('neTankGame');
# const ctx = canvas.getContext('2d');
# const GRID = 30;
#
# let ne_tank_score = 0, currentWave = 1, enemiesKilledInWave = 0, totalWaveEnemies = 4, spawnedInWave = 0;
# let gameOver = false, paused = true, superEnergy = 0, kingMode = false;
# let adminMode = false, bossCheat = false, laserMode = false, inputBuffer = "";
#
# const player = {
#     x: 6, y: 17, hp: 5, maxHp: 5,
#     triple: false, speed: 0.2, fireRate: 400, lastShot: 0,
#     bullets: [], megaShot: false, shield: 0
# };
# let enemies = [], enemyBullets = [];
#
# // --- ПОЛНАЯ ГРАФИКА ТАНКА ИЗ ОРИГИНАЛА ---
# function drawTank(x, y, color, isEnemy=false, isBoss=false, isSpecial=false) {
#     ctx.save();
#     const size = isSpecial ? GRID * 2.6 : (isBoss ? GRID * 2.2 : GRID);
#     const px = x * GRID, py = y * GRID;
#     const half = size / 2;
#     const time = Date.now() / 100;
#
#     ctx.shadowBlur = (kingMode && !isEnemy) ? 30 : 10;
#     ctx.shadowColor = (kingMode && !isEnemy) ? "#fff" : color;
#
#     // 1. Гусеницы с анимацией
#     ctx.fillStyle = "#111";
#     ctx.fillRect(px-4, py+2, 8, size-4); ctx.fillRect(px+size-4, py+2, 8, size-4);
#     ctx.strokeStyle = "rgba(255,255,255,0.2)";
#     for(let i=0; i<size; i+=5) {
#         let shift = (time % 5);
#         ctx.beginPath();
#         ctx.moveTo(px-4, py+i+shift); ctx.lineTo(px+4, py+i+shift);
#         ctx.moveTo(px+size-4, py+i+shift); ctx.lineTo(px+size+4, py+i+shift);
#         ctx.stroke();
#     }
#
#     // 2. Корпус
#     ctx.fillStyle = "#0a0a0c"; ctx.strokeStyle = (kingMode && !isEnemy) ? "#fff" : color;
#     ctx.lineWidth = 2;
#     ctx.beginPath(); ctx.roundRect(px, py, size, size, 4); ctx.fill(); ctx.stroke();
#
#     // 3. Трубы
#     ctx.fillStyle = "#222";
#     ctx.fillRect(px+2, isEnemy?py-4:py+size, 6, 6);
#     ctx.fillRect(px+size-8, isEnemy?py-4:py+size, 6, 6);
#
#     // 4. Орудие
#     ctx.fillStyle = (kingMode && !isEnemy) ? "#fff" : color;
#     const gW = size * 0.25, gL = size * 0.7;
#     if(isEnemy) {
#         ctx.fillRect(px + half - gW/2, py + size - 2, gW, gL);
#     } else {
#         ctx.fillRect(px + half - gW/2, py - gL + 2, gW, gL);
#     }
#
#     // 5. Башня и Символ
#     ctx.beginPath(); ctx.arc(px + half, py + half, half * 0.65, 0, Math.PI*2);
#     ctx.fillStyle = "#050505"; ctx.fill(); ctx.stroke();
#     ctx.fillStyle = isEnemy ? "rgba(255,0,0,0.6)" : "rgba(255,255,255,0.4)";
#     ctx.font = "bold "+(size/2.2) + "px Arial"; ctx.textAlign = "center";
#     ctx.fillText(isEnemy?"💀":"✠", px + half, py + half + (size/8));
#
#     // Щит
#     if(!isEnemy && player.shield > 0) {
#         ctx.beginPath(); ctx.arc(px+half, py+half, size*1.2, 0, Math.PI*2);
#         ctx.strokeStyle = "rgba(0, 242, 255, 0.4)"; ctx.lineWidth = 3; ctx.stroke();
#     }
#     ctx.restore();
# }
#
# function drawHP(x, y, current, max, width) {
#     const px = x * GRID, py = y * GRID - 15;
#     ctx.fillStyle = "rgba(0,0,0,0.8)"; ctx.fillRect(px, py, width, 6);
#     ctx.fillStyle = current > (max*0.3) ? "#00ff44" : "#ff0000";
#     ctx.fillRect(px, py, Math.max(0, (current/max)*width), 6);
# }
#
# function update() {
#     if(gameOver || paused) return;
#
#     // Спавн
#     if(enemies.length < 3 && spawnedInWave < totalWaveEnemies) {
#         const isB = (spawnedInWave > 0 && spawnedInWave % 5 === 0);
#         const mhp = isB ? 10 * currentWave : 1;
#         enemies.push({
#             x: Math.random() * 11, y: -3, targetY: Math.random() * 5 + 1,
#             speed: 0.04 + (currentWave * 0.006), hp: mhp, maxHp: mhp,
#             isBoss: isB, lastShot: Date.now(), state: 'moving', sideDir: 1, moveTimer: Date.now()
#         });
#         spawnedInWave++;
#     }
#
#     if(adminMode) { superEnergy = 100; kingMode = true; player.hp = player.maxHp; }
#     if(superEnergy >= 100 && !kingMode) kingMode = true;
#     if(kingMode) { superEnergy -= 0.35; if(superEnergy <= 0) kingMode = false; }
#
#     // Лазер
#     if(laserMode) {
#         const lX = player.x + (bossCheat || kingMode ? 1.2 : 0.5);
#         enemies.forEach((e, i) => {
#             if(Math.abs((e.x + (e.isBoss?1:0.5)) - lX) < 1.4) {
#                 e.hp -= 0.2;
#                 if(e.hp <= 0) { enemies.splice(i, 1); ne_tank_score += 150; enemiesKilledInWave++; }
#             }
#         });
#     }
#
#     // Обработка пуль
#     for (let bi = player.bullets.length - 1; bi >= 0; bi--) {
#         let b = player.bullets[bi]; b.y -= 0.8;
#         if (b.y < -2) { player.bullets.splice(bi, 1); continue; }
#         for (let ei = enemies.length - 1; ei >= 0; ei--) {
#             let e = enemies[ei];
#             let hit = e.isBoss ? 1.8 : 1.1;
#             let bRealX = b.x + (bossCheat || kingMode ? 1.2 : 0.45);
#             if (Math.abs(bRealX - (e.x + (e.isBoss?1:0.5))) < hit && Math.abs(b.y - e.y) < hit) {
#                 e.hp -= (kingMode || player.megaShot ? 20 : 1);
#                 if (!kingMode && !player.megaShot) { player.bullets.splice(bi, 1); }
#                 if (e.hp <= 0) {
#                     enemies.splice(ei, 1); ne_tank_score += 100; enemiesKilledInWave++;
#                     if (!kingMode) superEnergy = Math.min(100, superEnergy + 15);
#                 }
#                 break;
#             }
#         }
#     }
#
#     // Враги
#     enemies.forEach(e => {
#         if(e.state === 'moving') {
#             if(e.y < e.targetY) e.y += e.speed;
#             else { e.state = 'firing'; e.moveTimer = Date.now(); }
#         } else {
#             e.x += e.sideDir * 0.025; if(e.x < 0.2 || e.x > 11.5) e.sideDir *= -1;
#             if(Date.now() - e.lastShot > 2800 - (currentWave * 120)) {
#                 enemyBullets.push({ x: e.x + (e.isBoss?1:0.4), y: e.y + 1.2, speed: 0.18 + (currentWave*0.01) });
#                 e.lastShot = Date.now();
#             }
#         }
#         if(Math.abs(e.x - player.x) < 0.9 && Math.abs(e.y - player.y) < 0.9 && !adminMode) {
#             if(player.shield > 0) { player.shield--; enemies.splice(enemies.indexOf(e), 1); }
#             else endGame();
#         }
#     });
#
#     enemyBullets.forEach((eb, i) => {
#         eb.y += eb.speed;
#         if(Math.abs(eb.x - player.x) < 0.7 && Math.abs(eb.y - player.y) < 0.7 && !adminMode) {
#             if(player.shield > 0) { player.shield--; enemyBullets.splice(i, 1); }
#             else { player.hp--; enemyBullets.splice(i, 1); if(player.hp <= 0) endGame(); }
#         }
#     });
#
#     if(enemiesKilledInWave >= totalWaveEnemies && enemies.length === 0) {
#         currentWave++; spawnedInWave = 0; enemiesKilledInWave = 0;
#         totalWaveEnemies += 2; openUpgradeMenu();
#     }
#
#     document.getElementById('ne_tank_score').innerText = ne_tank_score;
#     document.getElementById('super-bar').style.width = superEnergy + "%";
# }
#
# function openUpgradeMenu() {
#     paused = true; document.getElementById('level-up').style.display = 'flex';
#     const container = document.getElementById('skills-list'); container.innerHTML = '';
#     const pool = [
#         {n:'TRIPLE CANNON', d:'Веерная стрельба', f:()=>player.triple=true},
#         {n:'HEAVY PLATING', d:'Макс HP +2 и ремонт', f:()=>{player.maxHp+=2; player.hp=player.maxHp}},
#         {n:'AUTO-LOADER', d:'Скорострельность ++', f:()=>player.fireRate*=0.6},
#         {n:'VORTEX AMMO', d:'Сквозные мощные снаряды', f:()=>player.megaShot=true},
#         {n:'WARP DRIVE', d:'Скорость маневров ++', f:()=>player.speed*=1.4},
#         {n:'PLASMA SHIELD', d:'2 заряда защиты', f:()=>player.shield+=2},
#         {n:'REPAIR UNIT', d:'Полный ремонт брони', f:()=>player.hp=player.maxHp},
#         {n:'NUKE STRIKE', d:'Уничтожить всех врагов', f:()=>enemies=[]}
#     ];
#     pool.sort(() => Math.random() - 0.5).slice(0, 3).forEach(s => {
#         const d = document.createElement('div'); d.className = 'skill-card';
#         d.innerHTML = `<b>${s.n}</b><br><small>${s.d}</small>`;
#         d.onclick = () => { s.f(); document.getElementById('level-up').style.display = 'none'; paused = false; };
#         container.appendChild(d);
#     });
# }
#
# function draw() {
#     ctx.clearRect(0, 0, canvas.width, canvas.height);
#
#     // Сетка
#     ctx.strokeStyle = "rgba(0, 242, 255, 0.05)";
#     for(let i=0; i<canvas.width; i+=GRID) { ctx.beginPath(); ctx.moveTo(i,0); ctx.lineTo(i,canvas.height); ctx.stroke(); }
#
#     let pX = player.x; if(bossCheat || kingMode) pX -= 0.8;
#     drawTank(pX, player.y, kingMode?"#fff":"#00f2ff", false, false, (bossCheat || kingMode));
#     drawHP(pX, player.y, player.hp, player.maxHp, (bossCheat || kingMode) ? 80 : 30);
#
#     if(laserMode) {
#         const lX = player.x * GRID + (bossCheat || kingMode ? 40 : 15);
#         ctx.fillStyle = "rgba(255, 0, 76, 0.4)"; ctx.shadowBlur = 25; ctx.shadowColor = "#ff004c";
#         ctx.fillRect(lX - 12, 0, 24, player.y * GRID);
#     }
#
#     enemies.forEach(e => {
#         drawTank(e.x, e.y, "#ff004c", true, e.isBoss);
#         drawHP(e.x, e.y, e.hp, e.maxHp, e.isBoss ? 70 : 30);
#     });
#
#     player.bullets.forEach(b => {
#         ctx.fillStyle = player.megaShot ? "#ff00ff" : "#ffee00";
#         const bX = b.x * GRID + (bossCheat || kingMode ? 38 : 14);
#         ctx.fillRect(bX, b.y * GRID, 6, 25);
#     });
#
#     enemyBullets.forEach(eb => {
#         ctx.fillStyle = "#ff004c"; ctx.fillRect(eb.x * GRID + 13, eb.y * GRID, 6, 14);
#     });
# }
#
# function endGame() {
#     gameOver = true; document.getElementById('game-over').style.display = 'flex';
#     document.getElementById('final-score').innerText = "SCORE: " + ne_tank_score;
# }
#
# const keys = {};
# window.onkeydown = e => {
#     keys[e.code] = true;
#     if("1234567".includes(e.key)) inputBuffer += e.key;
#     if(e.key === "Enter") {
#         if(inputBuffer === "1234") adminMode = !adminMode;
#         if(inputBuffer === "4321") laserMode = !laserMode;
#         inputBuffer = "";
#     }
# };
# window.onkeyup = e => keys[e.code] = false;
#
# function loop() {
#     if(!paused && !gameOver) {
#         if(keys['ArrowLeft'] && player.x > 0) player.x -= player.speed;
#         if(keys['ArrowRight'] && player.x < 12) player.x += player.speed;
#         if(keys['Space'] && Date.now() - player.lastShot > player.fireRate) {
#             player.bullets.push({x: player.x, y: player.y});
#             if(player.triple) {
#                 player.bullets.push({x: player.x - 0.7, y: player.y + 0.3});
#                 player.bullets.push({x: player.x + 0.7, y: player.y + 0.3});
#             }
#             player.lastShot = Date.now();
#         }
#     }
#     update(); draw(); requestAnimationFrame(loop);
# }
#
# let c = 3;
# let it = setInterval(() => {
#     c--; document.getElementById('countdown-display').innerText = c > 0 ? c : "PURGE!";
#     if(c < 0) { clearInterval(it); document.getElementById('start-timer').style.display = 'none'; paused = false; }
# }, 1000);
#
# loop();
# </script>
# </body>
# </html>
